"""Private source intake and strict scorer for the ForEnergo selection benchmark.

Raw customer workbooks are never packaged with this module. Intake outputs must
be written beneath the repository's ignored .tmp/ directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


REQUEST_HEADERS = ("№", "Запрос Заказчика")
APPENDIX_SHEET = "Приложение 1"
APPENDIX_HEADER_ROW = 4


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_name(value: Any) -> str:
    """Normalize typography only; preserve punctuation and product digits."""
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("ё", "е").replace("Ё", "Е")
    return re.sub(r"\s+", " ", text).strip().casefold()


def _load_requests(path: Path) -> list[dict[str, Any]]:
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        sheet = workbook.active
        header = tuple(sheet.cell(1, col).value for col in range(1, 3))
        if header != REQUEST_HEADERS:
            raise ValueError(f"Unexpected request headers in {path.name}: {header!r}")
        rows = []
        for row_number, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            if len(row) < 2 or row[0] is None or not str(row[1] or "").strip():
                continue
            if not isinstance(row[0], int):
                raise ValueError(f"Request row {row_number} has a non-integer source number")
            rows.append({"request_id": str(row[0]), "request_row": row_number,
                         "request_name": str(row[1]).strip()})
        return rows
    finally:
        workbook.close()


def _load_appendix(path: Path) -> list[dict[str, Any]]:
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        if APPENDIX_SHEET not in workbook.sheetnames:
            raise ValueError(f"Missing sheet {APPENDIX_SHEET!r} in {path.name}")
        sheet = workbook[APPENDIX_SHEET]
        header = tuple(sheet.cell(APPENDIX_HEADER_ROW, col).value for col in range(1, 5))
        if str(header[0]).strip() != "№ п/п" or "Наименование товара" not in str(header[1]):
            raise ValueError(f"Unexpected Appendix 1 header: {header!r}")
        rows = []
        for row_number, row in enumerate(sheet.iter_rows(min_row=APPENDIX_HEADER_ROW + 1,
                                                         values_only=True),
                                          APPENDIX_HEADER_ROW + 1):
            if not row or not isinstance(row[0], int):
                continue
            rows.append({"appendix_item_number": row[0], "appendix_row": row_number,
                         "appendix_name": str(row[1] or "").strip(),
                         "technical_references": str(row[2] or "").strip(),
                         "unit": str(row[3] or "").strip()})
        return rows
    finally:
        workbook.close()


def _assert_private_output(output: Path, repository_root: Path) -> None:
    root = repository_root.resolve()
    target = output.resolve()
    if root not in target.parents or ".tmp" not in target.relative_to(root).parts:
        raise ValueError("ForEnergo intake files contain customer data and must stay under repository .tmp/")


def _style_sheet(sheet, widths: list[int]) -> None:
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="264653")
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def prepare_intake(request_path: Path, appendix_path: Path, catalogue_path: Path,
                   output_path: Path, repository_root: Path) -> dict[str, Any]:
    """Create a private, line-level expert/candidate intake workbook.

    Name crosswalk is exact after Unicode/whitespace normalization. It does not
    infer product equivalence and is deliberately not a selection score.
    """
    for path in (request_path, appendix_path, catalogue_path):
        if not path.is_file():
            raise ValueError(f"Input is not a file: {path}")
    _assert_private_output(output_path, repository_root)

    requests = _load_requests(request_path)
    appendix = _load_appendix(appendix_path)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in appendix:
        if item["appendix_name"]:
            by_name[normalized_name(item["appendix_name"])].append(item)

    request_rows: list[list[Any]] = []
    matched_appendix_rows: set[int] = set()
    join_counts: Counter[str] = Counter()
    for request in requests:
        matches = by_name.get(normalized_name(request["request_name"]), [])
        status = "exact_unique" if len(matches) == 1 else "exact_ambiguous" if matches else "no_exact_name"
        join_counts[status] += 1
        match = matches[0] if len(matches) == 1 else None
        if match:
            matched_appendix_rows.add(match["appendix_row"])
        request_rows.append([
            request["request_id"], request["request_name"], request["request_row"],
            match["appendix_item_number"] if match else None,
            match["appendix_name"] if match else None,
            match["technical_references"] if match else None,
            match["unit"] if match else None,
            match["appendix_row"] if match else None,
            status, *([None] * 16),
        ])

    appendix_only = [item for item in appendix if item["appendix_row"] not in matched_appendix_rows]
    workbook = Workbook()
    positions = workbook.active
    positions.title = "Позиции"
    positions.append(["ID заявки", "Запрос заказчика", "Строка Examplepositions",
                      "№ приложения 1", "Точное имя приложения", "Технические ссылки из приложения",
                      "Ед. изм.", "Строка приложения", "Сверка исходников",
                      "Эталонный статус", "Эталонный SKU", "Допустимые SKU эталона (через ;)",
                      "Источник эталона", "Рецензент", "Решение системы", "SKU системы",
                      "Источник доказательства системы", "ID системы", "Версия системы",
                      "Модель системы", "Время системы, с", "Токены входа", "Токены выхода",
                      "Комментарий эксперта", "Комментарий системы"])
    for row in request_rows:
        positions.append(row)
    _style_sheet(positions, [13, 68, 20, 18, 68, 70, 12, 18, 22, 22, 28, 36, 42,
                             20, 22, 28, 42, 24, 20, 22, 18, 16, 16, 42, 42])
    gold_validation = DataValidation(type="list", formula1='"exact,expert_review,no_candidate,insufficient_data,pending"', allow_blank=True)
    candidate_validation = DataValidation(type="list", formula1='"select,review,abstain,no_candidate"', allow_blank=True)
    positions.add_data_validation(gold_validation)
    positions.add_data_validation(candidate_validation)
    gold_validation.add(f"J2:J{max(2, len(request_rows) + 1)}")
    candidate_validation.add(f"O2:O{max(2, len(request_rows) + 1)}")

    appendix_sheet = workbook.create_sheet("Только приложение")
    appendix_sheet.append(["№ приложения", "Наименование", "Технические ссылки",
                           "Ед. изм.", "Строка источника"])
    for item in appendix_only:
        appendix_sheet.append([item["appendix_item_number"], item["appendix_name"],
                               item["technical_references"], item["unit"], item["appendix_row"]])
    _style_sheet(appendix_sheet, [18, 72, 75, 12, 18])

    sources = workbook.create_sheet("Срез и метод")
    source_rows = [
        ["Поле", "Значение"],
        ["Статус", "Источник подготовлен; качество подбора не оценено: нет эталона выбранных изделий и результата системы."],
        ["Метод точной сверки", "NFKC + регистр + схлопывание пробелов; знаки и цифры сохранены. Нечёткое совпадение запрещено."],
        ["Позиции Examplepositions", len(requests)],
        ["Нумерованные строки Приложения 1", len(appendix)],
        ["Точное уникальное совпадение", join_counts["exact_unique"]],
        ["Точное неоднозначное совпадение", join_counts["exact_ambiguous"]],
        ["Запрос без точного имени в приложении", join_counts["no_exact_name"]],
        ["Строк приложения без точного имени в запросах", len(appendix_only)],
        ["Выход подбора", "Не предоставлен"],
        ["Эталон фактически выбранных SKU", "Не предоставлен"],
        ["Точность подбора", "НЕ СЧИТАЕТСЯ"],
        ["Файл запроса SHA-256", sha256_file(request_path)],
        ["Файл приложения SHA-256", sha256_file(appendix_path)],
        ["Срез каталога SHA-256", sha256_file(catalogue_path)],
        ["Срез каталога", catalogue_path.name],
        ["Дата подготовки UTC", datetime.now(timezone.utc).isoformat(timespec="seconds")],
    ]
    for row in source_rows:
        sources.append(row)
    sources.column_dimensions["A"].width = 46
    sources.column_dimensions["B"].width = 110
    for cell in sources[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="264653")
    for row in sources.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    sources.freeze_panes = "A2"

    readme = workbook.create_sheet("Пояснение")
    for row in [
        ["Зачем этот файл"],
        ["Подготовить независимую построчную проверку подбора номенклатуры."],
        ["Это не таблица рекомендаций и не результат оценки системы."],
        ["Не заполнять факт выбора по одному сходству названий. Нужны подтверждённый SKU и ссылка на независимое решение инженера или на фактический результат закрытого тендера."],
        ["Точное совпадение имени только связывает две входные таблицы. Оно не подтверждает техническую эквивалентность и не означает, что SKU выбран."],
        ["Поля эталона/рецензента отделены от полей вывода тестируемой системы."],
        ["Лист 'Только приложение' показывает номенклатуру, которой нет в списке Examplepositions при строгом совпадении имени."],
        ["Все исходные документы и этот рабочий файл остаются приватными в .tmp и не попадут в Git."],
    ]:
        readme.append(row)
    readme.column_dimensions["A"].width = 130
    for row in readme.iter_rows():
        row[0].alignment = Alignment(vertical="top", wrap_text=True)
    readme.freeze_panes = "A2"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    workbook.close()
    return {
        "status": "pending_oracle",
        "request_rows": len(requests),
        "appendix_rows": len(appendix),
        "join_counts": dict(join_counts),
        "appendix_only_rows": len(appendix_only),
        "selection_accuracy": None,
        "selection_accuracy_reason": "No retained system output or independently confirmed selected-SKU oracle.",
        "inputs_sha256": {p.name: sha256_file(p) for p in (request_path, appendix_path, catalogue_path)},
        "output": str(output_path.resolve()),
        "output_sha256": sha256_file(output_path),
    }


def _read_sheet_rows(workbook_path: Path, sheet_name: str) -> tuple[list[str], list[tuple[int, tuple[Any, ...]]]]:
    """Read a sheet even when the producer left its XLSX dimension at A1."""
    workbook = load_workbook(workbook_path, data_only=True, read_only=True)
    try:
        if sheet_name not in workbook.sheetnames:
            raise ValueError(f"Missing sheet {sheet_name!r} in {workbook_path.name}")
        sheet = workbook[sheet_name]
        sheet.reset_dimensions()
        iterator = sheet.iter_rows(values_only=True)
        header = next(iterator, None)
        if not header:
            raise ValueError(f"Missing header row in {workbook_path.name}:{sheet_name}")
        headers = [str(value or "").strip() for value in header]
        rows = [(row_number, tuple(row))
                for row_number, row in enumerate(iterator, 2)
                if any(value is not None for value in row)]
        return headers, rows
    finally:
        workbook.close()


def _columns(headers: list[str], required: set[str], source: str) -> dict[str, int]:
    positions = {header: index for index, header in enumerate(headers) if header}
    missing = sorted(required - set(positions))
    if missing:
        raise ValueError(f"{source} columns missing: {missing}")
    return positions


def prepare_case_intake(technical_workbook: Path, candidate_workbook: Path,
                        catalogue_workbook: Path, output_path: Path,
                        repository_root: Path) -> dict[str, Any]:
    """Build a private, row-preserving review set from a tender and saved XLSX output.

    The supplied candidate is retained as an unattributed artifact. This function
    does not infer a system/version or fill any gold labels.
    """
    for path in (technical_workbook, candidate_workbook, catalogue_workbook):
        if not path.is_file():
            raise ValueError(f"Input is not a file: {path}")
    _assert_private_output(output_path, repository_root)

    tech_headers, tech_lines = _read_sheet_rows(technical_workbook, "Заявка")
    tech_columns = _columns(tech_headers, {
        "№ позиции", "Код заявки покупателя", "Наименование товара", "ID изделия",
        "Предлагаемая модель · проект", "Ед. изм.", "Количество", "Срок поставки",
        "Филиал покупателя", "Место поставки", "Нормативные требования",
    }, f"{technical_workbook.name}:Заявка")
    summary_headers, summary_rows = _read_sheet_rows(technical_workbook, "Характеристики")
    summary_columns = _columns(summary_headers, {
        "ID изделия", "Требуемый товар", "Предлагаемое изделие · проект",
        "Параметры изделия", "Ед. изм.", "Общее количество", "Число строк поставки",
        "Изготовитель", "Что требуется уточнить / подтвердить", "Подтверждение соответствия",
    }, f"{technical_workbook.name}:Характеристики")

    requirements: dict[str, dict[str, Any]] = {}
    for offset, row in summary_rows:
        item_id = str(row[summary_columns["ID изделия"]] or "").strip()
        if not item_id:
            continue
        if item_id in requirements:
            raise ValueError(f"Duplicate ID изделия {item_id} in {technical_workbook.name}:Характеристики")
        requirements[item_id] = {
            "request_id": item_id,
            "request_name": str(row[summary_columns["Требуемый товар"]] or "").strip(),
            "tech_summary_row": offset,
            "proposed_model_in_source": str(row[summary_columns["Предлагаемое изделие · проект"]] or "").strip(),
            "parameters": str(row[summary_columns["Параметры изделия"]] or "").strip(),
            "unit": str(row[summary_columns["Ед. изм."]] or "").strip(),
            "declared_total": str(row[summary_columns["Общее количество"]] or "").strip(),
            "declared_delivery_rows": str(row[summary_columns["Число строк поставки"]] or "").strip(),
            "manufacturer": str(row[summary_columns["Изготовитель"]] or "").strip(),
            "clarification": str(row[summary_columns["Что требуется уточнить / подтвердить"]] or "").strip(),
            "conformity": str(row[summary_columns["Подтверждение соответствия"]] or "").strip(),
        }

    delivery_counts: Counter[str] = Counter()
    delivery_rows: list[tuple[int, tuple[Any, ...]]] = []
    for offset, row in tech_lines:
        item_id = str(row[tech_columns["ID изделия"]] or "").strip()
        if not item_id:
            continue
        if item_id not in requirements:
            raise ValueError(f"Delivery row {offset} references unknown ID изделия {item_id}")
        delivery_counts[item_id] += 1
        delivery_rows.append((offset, tuple(row)))

    candidate_headers, candidate_rows = _read_sheet_rows(candidate_workbook, "Сопоставление")
    candidate_columns = _columns(candidate_headers, {
        "Закупка", "Вариант из файла", "Статус соответствия", "Комментарий по соответствию",
    }, f"{candidate_workbook.name}:Сопоставление")
    candidates: dict[str, dict[str, Any]] = {}
    for offset, row in candidate_rows:
        request_text = str(row[candidate_columns["Закупка"]] or "").strip()
        match = re.match(r"^(\d+)\.\s*(.*)$", request_text, re.DOTALL)
        if not match:
            raise ValueError(f"Candidate row {offset} has no explicit numeric request ID")
        item_id, candidate_name = match.group(1), match.group(2).strip()
        if item_id in candidates:
            raise ValueError(f"Duplicate candidate ID {item_id} in {candidate_workbook.name}")
        if item_id not in requirements:
            raise ValueError(f"Candidate row {offset} references unknown request ID {item_id}")
        if normalized_name(candidate_name) != normalized_name(requirements[item_id]["request_name"]):
            raise ValueError(f"Candidate row {offset} request text does not match technical workbook ID {item_id}")
        candidates[item_id] = {
            "candidate_row": offset,
            "candidate_name": str(row[candidate_columns["Вариант из файла"]] or "").strip(),
            "candidate_status": str(row[candidate_columns["Статус соответствия"]] or "").strip(),
            "candidate_comment": str(row[candidate_columns["Комментарий по соответствию"]] or "").strip(),
        }
    if set(candidates) != set(requirements):
        raise ValueError(
            f"Candidate IDs do not cover requirements: missing={sorted(set(requirements)-set(candidates))[:8]}, "
            f"extra={sorted(set(candidates)-set(requirements))[:8]}"
        )
    candidate_field_counts = {
        "candidate_model": sum(bool(item["candidate_name"]) for item in candidates.values()),
        "candidate_status": sum(bool(item["candidate_status"]) for item in candidates.values()),
        "candidate_comment": sum(bool(item["candidate_comment"]) for item in candidates.values()),
    }
    for item_id, req in requirements.items():
        if delivery_counts[item_id] != int(req["declared_delivery_rows"] or 0):
            raise ValueError(f"Delivery row count mismatch for request ID {item_id}")

    catalogue_products_header, catalogue_products = _read_sheet_rows(catalogue_workbook, "Товары")
    catalogue_characteristics_header, catalogue_characteristics = _read_sheet_rows(catalogue_workbook, "Характеристики")
    if not catalogue_products_header or not catalogue_characteristics_header:
        raise ValueError(f"Incomplete catalogue workbook: {catalogue_workbook.name}")
    catalogue_columns = _columns(catalogue_products_header,
                                 {"ID", "Наименование", "Модель", "Источник", "Страница"},
                                 f"{catalogue_workbook.name}:Товары")
    catalogue_name_index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source_row, row in catalogue_products:
        product_id = str(row[catalogue_columns["ID"]] or "").strip()
        if not product_id:
            continue
        product_name = str(row[catalogue_columns["Наименование"]] or "").strip()
        model = str(row[catalogue_columns["Модель"]] or "").strip()
        evidence = {
            "product_id": product_id,
            "source": str(row[catalogue_columns["Источник"]] or "").strip(),
            "page": str(row[catalogue_columns["Страница"]] or "").strip(),
            "row": str(source_row),
        }
        for alias in {normalized_name(product_name), normalized_name(model)} - {""}:
            catalogue_name_index[alias].append(evidence)
    exact_catalogue_matches: dict[str, list[dict[str, str]]] = {}
    abstention_ids: set[str] = set()
    for item_id, candidate in candidates.items():
        proposed = candidate["candidate_name"]
        if not proposed or "не найден точный вариант" in normalized_name(proposed):
            exact_catalogue_matches[item_id] = []
            abstention_ids.add(item_id)
        else:
            exact_catalogue_matches[item_id] = catalogue_name_index.get(normalized_name(proposed), [])
    recommended_candidate_ids = set(candidates) - abstention_ids
    exact_match_ids = {item_id for item_id in recommended_candidate_ids
                       if exact_catalogue_matches[item_id]}

    workbook = Workbook()
    positions = workbook.active
    positions.title = "Проверка позиций"
    positions.append([
        "ID изделия", "Требуемый товар", "Требования/параметры из XLSX", "Ед. изм.",
        "Общее количество", "Строк поставки", "Строки исходной заявки",
        "Предлагаемая модель из техчасти", "Модель из файла подбора", "Статус из файла подбора",
        "Комментарий из файла подбора", "Строка файла подбора", "Точное совпадение строки с каталогом",
        "ID товара из точных совпадений", "Источники и страницы точных совпадений", "Эталонный статус",
        "Эталонный SKU", "Источник эталона", "Рецензент", "Статус атрибуции кандидата",
        "ID системы", "Версия системы", "Модель", "Время, с", "Токены входа", "Токены выхода",
        "Ошибка/замечание проверяющего",
    ])
    line_sources: dict[str, list[str]] = defaultdict(list)
    for source_row, row in delivery_rows:
        item_id = str(row[tech_columns["ID изделия"]] or "").strip()
        line_sources[item_id].append(str(source_row))
    for item_id in sorted(requirements, key=lambda value: (not value.isdigit(), int(value) if value.isdigit() else value)):
        req = requirements[item_id]
        cand = candidates[item_id]
        catalogue_matches = exact_catalogue_matches[item_id]
        if item_id in abstention_ids:
            catalogue_match_state = "система не предложила изделие"
        elif catalogue_matches:
            catalogue_match_state = "точная строка есть; это не подтверждает соответствие"
        else:
            catalogue_match_state = "точной строки нет; возможен алиас, требуется сверка"
        catalogue_product_ids = list(dict.fromkeys(match["product_id"] for match in catalogue_matches))
        catalogue_refs = list(dict.fromkeys(
            f"{match['source']} · стр. {match['page']} · строка {match['row']}"
            for match in catalogue_matches
        ))
        positions.append([
            item_id, req["request_name"], req["parameters"], req["unit"], req["declared_total"],
            delivery_counts[item_id], "; ".join(line_sources[item_id]), req["proposed_model_in_source"],
            cand["candidate_name"], cand["candidate_status"], cand["candidate_comment"],
            cand["candidate_row"], catalogue_match_state, "; ".join(catalogue_product_ids),
            "; ".join(catalogue_refs), "pending", None, None, None,
            "unknown: source workbook has no producer/version metadata", None, None, None, None, None, None, None,
        ])
    _style_sheet(positions, [12, 70, 70, 12, 18, 16, 24, 40, 52, 28, 82, 18, 48, 32, 62,
                             20, 24, 52, 20, 48, 24, 20, 22, 16, 16, 16, 48])
    positions.freeze_panes = "A2"

    deliveries = workbook.create_sheet("Строки поставки")
    deliveries.append(["Строка источника", *tech_headers])
    for source_row, row in delivery_rows:
        deliveries.append([source_row, *row])
    _style_sheet(deliveries, [18] + [36] * len(tech_headers))

    source_sheet = workbook.create_sheet("Срез и метод")
    status_counts = Counter(candidate["candidate_status"] for candidate in candidates.values())
    source_rows = [
        ["Поле", "Значение"],
        ["Статус оценки", "pending_oracle: это intake и проверка структуры, точность подбора не рассчитана"],
        ["Позиции номенклатуры", len(requirements)],
        ["Строк поставки", len(delivery_rows)],
        ["Точный crosswalk требований к файлу подбора", f"{len(candidates)}/{len(requirements)} по явному ID и точному нормализованному имени"],
        ["Структурное покрытие кандидатной книги", f"{len(candidates)}/{len(requirements)} строк; дубли ID запрещены"],
        ["Непустые значения: модель кандидата", f"{candidate_field_counts['candidate_model']}/{len(candidates)}"],
        ["Непустые значения: статус", f"{candidate_field_counts['candidate_status']}/{len(candidates)}"],
        ["Непустые значения: комментарий", f"{candidate_field_counts['candidate_comment']}/{len(candidates)}"],
        ["Candidate с предложенным изделием", len(recommended_candidate_ids)],
        ["Точное совпадение строки candidate с наименованием/моделью каталога",
         f"{len(exact_match_ids)}/{len(recommended_candidate_ids)}; только трассировка, не оценка соответствия"],
        ["Candidate без точного совпадения строки с каталогом",
         f"{len(recommended_candidate_ids - exact_match_ids)}/{len(recommended_candidate_ids)}; ручная проверка алиасов"],
        ["Без предложения изделия", len(abstention_ids)],
        ["Система/версия файла подбора", "Не установлены; версия API не считается версией генератора"],
        ["Эталон", "Не заполнен: нужен факт подбора или инженерная метка с источником"],
        ["Товары в срезе каталога", len(catalogue_products)],
        ["Характеристики в срезе каталога", len(catalogue_characteristics)],
        ["Примечание к каталогу", "Читал листы после сброса ошибочного XLSX used-range A1; фактические строки проверены"],
        ["Техчасть SHA-256", sha256_file(technical_workbook)],
        ["Файл подбора SHA-256", sha256_file(candidate_workbook)],
        ["Каталог SHA-256", sha256_file(catalogue_workbook)],
        ["Строки файла подбора по заявленному статусу", json.dumps(status_counts, ensure_ascii=False, sort_keys=True)],
        ["Дата подготовки UTC", datetime.now(timezone.utc).isoformat(timespec="seconds")],
    ]
    for row in source_rows:
        source_sheet.append(row)
    source_sheet.column_dimensions["A"].width = 48
    source_sheet.column_dimensions["B"].width = 110
    source_sheet.freeze_panes = "A2"
    notes = workbook.create_sheet("Пояснение")
    for row in [
        ["Это закрытый рабочий intake для независимой проверки подбора."],
        ["90 строк подбора точно связаны с 90 позициями техчасти по ID и имени; все 2,156 строк поставки сохранены."],
        ["Значения и статусы из файла-кандидата сохранены как есть и не считаются правильными ответами."],
        ["Точное совпадение строки с каталогом показывает только трассировку; отсутствие точной строки не доказывает, что изделия нет."],
        ["Версия генератора в исходном файле отсутствует. Поля системы и времени намеренно пусты."],
        ["Все эталонные статусы остаются pending, пока эксперт не подтвердит SKU и источник."],
        ["Не смешивать неполную атрибуцию и неподтверждённые строки с метрикой точности."],
        ["Исходники и эта книга хранятся только в игнорируемом .tmp/ benchmark-репозитория."],
    ]:
        notes.append(row)
    notes.column_dimensions["A"].width = 130
    for row in notes.iter_rows():
        row[0].alignment = Alignment(vertical="top", wrap_text=True)
    notes.freeze_panes = "A2"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    workbook.close()
    return {
        "status": "pending_oracle",
        "selection_accuracy": None,
        "request_rows": len(requirements),
        "delivery_rows": len(delivery_rows),
        "candidate_crosswalk_rows": len(candidates),
        "candidate_field_counts": candidate_field_counts,
        "candidate_structural_coverage": len(candidates) / len(requirements) if requirements else None,
        "candidate_recommendations": len(recommended_candidate_ids),
        "candidate_exact_catalogue_text_matches": len(exact_match_ids),
        "candidate_without_exact_catalogue_text_match": len(recommended_candidate_ids - exact_match_ids),
        "candidate_abstentions": len(abstention_ids),
        "catalogue_products": len(catalogue_products),
        "catalogue_characteristics": len(catalogue_characteristics),
        "candidate_status_counts": dict(status_counts),
        "candidate_provenance": "unknown",
        "inputs_sha256": {p.name: sha256_file(p) for p in (technical_workbook, candidate_workbook, catalogue_workbook)},
        "output": str(output_path.resolve()),
        "output_sha256": sha256_file(output_path),
    }


ALLOWED_GOLD = {"exact", "expert_review", "no_candidate", "insufficient_data"}
ALLOWED_DECISIONS = {"select", "review", "abstain", "no_candidate"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: each JSONL record must be an object")
        records.append(value)
    return records


def _split_cell(value: Any) -> list[str]:
    return [part.strip() for part in re.split(r"[;\n]+", str(value or "")) if part.strip()]


def _read_workbook_records(path: Path, kind: str) -> list[dict[str, Any]]:
    """Read either side of the benchmark from the same review workbook."""
    workbook = load_workbook(path, data_only=True, read_only=True)
    try:
        if "Позиции" not in workbook.sheetnames:
            raise ValueError(f"Missing sheet 'Позиции' in {path.name}")
        sheet = workbook["Позиции"]
        headers = [str(value or "").strip() for value in next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))]
        columns = {header: index for index, header in enumerate(headers) if header}
        required = ({"ID заявки", "Эталонный статус", "Эталонный SKU",
                     "Допустимые SKU эталона (через ;)", "Источник эталона"}
                    if kind == "gold" else
                    {"ID заявки", "Решение системы", "SKU системы", "Источник доказательства системы",
                     "ID системы", "Версия системы", "Модель системы", "Время системы, с",
                     "Токены входа", "Токены выхода"})
        missing = sorted(required - set(columns))
        if missing:
            raise ValueError(f"Workbook {kind} columns missing: {missing}")

        records = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            request_id = str(row[columns["ID заявки"]] or "").strip()
            if not request_id:
                continue
            if kind == "gold":
                status = str(row[columns["Эталонный статус"]] or "pending").strip()
                product_ids = _split_cell(row[columns["Допустимые SKU эталона (через ;)"]])
                single = str(row[columns["Эталонный SKU"]] or "").strip()
                if single:
                    product_ids.append(single)
                records.append({"request_id": request_id, "gold_status": status,
                                "product_ids": list(dict.fromkeys(product_ids)),
                                "evidence_refs": _split_cell(row[columns["Источник эталона"]])})
            else:
                decision = str(row[columns["Решение системы"]] or "").strip()
                product_id = str(row[columns["SKU системы"]] or "").strip()
                system_id = str(row[columns["ID системы"]] or "").strip()
                version = str(row[columns["Версия системы"]] or "").strip()
                if not any((decision, product_id, system_id, version)):
                    continue
                elapsed = row[columns["Время системы, с"]]
                in_tokens = row[columns["Токены входа"]]
                out_tokens = row[columns["Токены выхода"]]
                records.append({"request_id": request_id, "decision": decision, "product_id": product_id or None,
                                "system_id": system_id, "system_version": version,
                                "model": str(row[columns["Модель системы"]] or "").strip() or None,
                                "elapsed_seconds": elapsed, "input_tokens": in_tokens, "output_tokens": out_tokens,
                                "evidence_refs": _split_cell(row[columns["Источник доказательства системы"]])})
        return records
    finally:
        workbook.close()


def _read_records(path: Path, kind: str) -> list[dict[str, Any]]:
    return _read_workbook_records(path, kind) if path.suffix.lower() in {".xlsx", ".xlsm"} else _read_jsonl(path)


def score_selection(gold_path: Path, candidate_path: Path) -> dict[str, Any]:
    """Grade only engineer-labelled rows; unknown gold remains outside metrics."""
    gold_records = _read_records(gold_path, "gold")
    candidate_records = _read_records(candidate_path, "candidate")
    if not gold_records:
        raise ValueError("Gold oracle is empty; selection accuracy cannot be computed")
    gold_by_id = {str(row.get("request_id")): row for row in gold_records}
    if len(gold_by_id) != len(gold_records) or "None" in gold_by_id:
        raise ValueError("Gold request_id values must be present and unique")
    candidate_by_id = {str(row.get("request_id")): row for row in candidate_records}
    if len(candidate_by_id) != len(candidate_records) or "None" in candidate_by_id:
        raise ValueError("Candidate request_id values must be present and unique")
    unknown_candidates = sorted(set(candidate_by_id) - set(gold_by_id))
    if unknown_candidates:
        raise ValueError(f"Candidate output has request IDs absent from gold: {unknown_candidates[:5]}")

    counts: Counter[str] = Counter()
    scored = 0
    system_versions: set[str] = set()
    system_ids: set[str] = set()
    models: set[str] = set()
    elapsed: list[float] = []
    input_tokens: list[int] = []
    output_tokens: list[int] = []
    for request_id, gold in gold_by_id.items():
        gold_status = gold.get("gold_status")
        if gold_status not in ALLOWED_GOLD:
            if gold_status in (None, "pending", "unknown"):
                counts["unscored_pending_gold"] += 1
                continue
            raise ValueError(f"Unsupported gold_status for {request_id}: {gold_status!r}")
        if not gold.get("evidence_refs"):
            raise ValueError(f"Gold row {request_id} requires source evidence_refs")
        scored += 1
        candidate = candidate_by_id.get(request_id)
        if candidate is None:
            decision, product_id = "abstain", None
        else:
            decision, product_id = candidate.get("decision"), candidate.get("product_id")
            if decision not in ALLOWED_DECISIONS:
                raise ValueError(f"Unsupported candidate decision for {request_id}: {decision!r}")
            version = str(candidate.get("system_version") or "").strip()
            if not version:
                raise ValueError(f"Candidate row {request_id} requires system_version")
            system_id = str(candidate.get("system_id") or "").strip()
            if not system_id:
                raise ValueError(f"Candidate row {request_id} requires system_id")
            system_versions.add(version)
            system_ids.add(system_id)
            if candidate.get("model"):
                models.add(str(candidate["model"]))
            for value, bucket, cast in ((candidate.get("elapsed_seconds"), elapsed, float),
                                        (candidate.get("input_tokens"), input_tokens, int),
                                        (candidate.get("output_tokens"), output_tokens, int)):
                if value not in (None, ""):
                    try:
                        bucket.append(cast(value))
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid runtime/token value for {request_id}: {value!r}")
            if len(system_versions) > 1 or len(system_ids) > 1:
                raise ValueError("One scoring run must contain exactly one system_id and system_version")
            if decision == "select" and (not product_id or not candidate.get("evidence_refs")):
                raise ValueError(f"Selected row {request_id} requires product_id and evidence_refs")
        if gold_status == "exact":
            expected = {str(value) for value in (gold.get("product_ids") or []) if value}
            if gold.get("product_id"):
                expected.add(str(gold["product_id"]))
            if not expected:
                raise ValueError(f"Exact gold row {request_id} requires product_id or product_ids")
            if decision == "select" and str(product_id) in expected:
                counts["correct_exact_selection"] += 1
            elif decision == "select":
                counts["false_positive_selection"] += 1
                counts["missed_exact_selection"] += 1
            else:
                counts["missed_exact_selection"] += 1
                counts["abstained_on_exact"] += 1
        elif gold_status == "expert_review":
            if decision == "review":
                counts["correct_expert_review"] += 1
            elif decision == "select":
                counts["unsafe_auto_selection"] += 1
                counts["false_positive_selection"] += 1
            else:
                counts["abstained_on_review_case"] += 1
        else:
            if decision == "select":
                counts["false_positive_selection"] += 1
            elif decision == "review":
                counts["unnecessary_review"] += 1
            else:
                counts["correct_safe_abstention"] += 1

    selected = sum(1 for request_id in gold_by_id
                   if gold_by_id[request_id].get("gold_status") in ALLOWED_GOLD
                   and candidate_by_id.get(request_id, {}).get("decision") == "select")
    true_exact = counts["correct_exact_selection"]
    exact_gold = sum(1 for row in gold_records if row.get("gold_status") == "exact")
    metrics = {
        "scored_rows": scored,
        "pending_gold_rows": counts["unscored_pending_gold"],
        "selected_rows": selected,
        "selection_coverage": selected / scored if scored else None,
        "correct_exact_selections": true_exact,
        "false_positive_selections": counts["false_positive_selection"],
        "selection_precision": true_exact / selected if selected else None,
        "exact_match_recall": true_exact / exact_gold if exact_gold else None,
        "exact_gold_rows": exact_gold,
        "safe_abstentions": counts["correct_safe_abstention"],
        "unsafe_auto_selections": counts["unsafe_auto_selection"],
        "counts": dict(counts),
        "system_ids": sorted(system_ids),
        "system_versions": sorted(system_versions),
        "models": sorted(models),
        "elapsed_seconds_total": sum(elapsed) if elapsed else None,
        "timed_rows": len(elapsed),
        "input_tokens_total": sum(input_tokens) if input_tokens else None,
        "output_tokens_total": sum(output_tokens) if output_tokens else None,
        "gold_sha256": sha256_file(gold_path),
        "candidate_sha256": sha256_file(candidate_path),
    }
    return metrics


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ForEnergo tender selection benchmark intake and grader")
    subs = parser.add_subparsers(dest="command", required=True)
    prep = subs.add_parser("prepare", help="Create a private input crosswalk/review workbook")
    prep.add_argument("--requests", required=True, type=Path)
    prep.add_argument("--appendix", required=True, type=Path)
    prep.add_argument("--catalogue", required=True, type=Path)
    prep.add_argument("--output", required=True, type=Path)
    prep.add_argument("--repository-root", type=Path, default=Path.cwd())
    case = subs.add_parser("prepare-case", help="Prepare a private intake from a tender and saved XLSX output")
    case.add_argument("--technical-workbook", required=True, type=Path)
    case.add_argument("--candidate-workbook", required=True, type=Path)
    case.add_argument("--catalogue", required=True, type=Path)
    case.add_argument("--output", required=True, type=Path)
    case.add_argument("--repository-root", type=Path, default=Path.cwd())
    score = subs.add_parser("score", help="Score versioned selection JSONL against engineer-labelled JSONL")
    score.add_argument("--gold", required=True, type=Path)
    score.add_argument("--candidate", required=True, type=Path)
    score.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare_intake(args.requests, args.appendix, args.catalogue,
                                    args.output, args.repository_root)
        elif args.command == "prepare-case":
            result = prepare_case_intake(args.technical_workbook, args.candidate_workbook,
                                         args.catalogue, args.output, args.repository_root)
        else:
            result = score_selection(args.gold, args.candidate)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

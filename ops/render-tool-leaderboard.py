#!/usr/bin/env python3
"""Regrade saved tool outputs on the same 15 cases; no parser/model execution.

Execute with the isolated released catalog-extraction-benchmark0.3.0 environment.
Matching-only grader0.3.2 is source-pinned separately. Original score files and
candidate bytes are never overwritten. Our agent orchestrator is not ranked.
"""
import hashlib
import importlib.metadata
import importlib.util
import json
import statistics
import sys
from pathlib import Path

from catalog_bench.benchmark import grader_digest, score_file
from catalog_bench.dataset import validate_dataset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples/tool-leaderboard/common-15-v032"
BASELINE = "24b64859fd690d11afd8477c69a0f84336a28338ac0b49981e5300055364d57a"
PRIMARY = "f091872c67af7e410490df6b590cb8ac03a05eb6e615351ed281c4ae1687e21d"
MODULE = "e268c25f302e051d6b34295298eac6603dba8ff9f108003bb9bd3f3a2685972d"
BASE = "https://github.com/megamen32/catalog-extraction-benchmark/blob/main/"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if path.name.startswith("score-") and path.exists():
        assert path.read_text() == body, "Same-version saved grade drift; retain evidence and investigate"
        return
    path.write_text(body)


def check_privacy(data):
    text = json.dumps(data, ensure_ascii=False).lower()
    for marker in ["/home/", "/users/", "bearer "]:
        assert marker not in text, "Private marker in public artifact"


def main():
    assert importlib.metadata.version("catalog-extraction-benchmark") == "0.3.0"
    assert grader_digest() == BASELINE, "Released baseline algorithm drift"
    module_path = ROOT / "src/catalog_bench/language_corrected_grader.py"
    assert digest(module_path) == MODULE, "Primary grader file drift"
    spec = importlib.util.spec_from_file_location("pinned_language_grader", module_path)
    primary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(primary)
    assert primary.language_grader_digest() == PRIMARY
    validate_dataset("engineering-catalogs-v1")
    validate_dataset("engineering-catalogs-v2")

    v1 = read("src/catalog_bench/data/engineering-catalogs-v1/dataset.json")
    v2 = read("src/catalog_bench/data/engineering-catalogs-v2/dataset.json")
    fixtures = {c["id"]: c for c in v1["cases"]}
    expanded = {c["id"]: c for c in v2["cases"]}
    assert len(fixtures) == 15
    assert sum(c["coverage"]["engineering_facts"] for c in fixtures.values()) == 500
    fixture_paths = {}
    fixture_sha = {}
    for identifier, case in fixtures.items():
        a = ROOT / "src/catalog_bench/data/engineering-catalogs-v1" / case["fixture"]
        b = ROOT / "src/catalog_bench/data/engineering-catalogs-v2" / expanded[identifier]["fixture"]
        assert a.read_bytes() == b.read_bytes(), "Shared source annotation changed"
        fixture_paths[identifier], fixture_sha[identifier] = a, digest(a)

    source_manifests = {}
    before_candidates = {}
    rows = []

    def register_source(relative):
        source_manifests[relative] = digest(ROOT / relative)

    def assess(identifier, label, rounds, model, versions, source, aggregate_timing=None):
        reports = []
        for number, records in enumerate(rounds, 1):
            assert set(records) == set(fixtures), f"Missing/extra common case: {identifier}"
            cases, totals, valid = [], {"0.3.0": 0, "0.3.2": 0}, 0
            elapsed = []
            for case_id, source_case in records.items():
                fixture = fixtures[case_id]
                expected = fixture["coverage"]["engineering_facts"]
                candidate = source_case.get("candidate")
                entry = {"case_id": case_id, "expected": expected, "status": source_case["status"],
                         "source_sha256": fixture["source_sha256"], "fixture_sha256": fixture_sha[case_id],
                         "elapsed_seconds": source_case["elapsed_seconds"], "correct": {"0.3.0": 0, "0.3.2": 0}}
                assert source_case["source_sha256"] == fixture["source_sha256"]
                assert source_case["physical_page"] == fixture["physical_page"]
                if source_case.get("fixture_sha256"):
                    assert source_case["fixture_sha256"] == fixture_sha[case_id]
                if candidate and source_case["valid"]:
                    path = ROOT / candidate
                    assert digest(path) == source_case["candidate_sha256"]
                    before_candidates[candidate] = digest(path)
                    scores = {"0.3.0": score_file(fixture_paths[case_id], path),
                              "0.3.2": primary.score_language_corrected(fixture_paths[case_id], path)}
                    valid += 1
                    entry.update(candidate=candidate, candidate_sha256=digest(path), score_files={})
                    for version, score in scores.items():
                        assert score["engineering_facts"]["expected"] == expected
                        assert score["drawing_assertions"]["expected"] == 0
                        if source_case.get("retained_correct"):
                            assert score["engineering_facts"]["correct"] == source_case["retained_correct"][version]
                        check_privacy(score)
                        target = OUT / identifier / f"round-{number}" / case_id / f"score-v{version}.json"
                        write(target, score)
                        entry["correct"][version] = score["engineering_facts"]["correct"]
                        entry["score_files"][version] = str(target.relative_to(ROOT))
                        totals[version] += entry["correct"][version]
                elif candidate:
                    # Invalid output is retained as evidence, never repaired for this ranking.
                    path = ROOT / candidate
                    assert digest(path) == source_case["candidate_sha256"]
                    before_candidates[candidate] = digest(path)
                    entry.update(candidate=candidate, candidate_sha256=digest(path))
                if source_case["elapsed_seconds"] is not None:
                    elapsed.append(source_case["elapsed_seconds"])
                cases.append(entry)
            reports.append({"round": number, "expected": 500, "correct": totals,
                            "valid_pages": valid, "expected_pages": 15,
                            "elapsed_seconds_sum_known": sum(elapsed), "cases_with_known_time": len(elapsed),
                            "elapsed_seconds_sum": sum(elapsed) if len(elapsed) == 15 else None, "cases": cases})
            if len(elapsed) != 15 and aggregate_timing is not None:
                reports[-1]["elapsed_seconds_sum"] = aggregate_timing["elapsed_seconds"]
                reports[-1]["time_from_retained_aggregate"] = True
                reports[-1]["elapsed_definition"] = aggregate_timing.get(
                    "elapsed_seconds_definition", "retained aggregate of per-case durations; individual breakdown incomplete")
        percentages = [100 * r["correct"]["0.3.2"] / 500 for r in reports]
        baseline_percentages = [100 * r["correct"]["0.3.0"] / 500 for r in reports]
        rows.append({"id": identifier, "label": label, "model_or_mode": model,
                     "versions": versions, "source_receipt": source, "rounds": reports,
                     "mean_percent": statistics.mean(percentages),
                     "baseline_mean_percent": statistics.mean(baseline_percentages),
                     "sample_sd_pp": statistics.stdev(percentages) if len(percentages) > 1 else None,
                     "minimum_percent": min(percentages), "maximum_percent": max(percentages),
                     "rounds_count": len(reports), "statistical_winner_established": False})

    parsers = "examples/parser-outputs/2026-10-12/manifest.json"
    parser_data = read(parsers)
    register_source(parsers)
    for configuration in parser_data["configurations"]:
        records = {}
        for case in configuration["cases"]:
            output = case.get("output")
            records[case["case_id"]] = {
                "candidate": str(Path(parsers).parent / output["file"]) if output else None,
                "candidate_sha256": output["sha256"] if output else None,
                "valid": output is not None and case["status"] == "completed", "status": case["status"],
                "source_sha256": case["source"]["sha256"], "physical_page": case["source"]["physical_page"],
                "fixture_sha256": case["fixture_sha256"],
                "elapsed_seconds": case["timing"].get("elapsed_seconds")}
        assess(configuration["engine"], configuration["engine"], [records],
               "сохранённый режим парсера", configuration["versions"], parsers,
               aggregate_timing=configuration["historical_metrics"])

    direct = "examples/project-x/2026-10-12/manifest.json"
    direct_data = read(direct)
    register_source(direct)
    direct_rounds = []
    for round_data in direct_data["rounds"]:
        direct_rounds.append({case["case_id"]: {
            "candidate": str(Path(direct).parent / case["normalized"]),
            "candidate_sha256": case["normalized_sha256"], "valid": True, "status": "completed",
            "source_sha256": fixtures[case["case_id"]]["source_sha256"],
            "physical_page": fixtures[case["case_id"]]["physical_page"],
            "elapsed_seconds": case["elapsed_seconds"]}
            for case in round_data["entries"] if case["case_id"] in fixtures})
    assess("project-x-direct", "Project X", direct_rounds, "PDF / без Vision",
           {"snapshot": direct_data["snapshot"]}, direct)

    vision = "examples/project-x/2026-10-12-native-vision-v1-full/manifest.json"
    vision_data = read(vision)
    register_source(vision)
    for model in vision_data["models"]:
        model_rounds = []
        for number in (1, 2, 3):
            receipt = str(Path(vision).parent / model / f"round-{number}" / "results.json")
            data = read(receipt)
            register_source(receipt)
            model_rounds.append({case["case_id"]: {
                "candidate": str(Path(vision).parent / case["candidate"]) if case.get("candidate") else None,
                "candidate_sha256": case.get("candidate_sha256"),
                "valid": case["status"] == "completed", "status": case["status"],
                "source_sha256": case["source_sha256"], "physical_page": case["page"],
                "elapsed_seconds": case["elapsed_seconds"],
                "retained_correct": {version: score["engineering"] for version, score in case["selected_correct"].items()}}
                for case in data["cases"] if case["case_id"] in fixtures})
        assess("project-x-" + model, "Project X", model_rounds, "Vision / " + model,
               {"snapshot": vision_data["snapshot"], "integration": vision_data["integration"],
                "integration_sha256": vision_data["integration_sha256"]}, vision)

    for path, fingerprint in before_candidates.items():
        assert digest(ROOT / path) == fingerprint, "Candidate mutated during regrade"
    for path, fingerprint in source_manifests.items():
        assert digest(ROOT / path) == fingerprint, "Receipt mutated during regrade"
    rows.sort(key=lambda r: (-r["mean_percent"], r["id"]))
    last_score, rank = None, 0
    for ordinal, row in enumerate(rows, 1):
        if row["mean_percent"] != last_score:
            rank = ordinal
            last_score = row["mean_percent"]
        row["rank"] = rank
    manifest = {"schema_version": "1.0", "primary_grader": "0.3.2", "primary_grader_sha256": PRIMARY,
                "retained_baseline_grader": "0.3.0", "baseline_grader_sha256": BASELINE,
                "dataset": "common15 unchanged cases shared by engineering-catalogs-v1 and v2",
                "pages_per_round": 15, "engineering_facts_per_round": 500, "drawing_checks": 0,
                "primary_expanded_benchmark_replaced": False, "expanded_pages27_39_not_ranked_here": True,
                "model_calls": 0, "parser_calls": 0, "candidate_bytes_modified": False,
                "annotation_bytes_modified": False, "whole_page_accuracy": False,
                "statistical_winner_established": False, "our_orchestrator_included": False,
                "source_receipts": source_manifests, "fixture_sha256": fixture_sha,
                "observed_grading_runtime": {"python": sys.version,
                    **{name: importlib.metadata.version(name) for name in
                       ["catalog-extraction-benchmark", "pydantic", "pymupdf"]}},
                "candidate_files_verified": len(before_candidates), "rows": rows}
    check_privacy(manifest)
    write(OUT / "manifest.json", manifest)
    render(manifest)
    print(json.dumps({"configurations": len(rows), "retained_candidates_verified": len(before_candidates),
                      "project_x_positions": [{"mode": r["model_or_mode"], "rank": r["rank"],
                                               "percent": r["mean_percent"]} for r in rows if r["label"] == "Project X"],
                      "model_calls": 0, "parser_calls": 0}))


def render(manifest):
    product_directory = read("docs/tool-products.json")
    agent_included = manifest.get("our_orchestrator_included", False)
    lines = ["# Общий рейтинг инструментов — Project X включён", "",
        "**Одинаковые 15 страниц, 500 инженерных фактов, один оценщик 0.3.2 для всех.** Это общая часть сохранённых испытаний. Project X участвует как инструмент: без Vision, с GLM и с MiniMax. Наш агент, вызывающий инструменты, в этот рейтинг не включён.", "",
        "Новых вызовов парсеров или моделей не было: переоценены сохранённые JSON. Рейтинг — по наблюдаемому среднему проценту инженерных фактов. У Project X три раунда каждой конфигурации; у остальных инструментов пока по одному. Поэтому место в таблице не доказывает статистически устойчивого превосходства.", "",
        "[Скачать и установить инструменты](PRODUCTS-RU.md). Название инструмента ведёт на продукт; последний столбец — на манифест результатов.", "",
        "| Место | Инструмент / конфигурация | Режим / модель | Раундов | Раунд 1 | Раунд 2 | Раунд 3 | Среднее по 0.3.2 | SD, п.п. | Валидных страниц | Время раундов, с | Манифест |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in manifest["rows"]:
        product = product_directory["products"][product_directory["configurations"][row["id"]]]
        scores = [f"{r['correct']['0.3.2']}/500" for r in row["rounds"]]
        scores += ["не проводился"] * (3 - len(scores))
        sd = f"{row['sample_sd_pp']:.2f}" if row["sample_sd_pp"] is not None else "не измерен"
        pages = "; ".join(f"{r['valid_pages']}/15" for r in row["rounds"])
        times = "; ".join(f"{r['elapsed_seconds_sum']:.1f}" if r["elapsed_seconds_sum"] is not None else "не полностью измерено" for r in row["rounds"])
        lines.append("| " + " | ".join([str(row["rank"]), f"[{row['label']}]({product['url']})",
            row["model_or_mode"], str(row["rounds_count"]), *scores, f"{row['mean_percent']:.2f}%", sd, pages, times,
            f"[Результаты]({BASE}{row['source_receipt']})"]) + " |")
    lines += ["", "## Что именно сравнивается", "",
        "- У всех строк одинаковые страницы, исходные PDF и неизменённые эталоны. 15 страниц буквально входят в текущий набор v2. Здесь исключены новые страницы 27 и 39, для которых у большинства старых парсеров нет сохранённого ответа.",
        "- Полный основной бенчмарк остаётся на 17 страницах / 520 фактах +21 проверке чертежей. Эта таблица даёт сопоставимый общий рейтинг старых результатов и не заменяет расширенный бенчмарк.",
        "- Варианты MinerU standard/advanced, backend и устройства сохраняют исходную конфигурацию. Project X без Vision и с двумя Vision-моделями тоже отдельные конфигурации одного инструмента. Здесь не утверждается, что всем парсерам можно подключить одинаковые внешние модели.",
        "- Project X с Vision — протестированная адаптация native Vision v1 с рендером PDF и каталоговым JSON; это не измерение всех функций исходного банковского приложения. Исходный код и настоящее название не публикуются.",
        "- Неудачная или невалидная попытка остаётся нулём в знаменателе 500. Отсутствующий второй/третий раунд обозначен явно. Оценка выбранных фактов не означает полной точности страницы или всех каталогов.",
        "- Время — сумма длительностей попыток для этих 15 страниц, включая сохранённые неудачи. Где поштучная разбивка неполна, сохранена исходная измеренная сумма и это явно отмечено в манифесте. Версии, режимы и условия также сохранены; кеши и нагрузка не контролировались как отдельный эксперимент скорости.", "",
        "## Старый и новый оценщики живут параллельно", "",
        "Один сохранённый JSON получает отдельные файлы оценок 0.3.0 и 0.3.2. Исходные оценки 0.2.0/0.2.2 у парсеров и 0.3.0/0.3.1/0.3.2 у Project X также остаются на месте. Никакая переоценка не является новым модельным прогоном.", "",
        "| Инструмент / конфигурация | Режим / модель | Среднее 0.3.0 | Среднее 0.3.2 |",
        "|---|---|---|---|"]
    for row in manifest["rows"]:
        lines.append(f"| {row['label']} | {row['model_or_mode']} | {row['baseline_mean_percent']:.2f}% | {row['mean_percent']:.2f}% |")
    lines += ["", "[Полные новые оценки, точные версии, контрольные суммы и выходные JSON](../examples/tool-leaderboard/common-15-v032/manifest.json) · [История всех испытаний и основной расширенный набор](EXPERIMENT-HISTORY-RU.md) · [Слабые места Project X с примерами](PROJECT-X-SHORT-REVIEW-RU.md)", "",
        "Для повторного пересчёта используйте отдельное окружение с опубликованным wheel 0.3.0 и этот checkout:", "",
        "```bash", "uv venv .tmp/regrade-v030",
        "uv pip install --python .tmp/regrade-v030/bin/python https://github.com/megamen32/catalog-extraction-benchmark/releases/download/v0.3.0/catalog_extraction_benchmark-0.3.0-py3-none-any.whl",
        ".tmp/regrade-v030/bin/python -I ops/render-tool-leaderboard.py", "```", "",
        "Скрипт проверяет отпечатки обоих алгоритмов и неизменность кандидатов. Он не запускает парсеры, не вызывает модели и не меняет исходные файлы оценки.", ""]
    document = "\n".join(lines).replace("Project X", "Catalog Vision Backend")
    if agent_included:
        document = document.replace(".tmp/regrade-v030/bin/python -I ops/render-tool-leaderboard.py",
                                    ".tmp/regrade-v030/bin/python -I ops/add-catalog-agent-leaderboard.py")
        document = document.replace("# Общий рейтинг инструментов — Catalog Vision Backend включён",
                                    "# Общий рейтинг парсеров и агентов")
        document = document.replace("Наш агент, вызывающий инструменты, в этот рейтинг не включён.",
            "catalog-to-json включён отдельными версиями и моделями; агент и отдельные парсеры сравниваются как полные измеренные конфигурации.")
        document = document.replace("У Catalog Vision Backend три раунда каждой конфигурации; у остальных инструментов пока по одному.",
            "У Catalog Vision Backend по три раунда; у catalog-to-json по два или три в зависимости от версии; у остальных инструментов пока по одному.")
        document += ("\n## catalog-to-json: версии и стадия\n\n"
            "Все добавленные строки — первичное извлечение, без результата проверяющего. У версий 1.4.2, 1.4.4 и 1.4.6 по три сохранённых раунда; у 1.4.15 только два, поэтому серия явно неполная. Неудачные первые ответы дают ноль, поздние исправления их не заменяют.\n\n"
            "Время 1.4.15 — сумма известных длительностей нативных вызовов извлекателя; неполная длительность не заполнена нулём. У остальных строк сохранено собственное определение времени. Эти суммы не доказывают преимущество по скорости.\n\n"
            "Это оценки конкретных старых профилей. Они не являются измеренной точностью нынешнего выпуска 1.5.26 или принятых итоговых каталогов; проверяющий 1.4.17 не участвовал в этих первых ответах.\n\n"
            "[Новый снимок с агентом](../examples/tool-leaderboard/common-15-with-agent-v032/manifest.json) · "
            "[Прежний снимок без агента](../examples/tool-leaderboard/common-15-v032/manifest.json). "
            "Оба сохраняются отдельно; новых вызовов моделей или парсеров не было.\n")
    document = document.replace("Исходный код и настоящее название не публикуются.",
                                "Исходный код остаётся в приватном репозитории.")
    heading, body = document.split("\n", 1)
    notice = ("> [Catalog Vision Backend](CATALOG-VISION-BACKEND.md) — наша закрытая адаптация; "
              "репозиторий приватный, доступ по запросу владельцу; планируем предоставлять бесплатно. Оценки ниже относятся к сохранённым "
              "конфигурациям испытаний, а не к новому запуску переименованного форка.")
    document = heading + "\n\n" + notice + "\n\n" + body.lstrip("\n")
    (ROOT / "docs/TOOL-LEADERBOARD-RU.md").write_text(document, encoding="utf-8")


if __name__ == "__main__":
    main()

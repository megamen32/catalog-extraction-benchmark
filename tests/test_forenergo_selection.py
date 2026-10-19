import json
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

from catalog_bench import forenergo_selection as selection


def write_inputs(root: Path):
    requests = root / "requests.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["№", "Запрос Заказчика"])
    ws.append([1, "ОЗП-150 (25-150/25-150)"])
    ws.append([2, "ССТ-50 (25-50)"])
    wb.save(requests)

    appendix = root / "appendix.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Приложение 1"
    ws.append([None])
    ws.append([None])
    ws.append(["Приложение № 1"])
    ws.append(["№ п/п", "Наименование товара", "Технические характеристики", "Ед. изм."])
    ws.append([1, "ОЗП-150 (25-150/25-150)", "СТО-TEST-1", "шт"])
    ws.append([2, "ССТ-50 (35-50)", "СТО-TEST-2", "шт"])
    wb.save(appendix)

    catalogue = root / "catalogue.xlsx"
    wb = Workbook()
    wb.active.append(["ID", "Модель"])
    wb.active.append(["product-1", "ОЗП-150"])
    wb.save(catalogue)
    return requests, appendix, catalogue


def test_prepare_uses_exact_punctuation_safe_crosswalk_and_keeps_gold_pending(tmp_path):
    req, appendix, catalogue = write_inputs(tmp_path)
    out = tmp_path / ".tmp" / "intake.xlsx"
    result = selection.prepare_intake(req, appendix, catalogue, out, tmp_path)

    assert result["status"] == "pending_oracle"
    assert result["join_counts"] == {"exact_unique": 1, "no_exact_name": 1}
    assert result["appendix_only_rows"] == 1
    wb = load_workbook(out, data_only=True)
    rows = list(wb["Позиции"].values)
    assert rows[1][8] == "exact_unique"
    assert rows[1][9] is None
    assert rows[2][8] == "no_exact_name"
    assert wb["Только приложение"].max_row == 2
    wb.close()


def test_prepare_refuses_to_write_private_source_data_outside_tmp(tmp_path):
    req, appendix, catalogue = write_inputs(tmp_path)
    with pytest.raises(ValueError, match=r"under repository \.tmp/"):
        selection.prepare_intake(req, appendix, catalogue, tmp_path / "public.xlsx", tmp_path)


def test_packaged_cli_uses_working_directory_as_private_project_root(tmp_path, monkeypatch, capsys):
    req, appendix, catalogue = write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = selection.main([
        "prepare", "--requests", str(req), "--appendix", str(appendix),
        "--catalogue", str(catalogue), "--output", ".tmp/intake.xlsx",
    ])
    assert result == 0
    assert json.loads(capsys.readouterr().out)["status"] == "pending_oracle"
    assert (tmp_path / ".tmp/intake.xlsx").is_file()


def test_grader_separates_false_selection_from_safe_abstention(tmp_path):
    gold = tmp_path / "gold.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    gold.write_text("\n".join([
        json.dumps({"request_id": "1", "gold_status": "exact", "product_id": "p1",
                    "evidence_refs": ["tender.xlsx#row=1", "engineer-review#row=1"]}),
        json.dumps({"request_id": "2", "gold_status": "insufficient_data",
                    "evidence_refs": ["standard.pdf#page=4"]}),
        json.dumps({"request_id": "3", "gold_status": "expert_review",
                    "evidence_refs": ["standard.pdf#page=8"]}),
    ]) + "\n", encoding="utf-8")
    candidate.write_text("\n".join([
        json.dumps({"request_id": "1", "decision": "select", "product_id": "wrong",
                    "evidence_refs": ["catalogue.xlsx#product=wrong"], "system_id": "test",
                    "system_version": "1.0"}),
        json.dumps({"request_id": "2", "decision": "abstain", "system_id": "test",
                    "system_version": "1.0"}),
        json.dumps({"request_id": "3", "decision": "review", "system_id": "test",
                    "system_version": "1.0"}),
    ]) + "\n", encoding="utf-8")

    result = selection.score_selection(gold, candidate)
    assert result["scored_rows"] == 3
    assert result["selected_rows"] == 1
    assert result["false_positive_selections"] == 1
    assert result["selection_precision"] == 0.0
    assert result["counts"]["correct_safe_abstention"] == 1
    assert result["counts"]["correct_expert_review"] == 1


def test_grader_refuses_empty_or_unsupported_gold(tmp_path):
    gold = tmp_path / "gold.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    candidate.write_text("", encoding="utf-8")
    gold.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="oracle is empty"):
        selection.score_selection(gold, candidate)

    gold.write_text(json.dumps({"request_id": "1", "gold_status": "guess"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported gold_status"):
        selection.score_selection(gold, candidate)


def test_cli_reports_invalid_oracle_as_a_clean_error(tmp_path, capsys):
    gold = tmp_path / "gold.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    gold.write_text("", encoding="utf-8")
    candidate.write_text("", encoding="utf-8")
    assert selection.main(["score", "--gold", str(gold), "--candidate", str(candidate)]) == 2
    output = capsys.readouterr()
    assert "oracle is empty" in output.err
    assert "Traceback" not in output.err


def test_grader_does_not_count_pending_gold_as_accuracy(tmp_path):
    gold = tmp_path / "gold.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    gold.write_text(json.dumps({"request_id": "1", "gold_status": "pending"}) + "\n", encoding="utf-8")
    candidate.write_text(json.dumps({"request_id": "1", "decision": "select", "product_id": "p1",
                                    "evidence_refs": ["catalogue#p1"], "system_id": "test",
                                    "system_version": "1.0"}) + "\n", encoding="utf-8")
    result = selection.score_selection(gold, candidate)
    assert result["scored_rows"] == 0
    assert result["pending_gold_rows"] == 1
    assert result["selection_precision"] is None
    assert result["exact_match_recall"] is None


def test_excel_rows_are_scored_with_separate_gold_candidate_and_usage_fields(tmp_path):
    req, appendix, catalogue = write_inputs(tmp_path)
    book = tmp_path / ".tmp" / "intake.xlsx"
    selection.prepare_intake(req, appendix, catalogue, book, tmp_path)
    wb = load_workbook(book)
    ws = wb["Позиции"]
    columns = {str(c.value): c.column for c in ws[1]}
    gold_values = {
        "Эталонный статус": "exact", "Эталонный SKU": "p1",
        "Источник эталона": "tender.xlsx#row=1\nengineer-review#row=1",
        "Решение системы": "select", "SKU системы": "p1",
        "Источник доказательства системы": "catalogue.xlsx#product=p1",
        "ID системы": "selector", "Версия системы": "1.2.3", "Модель системы": "glm",
        "Время системы, с": 1.25, "Токены входа": 100, "Токены выхода": 20,
    }
    for header, value in gold_values.items():
        ws.cell(2, columns[header], value)
    abstain_values = {
        "Эталонный статус": "insufficient_data", "Источник эталона": "standard.pdf#page=4",
        "Решение системы": "abstain", "ID системы": "selector", "Версия системы": "1.2.3",
        "Модель системы": "glm", "Время системы, с": 0.3, "Токены входа": 10, "Токены выхода": 2,
    }
    for header, value in abstain_values.items():
        ws.cell(3, columns[header], value)
    wb.save(book)
    wb.close()

    result = selection.score_selection(book, book)
    assert result["scored_rows"] == 2
    assert result["pending_gold_rows"] == 0
    assert result["correct_exact_selections"] == 1
    assert result["counts"]["correct_safe_abstention"] == 1
    assert result["selection_precision"] == 1.0
    assert result["exact_match_recall"] == 1.0
    assert result["system_ids"] == ["selector"]
    assert result["system_versions"] == ["1.2.3"]
    assert result["models"] == ["glm"]
    assert result["elapsed_seconds_total"] == pytest.approx(1.55)
    assert result["input_tokens_total"] == 110
    assert result["output_tokens_total"] == 22

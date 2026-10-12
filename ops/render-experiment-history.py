#!/usr/bin/env python3
"""Build the public history from retained public receipts; never invoke a model.

Run from any directory with Python 3.10+. Existing experiment outputs and scores
are read-only. This index is replaceable; its cited receipts remain the evidence.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/megamen32/catalog-extraction-benchmark/blob/main/"
SOURCES: dict[str, dict] = {}


def read(relative: str) -> dict:
    path = ROOT / relative
    raw = path.read_bytes()
    previous = SOURCES.get(relative)
    digest = hashlib.sha256(raw).hexdigest()
    if previous and previous["sha256"] != digest:
        raise RuntimeError(f"Receipt changed while rendering: {relative}; retry after publication")
    if not previous:
        stamp = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", relative], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip() or None
        SOURCES[relative] = {"sha256": digest, "last_commit_time": stamp}
    return json.loads(raw)


def evaluation(engineering: int, expected: int, drawing: int = 0,
               drawing_expected: int = 0) -> dict:
    assert 0 <= engineering <= expected and 0 <= drawing <= drawing_expected
    return {"engineering_correct": engineering, "engineering_expected": expected,
            "drawing_correct": drawing, "drawing_expected": drawing_expected}


def round_entry(number: int, scores: dict, valid: int, pages: int,
                elapsed: float | None, timing: str, **extra) -> dict:
    return {"round": number, "evaluations": scores, "valid_pages": valid,
            "expected_pages": pages, "elapsed_seconds": elapsed,
            "elapsed_definition": timing, **extra}


def collect() -> list[dict]:
    experiments = []

    def add(identifier, label, dataset, stage, primary, rounds, receipts, **extra):
        experiments.append({"id": identifier, "label": label, "dataset": dataset,
                            "stage": stage, "primary_grader": primary, "rounds": rounds,
                            "receipts": receipts, **extra})

    old = "examples/agent-routing/2026-10-12-v1.4.1/manifest.json"
    data = read(old)
    for arm, values in data["arms"].items():
        add("v141-" + arm, "1.4.1 / " + arm, "v1", "first_pass", "0.2.2",
            [round_entry(1, {"0.2.2": evaluation(values["correct"], 500)},
                         values["completed_pages"], 15, values["elapsed_seconds_sum"],
                         "sum of native attempt durations")], [old],
            model=data["model"], protocol={k: data[k] for k in
                ["program_revision", "contract_sha256", "max_tokens", "runtime_versions"]},
            complete=True, planned_rounds=1)

    repeated = "examples/agent-routing/2026-10-12-repeated-runs/manifest.json"
    regraded = "examples/agent-routing/2026-10-12-repeated-runs/regrade-v0.2.4.json"
    historical, new = read(repeated), read(regraded)
    for variant, program in [("v142", "1.4.2"), ("v144", "1.4.4")]:
        rounds = []
        for old_round, new_round in zip(historical["variants"][variant]["rounds"],
                                        new["variants"][variant]["rounds"]):
            assert old_round["round"] == new_round["round"]
            rounds.append(round_entry(old_round["round"], {
                "0.2.2": evaluation(old_round["correct"], 500),
                "0.2.4": evaluation(new_round["correct"], 500)},
                new_round["completed_pages"], 15, old_round["elapsed_seconds_sum"],
                "sum of attempt durations, overlapping when concurrent",
                retained_first_round=old_round["retained_historical_round"]))
        add(variant, program, "v1", "first_pass", "0.2.4", rounds,
            [repeated, regraded], model=historical["variants"][variant]["protocol"]["model"],
            protocol=historical["variants"][variant]["protocol"], complete=True,
            planned_rounds=3, offline_regrade_model_calls=0)

    fresh = "examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json"
    data = read(fresh)
    add("v146", "1.4.6", "v1", "first_pass", "0.2.4",
        [round_entry(r["round"], {"0.2.4": evaluation(r["correct"], 500)},
                     r["completed_pages"], 15, r["elapsed_seconds_sum"],
                     "sum of attempt durations, overlapping when concurrent") for r in data["rounds"]],
        [fresh], model=data["protocol"]["model"], protocol=data["protocol"],
        complete=True, planned_rounds=3, all_rounds_fresh=True)

    offline = "examples/offline-regrading/2026-10-12-v032/summary.json"
    rescored = read(offline)
    initial = []
    for number in (1, 2):
        receipt = f"examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-{number}/summary.json"
        data = read(receipt)
        current = next(r for r in rescored["rounds"] if
                       r["profile"] == "our-initial" and r["round"] == f"round-{number}")
        initial.append(round_entry(number, {
            "0.3.0": evaluation(data["engineering_correct"], 520, data["drawing_correct"], 21),
            "0.3.1": evaluation(data["corrected_engineering_correct"], 520, data["corrected_drawing_correct"], 21),
            "0.3.2": evaluation(current["engineering_correct"], 520, current["drawing_correct"], 21)},
            data["valid_first_pass_candidates"], 17, data["round_wall_elapsed_seconds"],
            "pipeline round wall at snapshot; includes review/repair/admission; not extractor sum"))
    add("legacy-mixed", "1.4.2 → 1.4.8 / первая выгрузка", "v2", "first_pass", "0.3.2",
        initial, [offline] + [f"examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-{n}/summary.json" for n in (1, 2)],
        model="MiniMax-M3.1-Flash-Preview → glm-5.3-flash Coding Endpoint",
        protocol=data["native_roles"], complete=False, planned_rounds=3,
        status="checkpointed; third round not started; replaced by a fresh corrected cohort")

    xmanifest = "examples/project-x/2026-10-12-native-vision-v1-full/manifest.json"
    xs = "examples/project-x/2026-10-12-native-vision-v1-full/summary.json"
    xm, summary = read(xmanifest), read(xs)
    for model in xm["models"]:
        rounds, receipts = [], [xmanifest, xs]
        for number in (1, 2, 3):
            receipt = f"examples/project-x/2026-10-12-native-vision-v1-full/{model}/round-{number}/results.json"
            data = read(receipt)
            rounds.append(round_entry(number, {v: evaluation(
                s["engineering"]["correct"], 520, s["drawing"]["correct"], 21)
                for v, s in data["scores"].items()}, data["valid_json_cases"], 17,
                data["timing"]["subprocess_seconds_sum"], "sum of full per-case subprocess wall durations"))
            receipts.append(receipt)
        add("project-x-" + model, "Project X / " + model, "v2", "first_pass", "0.3.2",
            rounds, receipts, model=model, complete=True, planned_rounds=3,
            protocol={k: xm[k] for k in ["snapshot", "integration", "integration_sha256", "image_preparation",
                "max_output_tokens", "temperature", "native_json_syntax_repair_maximum", "response_format_policy"]},
            offline_regrade_model_calls=0)

    native = "examples/project-x/2026-10-12/manifest.json"
    data = read(native)
    add("project-x-direct", "Project X / PDF без Vision", "v2", "direct_parser", "0.3.0",
        [round_entry(i, {"0.3.0": evaluation(r["engineering_correct"], 520, r["drawing_correct"], 21)},
                     r["attempts"], 17, r["elapsed_seconds_sum"], "sum of full per-case subprocess wall durations")
         for i, r in enumerate(data["rounds"], 1)], [native], model=None, complete=True,
        planned_rounds=3, provider_calls=0)

    corrected = "examples/agent-routing/2026-10-12-corrected-v032/manifest.json"
    data = read(corrected)
    # Publisher emits all-17 initial snapshots separately from closed review rounds.
    # Do not turn a partial run into zero accuracy or mix acceptance with initial extraction.
    stages = {stage: [] for stage in ["first_pass", "available_draft", "accepted_delivery"]}
    stage_receipts = {stage: [corrected] for stage in stages}
    for number in (1, 2, 3):
        for stage in stages:
            folder = f"first-pass-round-{number}" if stage == "first_pass" else f"round-{number}"
            receipt = f"examples/agent-routing/2026-10-12-corrected-v032/{folder}/round.json"
            if not (ROOT / receipt).exists():
                continue
            snapshot = read(receipt)
            assert snapshot["round"] == number and snapshot["primary_grader_release"] == "0.3.2"
            values = snapshot[stage]
            baseline = snapshot["baseline_v0_3_0"]
            assert baseline["grader_sha256"] == "24b64859fd690d11afd8477c69a0f84336a28338ac0b49981e5300055364d57a"
            old = baseline[stage]
            assert values["engineering_expected"] == old["engineering_expected"] == 520
            assert values["drawing_expected"] == old["drawing_expected"] == 21
            assert values["selected_pages"] == old["selected_pages"] == 17
            stages[stage].append(round_entry(number, {
                "0.3.0": evaluation(old["engineering_correct"], 520, old["drawing_correct"], 21),
                "0.3.2": evaluation(values["engineering_correct"], 520, values["drawing_correct"], 21)},
                values["valid_pages"], 17, snapshot.get("report", {}).get("wall_seconds"),
                "round wall when retained in public report; unknown otherwise"))
            stage_receipts[stage].append(receipt)
    for stage, rounds in stages.items():
        add("corrected-mixed-" + stage, "1.4.15 → 1.4.17 / " + {
            "first_pass": "первая выгрузка", "available_draft": "последний черновик",
            "accepted_delivery": "принятый результат"}[stage], "v2", stage, "0.3.2",
            rounds, stage_receipts[stage], model="MiniMax-M3.1-Flash-Preview → glm-5.3-flash Coding Endpoint",
            protocol={"native_roles": data["native_roles"], "method": data["method"],
                      "plan_sha256": data["plan_sha256"], "observed_sdk_versions": data["observed_sdk_versions"]},
            complete=len(rounds) == 3, planned_rounds=3, status=data["status"])

    parsers = "examples/parser-outputs/2026-10-12/manifest.json"
    parser_regrade = "examples/parser-outputs/2026-10-12/regrade-v0.2.2.json"
    data, regrade = read(parsers), read(parser_regrade)
    by_engine = {c["engine"]: c for c in regrade["configurations"]}
    for configuration in data["configurations"]:
        engine, metrics = configuration["engine"], configuration["historical_metrics"]
        new = by_engine[engine]
        add("parser-" + engine, engine, "v1", "direct_parser", "0.2.2",
            [round_entry(1, {"0.2.0": evaluation(metrics["correct_facts"], 500),
                             "0.2.2": evaluation(new["regraded_correct"], 500)},
                         metrics["completed_cases"], 15, metrics["elapsed_seconds"],
                         metrics.get("elapsed_seconds_definition", "sum of per-case monitored durations"))],
            [parsers, parser_regrade], model=None, complete=True, planned_rounds=1,
            versions=configuration["versions"], backend_version=metrics.get("backend_version"),
            offline_regrade_model_calls=0)
    return experiments


def stats(exp: dict, component="engineering") -> dict | None:
    if len(exp["rounds"]) < 3 or not exp["complete"]:
        return None
    values = [r["evaluations"][exp["primary_grader"]] for r in exp["rounds"]]
    if not values[0][component + "_expected"]:
        return None
    percentages = [100 * v[component + "_correct"] / v[component + "_expected"] for v in values]
    return {"mean_percent": statistics.mean(percentages), "sample_sd_pp": statistics.stdev(percentages),
            "minimum_percent": min(percentages), "maximum_percent": max(percentages)}


def cell(r: dict, grader: str, component="engineering") -> str:
    values = r["evaluations"][grader]
    correct, expected = values[component + "_correct"], values[component + "_expected"]
    return "—" if not expected else f"{correct}/{expected} ({correct / expected * 100:.2f}%)"


def linked(exp: dict) -> str:
    return f"[{exp['label']}]({BASE}{exp['receipts'][0]})"


def table(experiments: list[dict], component="engineering") -> list[str]:
    lines = ["| Программа / профиль | Оценщик | Раунд 1 | Раунд 2 | Раунд 3 | Среднее ± SD, п.п. | Валидных страниц | Время по раундам, с |",
             "|---|---|---|---|---|---|---|---|"]
    for exp in experiments:
        rounds = exp["rounds"]
        columns = [cell(r, exp["primary_grader"], component) for r in rounds]
        missing = "не проводился" if exp["planned_rounds"] == 1 else (
            "не запускался" if exp.get("status", "").startswith("checkpointed") else "ожидается")
        columns += [missing] * (3 - len(columns))
        distribution = stats(exp, component)
        mean = f"{distribution['mean_percent']:.2f}% ± {distribution['sample_sd_pp']:.2f}" if distribution else "нет трёх завершённых раундов"
        pages = "; ".join(f"{r['valid_pages']}/{r['expected_pages']}" for r in rounds) or "ожидается"
        times = "; ".join(f"{r['elapsed_seconds']:.1f}" if r["elapsed_seconds"] is not None else "не записано" for r in rounds) or "ожидается"
        lines.append("| " + " | ".join([linked(exp), exp["primary_grader"], *columns[:3], mean, pages, times]) + " |")
    return lines


def render(experiments: list[dict]) -> str:
    lines = ["# Единая история испытаний", "",
        "**96,6% сохранились: это 483/500 в первом прогоне 1.4.2.** По трём сохранённым прогонам этой версии оценщик 0.2.4 даёт среднее 94,13%, а не 96,6%. Новая связка и расширенный набор проверяются отдельно; они не наследуют старый процент.", "",
        "Эта страница собирается из опубликованных результатов. [Машиночитаемая сводка](../examples/experiment-history.json) содержит версии, методы, время, ссылки и контрольные суммы источников. Таблицы показывают точность выбранных проверяемых фактов; точность всей страницы и всех каталогов пока не установлена.", "",
        "## Как читать историю", "",
        "- Набор v1: 15 страниц, 500 инженерных фактов. Набор v2: 17 страниц, 520 фактов и отдельно 21 проверка чертежей. v1 сохранён; оба набора доступны одновременно.",
        "- Первая выгрузка модели, исправляемый черновик и принятый проверяющим результат — разные стадии. Ниже первая выгрузка сравнивается с первой выгрузкой Project X. Готовность после проверки публикуется отдельно.",
        "- Для законченного раунда неудачные/невалидные ответы остаются в фиксированном знаменателе с нулём. Ещё не начатый раунд и новая страница, которой не было в старом запуске, обозначаются как отсутствующие измерения.",
        "- SD — выборочное стандартное отклонение по трём неокруглённым процентам, в процентных пунктах. Одного хорошего запуска недостаточно для выбора версии.",
        "- Время сохраняется в секундах. Старые параллельные испытания и Project X дают суммы времени попыток; смешанная связка — длительность раунда на момент снимка с проверками и ожиданием лимитов. Сравнение скорости по этим разным определениям некорректно.", "",
        "## Сохранённые испытания на v1 / 500 фактов", "",
        "Модель всех агентских строк: MiniMax-M3.1-Flash-Preview, medium, без второго проверяющего. У 1.4.2 и 1.4.4 первый раунд сохранён из первоначального испытания, два следующих были свежими. У 1.4.6 все три свежие. Различались и программа, и версии плагина: это сравнение полных профилей.", ""]
    lines += table([e for e in experiments if e["dataset"] == "v1" and e["stage"] == "first_pass"])
    lines += ["", "## Расширенный v2 / 520 инженерных фактов", "",
        "Project X здесь означает адаптированную Vision-интеграцию v1, а не весь исходный банковский продукт. Для неё завершены три свежих последовательных раунда каждой модели. Старая смешанная связка остановлена после двух первоначальных раундов; у исправленной 1.4.15 → 1.4.17 три свежих раунда ещё выполняются. Итоговый победитель новой связки пока не установлен.", ""]
    expanded = [e for e in experiments if e["dataset"] == "v2" and e["stage"] in ["first_pass", "direct_parser"]]
    lines += table(expanded)
    lines += ["", "## Черновик и принятый результат новой связки", "",
        "Эти строки обновляются после завершения каждого полного цикла. Принятый результат требует отчёта проверяющего; отклонённые страницы не становятся принятыми от наличия JSON. Пока цикл не завершён, итоговая точность стадии не заявляется.", ""]
    lines += table([e for e in experiments if e["stage"] in ["available_draft", "accepted_delivery"]])
    lines += ["", "## Чертежи / 21 отдельная проверка", "",
        "Табличная точность не заменяет точность привязки размеров к элементам чертежа. Статистические графики — линейные, столбчатые, круговые — в этот набор пока не входят.", ""]
    lines += table(expanded, "drawing")
    lines += ["", "## Два оценщика одновременно, без повторного вызова моделей", "",
        "В одном раунде может быть несколько оценок одного сохранённого ответа. Старые файлы оценки остаются на месте, новая версия записывает отдельный файл. В сводке первичный оценщик для v2 — 0.3.2; 0.3.0 и 0.3.1 видны рядом. Пересчёт не исправляет ответ программы и не является новым прогоном модели.", "",
        "| Профиль | Раунд | Старый оценщик: факты / чертежи | Новый оценщик: факты / чертежи | Дополнительные вызовы моделей |",
        "|---|---|---|---|---|"]
    for exp in experiments:
        if exp["stage"] == "direct_parser" and exp["dataset"] == "v1":
            continue
        for r in exp["rounds"]:
            if len(r["evaluations"]) < 2:
                continue
            old = next(iter(r["evaluations"]))
            new = exp["primary_grader"]
            fmt = lambda version: f"{version}: {cell(r, version)} / {cell(r, version, 'drawing')}"
            lines.append(f"| {linked(exp)} | {r['round']} | {fmt(old)} | {fmt(new)} | 0 |")
    lines += ["",
        "У 1.4.2, раунд 3, сохранённый ответ получил 406/500 по старому алгоритму и 466/500 по 0.2.4: оценщик научился учитывать однозначную группу размеров верхнего фланца. JSON не менялся. В 0.3.2 добавлены ограниченные физические алиасы единиц и английских обозначений геометрии; неправильные числа, допуски и принадлежность размера по-прежнему считаются ошибками.", "",
        "Новая страница может быть оценена задним числом только если её ответ действительно сохранён. У ранних 15-страничных испытаний нет результатов для новых страниц 27 и 39. Их нельзя превращать в якобы выполненный полный 17-страничный прогон.", "",
        "## Что произошло между высокими и низкими результатами", "",
        "1. 483/500 было верным результатом конкретного первого запуска. Три повтора выявили разброс; исправление оценщика изменило оценку одного сохранённого ответа, не работу модели.",
        "2. В расширенных испытаниях были настоящие сбои сохранения: запись секции рисунков после полной страницы могла стереть таблицу. На странице 38 инновационных изделий это превратило ранее сохранённую таблицу 72/72 в итоговые 0/72. Промежуточный ответ не подставлялся вместо доставленного.",
        "3. Изменился профиль: добавился второй агент, новая логика сохранения и новый набор. Низкий результат первой выгрузки старой связки не объясняется только добавлением 20 фактов: на прежних 500 фактах получено 381/500 и 459/500.",
        "4. Исправленное сохранение проверено через настоящий MCP на выходе рабочей оцифровки: таблица, 64 ячейки и текст сохранились после обновления рисунков и финализации. Это проверка конкретного бага, а не подтверждение 96% для новой версии.", "",
        "Сейчас исправленная связка проходит три раунда на замороженных v2/0.3.2. Оцифровка всех каталогов идёт отдельно. Следующий выбор программы будет опираться на эти новые три измерения; ошибки размеров, объединённых ячеек и слишком строгой буквальной проверки исправляются с отдельной версией и отдельным испытанием.", "",
        "## Отдельные пробы, которые не заменяют полный раунд", "",
        "- [1.4.3, страница 26: 15/15](../examples/agent-routing/2026-10-12-delivery-v1.4.3/manifest.json), 99,455 с. Этот ответ не подменяет неудачную попытку 1.4.2.",
        "- [Первичная Vision-проба Project X](../examples/project-x/2026-10-12-vision-preview/results.json): по старой строгой оценке страницы 78 MiniMax дал 108/140, GLM — 136/140. По одному ответу нельзя делать вывод о стабильности модели. Позднейшие полные раунды — отдельные свежие попытки.",
        "- Ранние 98,57% относились к 138/140 буквально прочитанным ячейкам одной страницы 78; это другой показатель, не точность всех каталогов.", "",
        "## Прямые парсеры: 21 конфигурация на v1", "",
        "315 попыток, 297 сохранённых выходных файлов; без дополнительных вызовов агентских моделей при переоценке. Некоторые парсеры используют собственные OCR/VLM-компоненты. Это первая обработка без агентского проверяющего, на прежнем наборе. Полные версии и определения времени находятся в сводке и [оригинальном манифесте](../examples/parser-outputs/2026-10-12/manifest.json).", "",
        "| Конфигурация | Оценщик 0.2.0 | Оценщик 0.2.2 | Валидных страниц | Время, с |",
        "|---|---|---|---|---|"]
    for exp in experiments:
        if exp["stage"] == "direct_parser" and exp["dataset"] == "v1":
            r = exp["rounds"][0]
            lines.append(f"| {exp['label']} | {cell(r, '0.2.0')} | {cell(r, '0.2.2')} | {r['valid_pages']}/15 | {r['elapsed_seconds']:.3f} |")
    lines += ["", "## Хронология опубликованных доказательств", "",
        "Ниже время последнего Git-коммита каждого исходного манифеста, UTC. Оно показывает публикацию/обновление доказательства, а не обязательно начало обработки. Фактическое время обработки, когда оно записано, остаётся в самом манифесте.", "",
        "| Последняя публикация, UTC | Доказательство |", "|---|---|"]
    for path, source in sorted(SOURCES.items(), key=lambda item: item[1]["last_commit_time"] or ""):
        lines.append(f"| {source['last_commit_time'] or 'ещё не закоммичен'} | [{path}]({BASE}{path}) |")
    lines += ["", "Воспроизвести индекс: `python3 ops/render-experiment-history.py`. Команда только читает опубликованные результаты и создаёт эту страницу и JSON-сводку; парсеры и модели не запускаются.", ""]
    return "\n".join(lines)


def main() -> None:
    experiments = collect()
    for exp in experiments:
        exp["engineering_distribution"] = stats(exp)
        exp["drawing_distribution"] = stats(exp, "drawing")
    document = render(experiments)
    # Fail if a source was published or changed during collection.
    for relative, source in SOURCES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == source["sha256"]
    index = {"schema_version": "1.0", "accuracy_scope": "selected source-reviewed facts, not full pages",
             "datasets": {"v1": {"pages": 15, "engineering": 500, "drawing": 0},
                          "v2": {"pages": 17, "engineering": 520, "drawing": 21}},
             "additional_model_or_parser_calls": 0, "source_receipts": SOURCES,
             "experiments": experiments}
    (ROOT / "docs/EXPERIMENT-HISTORY-RU.md").write_text(document, encoding="utf-8")
    (ROOT / "examples/experiment-history.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"experiments": len(experiments), "source_receipts": len(SOURCES),
                      "model_calls": 0, "parser_calls": 0}))


if __name__ == "__main__":
    main()

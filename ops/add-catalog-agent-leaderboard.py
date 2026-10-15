#!/usr/bin/env python3
"""Add retained agent first passes to a NEW common15 snapshot; no model calls.

Use the released 0.3.0 package with this checkout's pinned 0.3.2 matching module.
--baseline-package optionally points at an unpacked released wheel.
"""
import argparse
import copy
import hashlib
import importlib.util
import importlib.metadata
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = "examples/tool-leaderboard/common-15-v032/manifest.json"
OUT = ROOT / "examples/tool-leaderboard/common-15-with-agent-v032"
BASELINE = "24b64859fd690d11afd8477c69a0f84336a28338ac0b49981e5300055364d57a"
PRIMARY = "f091872c67af7e410490df6b590cb8ac03a05eb6e615351ed281c4ae1687e21d"
MODULE = "e268c25f302e051d6b34295298eac6603dba8ff9f108003bb9bd3f3a2685972d"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-package", type=Path)
    args = parser.parse_args()
    if args.baseline_package:
        sys.path.insert(0, str(args.baseline_package.resolve()))
    from catalog_bench.benchmark import grader_digest, score_file
    assert grader_digest() == BASELINE, "Use the frozen released 0.3.0 package"
    module_path = ROOT / "src/catalog_bench/language_corrected_grader.py"
    assert digest(module_path) == MODULE
    spec = importlib.util.spec_from_file_location("pinned032", module_path)
    primary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(primary)
    assert primary.language_grader_digest() == PRIMARY

    observed = {}

    def read(relative):
        path = ROOT / relative
        observed[relative] = digest(path)
        return json.loads(path.read_text())

    def write(path, value):
        text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if path.exists():
            assert path.read_text() == text, f"Same-version retained audit drift: {path}"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    parent = read(PARENT)
    manifest = copy.deepcopy(parent)
    fixtures = {c["id"]: c for c in read("src/catalog_bench/data/engineering-catalogs-v1/dataset.json")["cases"]}
    assert len(fixtures) == 15
    fixture_paths = {key: ROOT / "src/catalog_bench/data/engineering-catalogs-v1" / value["fixture"]
                     for key, value in fixtures.items()}
    for key, path in fixture_paths.items():
        assert digest(path) == parent["fixture_sha256"][key]
        observed[str(path.relative_to(ROOT))] = digest(path)

    def assess(identifier, label, rounds, protocol, receipt, planned=3):
        reports = []
        for number, records in enumerate(rounds, 1):
            assert set(records) == set(fixtures)
            cases, totals, elapsed, valid = [], {"0.3.0": 0, "0.3.2": 0}, [], 0
            for key, case in records.items():
                fixture = fixtures[key]
                assert case["source_sha256"] == fixture["source_sha256"]
                assert case["physical_page"] == fixture["physical_page"]
                if case.get("fixture_sha256"):
                    assert case["fixture_sha256"] == parent["fixture_sha256"][key]
                entry = {"case_id": key, "expected": fixture["coverage"]["engineering_facts"],
                         "source_sha256": case["source_sha256"],
                         "fixture_sha256": parent["fixture_sha256"][key],
                         "status": case["status"], "elapsed_seconds": case["elapsed_seconds"],
                         "correct": {"0.3.0": 0, "0.3.2": 0}}
                if case.get("candidate"):
                    path = ROOT / case["candidate"]
                    assert digest(path) == case["candidate_sha256"]
                    observed[case["candidate"]] = digest(path)
                    scores = {"0.3.0": score_file(fixture_paths[key], path),
                              "0.3.2": primary.score_language_corrected(fixture_paths[key], path)}
                    entry.update(candidate=case["candidate"], candidate_sha256=digest(path), score_files={})
                    for version, score in scores.items():
                        assert score["engineering_facts"]["expected"] == entry["expected"]
                        assert score["drawing_assertions"]["expected"] == 0
                        text = json.dumps(score, ensure_ascii=False).lower()
                        assert not any(s in text for s in ["/home/", "/users/", "bearer "]), "Private marker in score artifact"
                        target = OUT / identifier / f"round-{number}" / key / f"score-v{version}.json"
                        write(target, score)
                        entry["score_files"][version] = str(target.relative_to(ROOT))
                        entry["correct"][version] = score["engineering_facts"]["correct"]
                        totals[version] += entry["correct"][version]
                    valid += 1
                if case["elapsed_seconds"] is not None:
                    elapsed.append(case["elapsed_seconds"])
                cases.append(entry)
            assert sum(c["expected"] for c in cases) == 500
            reports.append({"round": number, "expected": 500, "correct": totals,
                            "valid_pages": valid, "expected_pages": 15,
                            "elapsed_seconds_sum_known": sum(elapsed), "cases_with_known_time": len(elapsed),
                            "elapsed_seconds_sum": sum(elapsed) if len(elapsed) == 15 else None,
                            "elapsed_definition": "Retained per-attempt time; native extractor duration for profile 1.4.15. No wall-time speed comparison.",
                            "cases": cases})
        percentages = [r["correct"]["0.3.2"] / 5 for r in reports]
        manifest["rows"].append({"id": identifier, "label": label,
            "model_or_mode": "первый проход / " + protocol["model"],
            "stage": "first_pass", "reviewer_run": False,
            "versions": protocol, "source_receipt": receipt, "rounds": reports,
            "rounds_count": len(reports), "rounds_planned": planned,
            "series_complete": len(reports) == planned,
            "mean_percent": statistics.mean(percentages),
            "baseline_mean_percent": statistics.mean(r["correct"]["0.3.0"] / 5 for r in reports),
            "sample_sd_pp": statistics.stdev(percentages) if len(reports) > 1 else None,
            "minimum_percent": min(percentages), "maximum_percent": max(percentages),
            "statistical_winner_established": False})

    def legacy_records(path, rounds):
        result = []
        for round_data in rounds:
            result.append({case["case_id"]: {
                **{k: case[k] for k in ["source_sha256", "physical_page", "status", "elapsed_seconds"]},
                "fixture_sha256": case["fixture_sha256"],
                "candidate": str(Path(path).parent / case["output"]["file"]) if case.get("output") and case["status"] == "completed" else None,
                "candidate_sha256": case["output"]["sha256"] if case.get("output") else None}
                for case in round_data["cases"]})
        return result

    repeated = "examples/agent-routing/2026-10-12-repeated-runs/manifest.json"
    data = read(repeated)
    assert data["complete"] and data["stage"] == "first_pass" and not data["reviewer_run"]
    for key in ["v142", "v144"]:
        variant = data["variants"][key]
        assess("catalog-to-json-" + key, "catalog-to-json " + variant["protocol"]["program_version"],
               legacy_records(repeated, variant["rounds"]), variant["protocol"], repeated)
    fresh = "examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json"
    data = read(fresh)
    assert data["complete"] and data["fresh_rounds"] == 3 and not data["reviewer_run"]
    assess("catalog-to-json-v146", "catalog-to-json 1.4.6", legacy_records(fresh, data["rounds"]), data["protocol"], fresh)

    corrected = "examples/agent-routing/2026-10-12-corrected-v032/manifest.json"
    data = read(corrected)
    rounds = []
    for number in [1, 2]:
        receipt = str(Path(corrected).parent / f"first-pass-round-{number}/round.json")
        records = {}
        for case in read(receipt)["execution_cases"]:
            if case["case_id"] not in fixtures:
                continue
            checksum = case.get("first_pass_dual_grading", {}).get("same_candidate_sha256")
            calls = [c for c in case["calls"] if c.get("role") == "extractor"]
            call = next((c for c in calls if checksum and c.get("artifact", {}).get("sha256") == checksum), calls[0] if calls else {})
            artifact = call.get("artifact") if checksum else None
            if artifact:
                assert calls and call is calls[0], "A later repair cannot replace the first pass"
                assert call["status"] == "completed" and artifact["sha256"] == checksum
            records[case["case_id"]] = {"source_sha256": case["source_sha256"],
                "physical_page": case["physical_page"], "status": "completed" if artifact else "failed_first_pass",
                "elapsed_seconds": call.get("native_elapsed_seconds"),
                "candidate": str(Path(corrected).parent / artifact["file"]) if artifact else None,
                "candidate_sha256": checksum}
        rounds.append(records)
    role = data["native_roles"]["extractor"]
    assess("catalog-to-json-v1415-first-pass", "catalog-to-json 1.4.15", rounds,
           {"program": role["program"], "contract_sha256": role["contract_sha256"], "model": role["model"]}, corrected)

    manifest["rows"].sort(key=lambda r: (-r["mean_percent"], r["id"]))
    last, rank = None, 0
    for ordinal, row in enumerate(manifest["rows"], 1):
        if row["mean_percent"] != last:
            rank = ordinal
            last = row["mean_percent"]
        row["rank"] = rank
    manifest.update(schema_version="1.1", our_orchestrator_included=True,
        parent_snapshot={"path": PARENT, "sha256": observed[PARENT]},
        additional_model_or_parser_calls=0, prior_candidate_rows_regraded=False,
        added_first_pass_profiles=4, current_program_accuracy_inherited=False,
        added_profiles_regrading_runtime={"python": sys.version, "baseline_grader_sha256": BASELINE,
            "primary_grader_sha256": PRIMARY, "primary_module_sha256": MODULE,
            "dependencies": {name: importlib.metadata.version(name) for name in ["pydantic", "pymupdf"]}},
        source_receipts={**parent["source_receipts"], **{k: v for k, v in observed.items() if k.endswith("manifest.json") or k.endswith("round.json")}})
    for relative, expected in observed.items():
        assert digest(ROOT / relative) == expected, f"Input changed: {relative}"
    write(OUT / "manifest.json", manifest)
    render_spec = importlib.util.spec_from_file_location("leaderboard_renderer", ROOT / "ops/render-tool-leaderboard.py")
    renderer = importlib.util.module_from_spec(render_spec)
    render_spec.loader.exec_module(renderer)
    renderer.check_privacy(manifest)
    renderer.render(manifest)
    print(json.dumps({"configurations": len(manifest["rows"]), "model_calls": 0,
        "agent_rows": [{k: r[k] for k in ["label", "rank", "mean_percent", "rounds_count"]}
                       for r in manifest["rows"] if r["id"].startswith("catalog-to-json-")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

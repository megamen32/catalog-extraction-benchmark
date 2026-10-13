import json
from pathlib import Path
import pytest
from catalog_bench.regressions import inspect_registry, read_registry, registry_root, score_regression, register_pending


def test_retained_cases_and_pending_glyph_are_not_one_accuracy_denominator():
    result = inspect_registry()
    assert len(result['cases']) == 8
    assert result['retained_artifact_hashes_verified']
    assert not result['changes_engineering_denominator']
    assert not score_regression('small4-glyph-z-or-e', {})['scored']


def test_real_source_word_repair_retains_unusual_literal_product_codes():
    root = registry_root()
    before = json.loads((root / 'artifacts/innov181-before15.json').read_text())
    after = json.loads((root / 'artifacts/innov181-after15.json').read_text())
    assert score_regression('innov181-engineering-identities', before)['passed'] == 2
    assert score_regression('innov181-engineering-identities', after)['passed'] == 2
    after['tables'][0]['rows'][2]['cells'][1]['value'] = 'АС 70/12'
    assert score_regression('innov181-engineering-identities', after)['passed'] == 1


def test_demo_role_requires_contextual_evidence_and_no_promoted_demo_tables():
    candidate = {'page_context': {'kind': 'software_demonstration', 'source_evidence': [
        {'kind': 'software_demonstration', 'transcription': 'contextual_summary'}]}, 'tables': []}
    assert score_regression('small4-software-example', candidate)['passed'] == 3
    candidate['tables'] = [{'demo': 'not a catalogue offer'}]
    assert score_regression('small4-software-example', candidate)['passed'] == 2
    assert score_regression('small4-software-example', {})['passed'] == 0


def test_legacy_input_schema_accepts_additive_meaning_metadata():
    from catalog_bench.schema import PageContent
    page = json.loads((registry_root() / 'artifacts/innov181-after15.json').read_text())
    baseline = PageContent.model_validate(page)
    page['page_context'] = {'kind': 'catalogue_product_data', 'summary': 'Product parameters'}
    current = PageContent.model_validate(page)
    assert current.tables == baseline.tables
    assert current.figures == baseline.figures


def test_registration_is_pending_idempotent_and_preserves_old_cases(tmp_path):
    case = registry_root() / 'small4-software-example.json'
    first = register_pending(case, tmp_path)
    assert first == register_pending(case, tmp_path)
    assert first['status'] == 'pending_adjudication'
    assert inspect_registry(tmp_path)['cases'][0]['status'] == 'pending_adjudication'
    captured = json.loads(Path(first['case_file']).read_text())
    assert all((tmp_path / a['path']).is_file() for a in captured['artifacts'])
    changed = tmp_path / 'changed.json'
    captured['title'] = 'Conflicting replacement'
    # Existing retained evidence can be supplied relative to the captured registry.
    changed.write_text(json.dumps(captured))
    with pytest.raises(ValueError, match='Existing case differs'):
        register_pending(changed, tmp_path)

"""Source-bound regressions, separate from frozen engineering score denominators."""
from pathlib import Path
import hashlib
import json
import re


def registry_root():
    return Path(__file__).with_name('data') / 'catalogue-regressions-v1'


def read_registry(root=None):
    root = Path(root) if root else registry_root()
    if (root / 'registry.json').exists():
        checksums = json.loads((root / 'checksums.json').read_text())
        for name, digest in checksums.items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f'Changed frozen regression annotation: {name}')
    index = (json.loads((root / 'registry.json').read_text()) if (root / 'registry.json').exists()
             else {'id': 'catalogue-regression-inbox', 'version': 'unadjudicated', 'case_files': []})
    files = [root / name for name in index['case_files']] + sorted((root / 'inbox').glob('*.json'))
    if not files:
        raise ValueError('Empty or missing regression registry')
    cases = [json.loads(path.read_text()) for path in files]
    ids = set()
    for case in cases:
        validate_case(case)
        if case['id'] in ids:
            raise ValueError('Duplicate regression ID')
        ids.add(case['id'])
        for artifact in case['artifacts']:
            raw = (root / artifact['path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
                raise ValueError(f'Changed retained artifact: {artifact["path"]}')
            json.loads(raw)
    return index, cases


def validate_case(case):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', case['id']):
        raise ValueError('Invalid regression ID')
    if case['status'] not in {'confirmed', 'pending_adjudication', 'diagnostic'}:
        raise ValueError('Invalid regression adjudication status')
    source = case['source']
    if not re.fullmatch(r'[0-9a-f]{64}', source['sha256']) or type(source['physical_page']) is not int or source['physical_page'] < 1:
        raise ValueError('Source hash and physical page are required')
    if not case.get('title') or not case.get('review_basis'):
        raise ValueError('Record the failure and source-review basis')
    for assertion in case['assertions']:
        if assertion['op'] not in {'equals', 'empty', 'contains', 'any_match'}:
            raise ValueError('Unsupported regression assertion')


def inspect_registry(root=None):
    index, cases = read_registry(root)
    return {'registry': index['id'], 'version': index['version'],
            'cases': [{k: c[k] for k in ('id', 'status', 'category', 'title')} for c in cases],
            'automatic_assertions': sum(len(c['assertions']) for c in cases if c['status'] == 'confirmed'),
            'retained_artifact_hashes_verified': True,
            'changes_engineering_denominator': False}


def score_regression(case_id, candidate, root=None):
    index, cases = read_registry(root)
    case = next((c for c in cases if c['id'] == case_id), None)
    if case is None:
        raise ValueError(f'Unknown regression: {case_id}')
    if case['status'] != 'confirmed' or not case['assertions']:
        return {'registry': index['id'], 'case': case_id, 'status': case['status'],
                'scored': False, 'reason': 'No adjudicated automatic oracle; excluded from accuracy totals'}
    results = []
    for assertion in case['assertions']:
        value = candidate
        try:
            for part in assertion['path']:
                value = value[part]
            op, expected = assertion['op'], assertion.get('expected')
            passed = (value == expected if op == 'equals' else value == [] if op == 'empty'
                      else expected in value if op == 'contains'
                      else isinstance(value, list) and any(isinstance(x, dict) and all(x.get(k) == v for k, v in expected.items()) for x in value))
        except (KeyError, IndexError, TypeError):
            passed = False
        results.append({'path': assertion['path'], 'passed': bool(passed)})
    return {'registry': index['id'], 'version': index['version'], 'case': case_id,
            'scored': True, 'passed': sum(r['passed'] for r in results), 'total': len(results),
            'checks': results, 'coverage': case.get('coverage_note', 'Only declared assertions'),
            'changes_engineering_denominator': False}


def register_pending(case_path, destination):
    """Capture exact new evidence immediately; adjudication is a separate step."""
    case_path, destination = Path(case_path), Path(destination)
    case = json.loads(case_path.read_text())
    case['status'] = 'pending_adjudication'
    validate_case(case)
    inbox = destination / 'inbox'
    objects = destination / 'objects'
    inbox.mkdir(parents=True, exist_ok=True)
    objects.mkdir(exist_ok=True)
    for artifact in case['artifacts']:
        raw = (case_path.parent / artifact['path']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != artifact['sha256']:
            raise ValueError('Retained evidence changed before registration')
        json.loads(raw)
        target = objects / (digest + '.json')
        if target.exists() and target.read_bytes() != raw:
            raise ValueError('Existing evidence identity collision')
        target.write_bytes(raw)
        artifact['path'] = 'objects/' + target.name
    target = inbox / (case['id'] + '.json')
    raw = (json.dumps(case, ensure_ascii=False, indent=2) + '\n').encode()
    if target.exists() and target.read_bytes() != raw:
        raise ValueError('Existing case differs; retain it and use a new case ID')
    target.write_bytes(raw)
    return {'registered': case['id'], 'status': case['status'], 'case_file': str(target),
            'model_calls': 0, 'changes_engineering_denominator': False}

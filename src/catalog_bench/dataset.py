"""Frozen annotations travel with the installed wheel; source PDFs do not."""
import hashlib
import json
from pathlib import Path
from .benchmark import BenchmarkCase

DATASET_ID = 'engineering-catalogs-v1'


def dataset_root():
    return Path(__file__).with_name('data') / DATASET_ID


def load_dataset():
    return json.loads((dataset_root() / 'dataset.json').read_text())


def fixture_path(case_id):
    matches = [c for c in load_dataset()['cases'] if c['id'] == case_id]
    if len(matches) != 1:
        raise ValueError(f'Unknown benchmark case: {case_id}')
    return dataset_root() / matches[0]['fixture']


def validate_dataset():
    dataset = load_dataset()
    checksums = json.loads((dataset_root() / 'checksums.json').read_text())
    for name, digest in checksums.items():
        if hashlib.sha256((dataset_root() / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Changed frozen annotation: {name}')
    ids = set()
    for case in dataset['cases']:
        if case['id'] in ids:
            raise ValueError('Duplicate case identity')
        ids.add(case['id'])
        fixture = BenchmarkCase.model_validate_json(fixture_path(case['id']).read_text())
        if fixture.id != case['id'] or fixture.source_sha256 != case['source_sha256'] or fixture.page != case['physical_page']:
            raise ValueError(f'Case/fixture binding mismatch: {case["id"]}')
        count = sum(len(row) for table in fixture.tables for row in table.rows) + len(fixture.selected_facts)
        if count != case['coverage']['engineering_facts']:
            raise ValueError('Declared coverage differs from source assertions')
        if fixture.tables and not fixture.semantic_columns:
            raise ValueError('Full body has no engineering column annotations')
    return {'dataset': dataset['id'], 'version': dataset['version'], 'cases': len(ids),
            'engineering_facts': sum(c['coverage']['engineering_facts'] for c in dataset['cases']),
            'full_page_ground_truth': False, 'checksums_verified': True}


def export_dataset(destination):
    import shutil
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Export destination must be fresh')
    validate_dataset()
    shutil.copytree(dataset_root(), destination, dirs_exist_ok=True)
    return destination

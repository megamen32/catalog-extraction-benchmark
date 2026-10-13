"""Fast unit: unknown own-column conditions cannot prove source absence (max15s)."""
import json
from pathlib import Path
import pytest
from catalog_bench.supplemental_drawing_audit_v101 import audit

FIXTURE=Path('fixtures/supplemental/opn27-drawing-v1.json')
BASE=Path('examples/supplemental-drawing-audit-v1/opn27-candidate-2/candidate.json')

def graded(tmp_path,field,value):
    content=json.loads(BASE.read_text());column=next(c for c in content['tables'][1]['columns'] if 'утечки' in c['label'])
    column[field]=value;p=tmp_path/'candidate.json';p.write_text(json.dumps(content,ensure_ascii=False))
    result=audit(FIXTURE,p);return next(c for c in result['checks'] if c['id']=='lower-creepage-no-minimum')['status']

@pytest.mark.parametrize('value',['at least','не более','минимум 10'])
def test_explicit_unprinted_bounds_are_wrong(tmp_path,value):
    assert graded(tmp_path,'qualifier',value)=='wrong'

@pytest.mark.parametrize('field,value',[
    ('qualifier','условие неизвестно'),('group','новое неизвестное условие'),
    ('label','Длина пути утечки тока при неизвестном условии'),
])
def test_unknown_condition_does_not_prove_absence(tmp_path,field,value):
    assert graded(tmp_path,field,value)=='missing'

@pytest.mark.parametrize('value',[None,'','условие «не менее» не указано','без условия не менее'])
def test_empty_or_explicitly_absent_condition_passes(tmp_path,value):
    assert graded(tmp_path,'qualifier',value)=='passed'

def test_retained_candidates_and_all_other_checks_unchanged():
    from catalog_bench.supplemental_drawing_audit import audit as old
    for n in (1,2):
        p=BASE.parent.parent/f'opn27-candidate-{n}'/'candidate.json';before=p.read_bytes()
        a=old(FIXTURE,p);b=audit(FIXTURE,p)
        assert a['checks'][:12]==b['checks'][:12] and before==p.read_bytes()
        assert {k:b['checks'][12][k] for k in a['checks'][12]}==a['checks'][12]
        assert (a['passed'],a['wrong'],a['missing'])==(b['passed'],b['wrong'],b['missing'])

def test_disclaimer_does_not_erase_a_second_asserted_bound(tmp_path):
    assert graded(tmp_path,'qualifier','условие не указано, но at least 10')=='wrong'

def test_unknown_after_absence_statement_remains_missing(tmp_path):
    assert graded(tmp_path,'qualifier','условие не указано; другая оговорка неизвестна')=='missing'

def test_energy_bound_never_borrowed_from_adjacent_column(tmp_path):
    content=json.loads(BASE.read_text());energy=next(c for c in content['tables'][1]['columns'] if 'энерг' in c['label'].lower())
    energy['qualifier']='at least 10';p=tmp_path/'candidate.json';p.write_text(json.dumps(content,ensure_ascii=False))
    result=audit(FIXTURE,p);assert result['checks'][-1]['status']=='passed'

@pytest.mark.parametrize('value',['условие at least не указано','без условия не более','without condition at most'])
def test_supported_negated_bounds_never_wrong(tmp_path,value):
    assert graded(tmp_path,'qualifier',value)=='passed'

def test_unsupported_negated_bound_is_missing(tmp_path):
    assert graded(tmp_path,'qualifier','not at least')=='missing'

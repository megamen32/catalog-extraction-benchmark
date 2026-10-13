"""Fast unit: separate compared objects from owned diameters; max10s/expected1s.

Real retained candidate is the RED reproducer. No source/model/fixture edits.
"""
import json
from pathlib import Path
import pytest
from catalog_bench.dataset import fixture_path
from catalog_bench.language_corrected_grader import score_language_corrected
from catalog_bench.ownership_corrected_grader import score_ownership_corrected

REAL=Path('examples/corrected-results-v033/retained-candidate39-reproducer.json')
FIXTURE=fixture_path('catalog-1-page-039','engineering-catalogs-v2')

def status(tmp_path,text,check='pitch116',title='Вид Б'):
    data=json.loads(REAL.read_text())
    data['figures']=[dict(title=title,description=text,labels=[])]
    path=tmp_path/'candidate.json';path.write_text(json.dumps(data,ensure_ascii=False))
    result=score_ownership_corrected(FIXTURE,path)
    return next(c['status'] for c in result['drawing_assertions']['checks'] if c['id']==check)

def test_retained_real_candidate_is_not_false_wrong():
    before=REAL.read_bytes();old=score_language_corrected(FIXTURE,REAL);new=score_ownership_corrected(FIXTURE,REAL)
    oldcheck=next(c for c in old['drawing_assertions']['checks'] if c['id']=='pitch116')
    newcheck=next(c for c in new['drawing_assertions']['checks'] if c['id']=='pitch116')
    assert oldcheck['status']=='wrong' and newcheck['status']=='passed'
    assert old['engineering_facts']==new['engineering_facts']
    assert old['metrics']==new['metrics'] and old['candidate_sha256']==new['candidate_sha256']
    assert REAL.read_bytes()==before

@pytest.mark.parametrize('text',[
    'Ø116 — наружная окружность.',
    'Внешний контур диаметром Ø116.',
    'Ø116 — наружный контур; отверстие между Ø116 и внешним контуром.',
    'Отверстие между Ø140 и внешним контуром Ø116.',
    'Между внешней окружностью Ø116 и центральной втулкой находится отверстие.',
])
def test_genuine_outer_ownership_remains_wrong(tmp_path,text):
    assert status(tmp_path,text)=='wrong'

@pytest.mark.parametrize('text',[
    'Отверстие между Ø116 и внешним контуром.',
    'Отверстие между внешним контуром и Ø116.',
    'Ø116 — штрихпунктирная окружность; отверстие между Ø116 и внешним контуром.',
    'Ø116 — штрихпунктирная окружность; отверстие между внешним контуром и Ø116.',
])
def test_comparison_is_not_owner_claim_or_positive_rescue(tmp_path,text):
    expected='passed' if 'штрих' in text else 'missing'
    assert status(tmp_path,text)==expected

def test_scope_numeric_negation_and_outer140_not_relaxed(tmp_path):
    assert status(tmp_path,'Ø116 — не наружный контур.')=='missing'
    assert status(tmp_path,'Ø2116 — наружный контур.')=='missing'
    assert status(tmp_path,'Ø116 — штрихпунктирная окружность.',title='Вид А')=='missing'
    assert status(tmp_path,'Отверстие между Ø140 и внешним контуром.',check='outer140')=='missing'


def test_all_verified_without_expected_tables_uses_new_drawing_conjunction(tmp_path):
    fixture=json.loads(FIXTURE.read_text());fixture['selected_facts']=[];fixture['tables']=[]
    fixture['drawing_assertions']=[next(a for a in fixture['drawing_assertions'] if a['id']=='pitch116')]
    f=tmp_path/'fixture.json';f.write_text(json.dumps(fixture,ensure_ascii=False))
    candidate=json.loads(REAL.read_text());candidate['tables']=[]
    candidate['figures']=[dict(title='Вид Б',description='Ø116 — штрихпунктирная окружность; отверстие между Ø116 и внешним контуром.',labels=[])]
    p=tmp_path/'candidate.json';p.write_text(json.dumps(candidate,ensure_ascii=False))
    assert not score_language_corrected(f,p)['all_verified_checks_passed']
    assert score_ownership_corrected(f,p)['all_verified_checks_passed']

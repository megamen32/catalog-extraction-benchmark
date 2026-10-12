"""Fast unit: correct charge-scope numeric boundaries without changing frozen fixtures.
Expected1s maximum5s; no model calls.
"""
import json
from catalog_bench.dataset import dataset_root
from catalog_bench.drawing import score_drawing_assertions
from catalog_bench.corrected_drawing_grader import corrected_assertions,CORRECTED_GRADER_VERSION


def assertions():return json.loads((dataset_root('engineering-catalogs-v2')/'fixtures/catalog-1-page-027.json').read_text())['drawing_assertions']

def test_wrong_longer_charge_cannot_borrow_source_group_scope():
    selected=next(a for a in assertions() if a['id']=='12-III-outer140')
    data={'figures':[{'title':'11,2 Кл III СЗ','description':'Вид Б: наружный контур φ140.','labels':[]}]}
    assert score_drawing_assertions([selected],data)['correct']==1  # retained frozen defect
    assert score_drawing_assertions(corrected_assertions([selected]),data)['correct']==0
    assert CORRECTED_GRADER_VERSION=='0.3.1'


def test_correct_literal_scopes_and_fixture_bytes_preserved():
    path=dataset_root('engineering-catalogs-v2')/'fixtures/catalog-1-page-027.json';before=path.read_bytes();original=assertions();corrected=corrected_assertions(original)
    for charge in ['1,2','1.2']:
        a=next(a for a in corrected if a['id']=='12-III-outer140');data={'figures':[{'title':charge+' Кл III СЗ','description':'Вид Б: наружный контур φ140.','labels':[]}]};assert score_drawing_assertions([a],data)['correct']==1
    assert path.read_bytes()==before and original==assertions()

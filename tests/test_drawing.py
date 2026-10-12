"""Fast unit, purpose: detect source geometry inversion/omission/scope and preserve negation.
Expected2s, maximum10s; no model calls.
"""
import json
from catalog_bench.dataset import dataset_root,validate_dataset
from catalog_bench.drawing import score_drawing_assertions


def assertions(page):
    return json.loads((dataset_root('engineering-catalogs-v2')/'fixtures'/f'catalog-1-page-{page:03d}.json').read_text())['drawing_assertions']

def grade(id,text,page=39,title=''):
    a=next(a for a in assertions(page) if a['id']==id)
    return score_drawing_assertions([a],{'figures':[{'title':title,'description':text,'labels':[]}]})['checks'][0]['status']

def test_dimension_ownership_inversion_and_label_only():
    assert grade('outer140','Вид Б: наружная окружность φ140; пунктирная окружность φ116')=='passed'
    assert grade('outer140','Вид Б: центральная окружность φ140; пунктирная окружность φ116')=='wrong'
    assert grade('outer140','Вид Б: φ140, φ116')=='missing'
    assert grade('outer140','Вид А: наружная окружность φ140; Вид Б: φ140')=='missing'

def test_material_negation_and_omission():
    assert grade('material-source-absence','Фарфоровый корпус')=='wrong'
    assert grade('material-source-absence','Материал не указан; ребристый контур')=='passed'
    assert grade('material-source-absence','Фарфор не указан в источнике')=='passed'
    assert score_drawing_assertions([assertions(39)[0]],{'figures':[]})['correct']==0

def test_endpoint_relation_not_presence():
    assert grade('dimension50-faces','Вид А:50 — высота пластины')=='passed'
    assert grade('dimension50-faces','Вид А:50 — между осями отверстий')=='wrong'
    assert grade('dimension50-faces','Вид А:50, φ13,2отв.')=='missing'
    assert grade('dimension274-loweredge','274 — до нижнего края закругленного элемента φ500')=='passed'
    assert grade('dimension274-loweredge','274 — от верхнего края элемента φ500')=='wrong'

def test_charge_execution_scope():
    assert grade('12-III-outer140','1,2 Кл III СЗ. Вид Б: наружный контур φ140',27)=='passed'
    assert grade('12-III-outer140','1,6 Кл IV СЗ. Вид Б: наружный контур φ140',27)=='missing'

def test_v1_immutable_v2_coverage():
    assert validate_dataset()['engineering_facts']==500
    result=validate_dataset('engineering-catalogs-v2')
    assert result['cases']==17 and result['engineering_facts']==520

def test_negated_owner_and_mixed_claims_do_not_false_pass():
    assert grade('outer140','Вид Б:φ140 не наружная окружность')!='passed'
    assert grade('outer140','Вид Б:φ140 не внутренняя, а внешний контур')=='passed'
    assert grade('material-source-absence','Материал не указан, но корпус фарфоровый')=='wrong'
    assert grade('dimension50-faces','Вид А:50 не высота пластины')!='passed'

def test_numeric_boundaries_and_linear_dimension_glyph():
    for wrong in ['150','1,50','φ50']:
        assert grade('dimension50-faces','Вид А:'+wrong+' — высота пластины')!='passed'
    assert grade('outer140','Вид Б:наружный контур φ2140')!='passed'
    assert grade('dimension274-loweredge','φ274 — до нижнего края элемента φ500')!='passed'

def test_terminal_punctuation_is_not_decimal_continuation():
    assert grade('dimension50-faces','Вид А: ширина пластины50.')=='passed'
    assert grade('outer140','Вид Б: наружный контурφ140.')=='passed'
    assert grade('outer140','Вид Б: наружный контурφ140,7.')!='passed'

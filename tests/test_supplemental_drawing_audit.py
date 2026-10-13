"""Fast unit (expected1s/max15s): supplemental scope, endpoints and own-column condition."""
import json,copy
from pathlib import Path
import pytest
from catalog_bench.supplemental_drawing_audit import audit

FIXTURE=Path('fixtures/supplemental/opn27-drawing-v1.json')
BASE=Path('examples/agent-routing/2026-10-13-drawing-v126/round-1/catalog-1-page-027/candidate-1.json')
CORRECT='Вид А: 45 — между центрами первых двух отверстий; 67.5 — от оси второго отверстия до центральной оси корпуса; 135 — от левого края пластины до центральной оси корпуса. Вид Б: Ø140 — наружная окружность.'

def candidate(tmp_path,description=CORRECT):
    d=json.loads(BASE.read_text());d['figures']=[{'title':f'ОПН 35 кВ, заряд {charge} Кл, {execution} СЗ','description':description,'labels':[]} for charge in ('1,2','1,6') for execution in ('III','IV')]
    d['tables'][1]['columns'][-1].update(label='Длина пути утечки тока',unit='см',group=None,qualifier=None)
    # Energy's minimum is a separate own column and must never contaminate leakage.
    d['tables'][1]['columns'][-2].update(label='Тепловая энергия',unit='кДж/кВ',group=None,qualifier='не менее')
    p=tmp_path/'candidate.json';p.write_text(json.dumps(d,ensure_ascii=False));return p,d

def statuses(result):return {c['id']:c['status'] for c in result['checks']}

def test_all_source_relationships_and_neighbouring_minimum(tmp_path):
    p,d=candidate(tmp_path);r=audit(FIXTURE,p)
    assert r['passed']==13 and r['wrong']==r['missing']==0 and r['new_overall_benchmark_percent'] is False

@pytest.mark.parametrize('value',['145','45.1','45,1','φ45'])
def test_wrong_numeric_forms_cannot_supply_45(tmp_path,value):
    p,d=candidate(tmp_path,CORRECT.replace('45 —',value+' —'));s=statuses(audit(FIXTURE,p))
    assert all(s[f'{charge}-{execution}-45']=='missing' for charge in ('1.2','1.6') for execution in ('III','IV'))

def test_real_shared_wrong_owner_and_full_length_are_wrong(tmp_path):
    p,d=candidate(tmp_path,'Вид А: 45 и 67.5 — размеры от левого края пластины до осей отверстий; 135 — полная длина пластины. Вид Б: Ø140.')
    r=audit(FIXTURE,p);assert r['wrong']==12 and r['passed']==1

def test_no_borrowing_between_groups_or_views(tmp_path):
    p,d=candidate(tmp_path);d['figures'][0]['description']='Вид А: 45, 67.5, 135. Вид Б: '+CORRECT.split('Вид А: ')[1].split('Вид Б:')[0]
    p.write_text(json.dumps(d,ensure_ascii=False));s=statuses(audit(FIXTURE,p))
    assert all(s['1.2-III-'+n]=='missing' for n in ('45','67.5','135'))
    assert s['1.2-IV-45']=='passed'

def test_comparative_execution_prose_cannot_borrow_title_scope(tmp_path):
    p,d=candidate(tmp_path);d['figures']=d['figures'][:1];d['figures'][0]['description']=CORRECT+' Исполнение IV СЗ имеет такой же вид.';p.write_text(json.dumps(d,ensure_ascii=False));s=statuses(audit(FIXTURE,p))
    assert s['1.2-III-45']=='passed' and s['1.2-IV-45']=='missing'

def test_negated_wrong_relation_and_mixed_correct_clause(tmp_path):
    text='Вид А: 45 — не от левого края пластины, а между центрами первых двух отверстий; 67.5 — от оси второго отверстия до центральной оси корпуса; 135 — не полная длина пластины, а от левого края пластины до центральной оси корпуса.'
    p,d=candidate(tmp_path,text);r=audit(FIXTURE,p);assert r['passed']==13 and r['wrong']==0

def test_unknown_owner_words_are_missing(tmp_path):
    p,d=candidate(tmp_path,'Вид А: 45 — расстояние; 67.5 — расстояние до пары отверстий; 135 — размер пластины.');r=audit(FIXTURE,p);assert r['missing']==12 and r['passed']==1

@pytest.mark.parametrize('field',['label','group','qualifier'])
def test_minimum_only_in_own_leakage_column_is_wrong(tmp_path,field):
    p,d=candidate(tmp_path);c=d['tables'][1]['columns'][-1];c[field]=(c.get(field) or '')+' не менее';p.write_text(json.dumps(d,ensure_ascii=False));assert statuses(audit(FIXTURE,p))['lower-creepage-no-minimum']=='wrong'

def test_absent_leakage_column_or_unit_is_missing(tmp_path):
    p,d=candidate(tmp_path);d['tables'][1]['columns'][-1]['unit']=None;p.write_text(json.dumps(d,ensure_ascii=False));assert statuses(audit(FIXTURE,p))['lower-creepage-no-minimum']=='missing'

def test_negated_minimum_is_not_asserted(tmp_path):
    p,d=candidate(tmp_path);d['tables'][1]['columns'][-1]['qualifier']='условие «не менее» не указано';p.write_text(json.dumps(d,ensure_ascii=False));assert statuses(audit(FIXTURE,p))['lower-creepage-no-minimum']=='passed'

def test_table_identity_does_not_borrow_upper_or_position(tmp_path):
    p,d=candidate(tmp_path);d['tables'].reverse();p.write_text(json.dumps(d,ensure_ascii=False));assert statuses(audit(FIXTURE,p))['lower-creepage-no-minimum']=='passed'
    for r in d['tables'][0]['rows']:
        for c in r['cells']:
            if isinstance(c['value'],str):c['value']=c['value'].replace('/1,6-','/1,2-')
    p.write_text(json.dumps(d,ensure_ascii=False));assert statuses(audit(FIXTURE,p))['lower-creepage-no-minimum']=='missing'

def test_ambiguous_combined_title_does_not_cover_two_executions(tmp_path):
    p,d=candidate(tmp_path);d['figures']=[d['figures'][0]];d['figures'][0]['title']='ОПН,1,2 Кл,III и IV СЗ';p.write_text(json.dumps(d,ensure_ascii=False));r=audit(FIXTURE,p);assert r['missing']==12

def test_unowned_left_edge_context_does_not_change_correct_45(tmp_path):
    p,d=candidate(tmp_path,CORRECT.replace('45 — между центрами первых двух отверстий','45 — между центрами первых двух отверстий, левый край пластины также показан'))
    assert statuses(audit(FIXTURE,p))['1.2-III-45']=='passed'

def test_retained_real_candidates_show_missing_then_wrong():
    root=Path('examples/supplemental-drawing-audit-v1');a=root/'opn27-candidate-1/candidate.json';b=root/'opn27-candidate-2/candidate.json';before=(a.read_bytes(),b.read_bytes())
    first=audit(FIXTURE,a);second=audit(FIXTURE,b)
    assert (first['passed'],first['wrong'],first['missing'])==(1,0,12)
    assert (second['passed'],second['wrong'],second['missing'])==(1,12,0)
    assert before==(a.read_bytes(),b.read_bytes())

def test_foreign_wrapper_source_is_rejected(tmp_path):
    p,d=candidate(tmp_path);p.write_text(json.dumps({'source':{'sha256':'foreign'},'pages':[{'pdf_page':27,'content':d}]}))
    with pytest.raises(AssertionError):audit(FIXTURE,p)

@pytest.mark.parametrize('dimension,relation',[
    ('135','от левого края пластины до центральной оси второго отверстия'),
    ('67.5','от оси второго отверстия до центральной оси этого же отверстия'),
])
def test_central_axis_owned_by_hole_cannot_pass_for_body_axis(tmp_path,dimension,relation):
    p,d=candidate(tmp_path,f'Вид А: {dimension} — {relation}.');s=statuses(audit(FIXTURE,p));assert s['1.2-III-'+dimension]=='wrong'

def test_orientation_axis_is_not_dimension_endpoint(tmp_path):
    p,d=candidate(tmp_path,CORRECT.replace('45 — между центрами первых двух отверстий','45 — между центрами первых двух отверстий, параллельно центральной оси'));assert statuses(audit(FIXTURE,p))['1.2-III-45']=='passed'

def test_plate_owned_central_axis_is_not_body_axis(tmp_path):
    p,d=candidate(tmp_path,'Вид А: 135 — от левого края пластины до центральной оси пластины.');assert statuses(audit(FIXTURE,p))['1.2-III-135']=='wrong'

@pytest.mark.parametrize('dimension,relation',[
    ('67.5','от оси первого отверстия до центральной оси корпуса'),
    ('135','от оси второго отверстия до центральной оси корпуса'),
])
def test_supported_explicit_other_endpoint_is_wrong(tmp_path,dimension,relation):
    p,d=candidate(tmp_path,f'Вид А: {dimension} — {relation}.');assert statuses(audit(FIXTURE,p))['1.2-III-'+dimension]=='wrong'

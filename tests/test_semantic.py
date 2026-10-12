"""Fast unit: prevent engineering false positives; expected <1s, maximum 5s."""
import json
from catalog_bench.dataset import fixture_path, validate_dataset
from catalog_bench.benchmark import BenchmarkCase, score_file
from catalog_bench.semantic import column_match, equivalent
from catalog_bench.schema import Column
from catalog_bench.profiles.opn_small import check


def anchor():
    return BenchmarkCase.model_validate_json(fixture_path('catalog-4-page-078').read_text())


def test_source_dataset_is_frozen_and_covers_500_facts():
    assert validate_dataset()['engineering_facts'] == 500
    assert validate_dataset()['cases'] == 15


def test_composite_fields_do_not_rescue_matching_number_and_unit():
    c=Column(id='c', label='Нормированная механическая разрушающая сила при изгибе; Нормированный разрушающий крутящий момент; Строительная высота Н', unit='мм', qualifier='не более')
    assert not column_match(anchor().semantic_columns[0][4], c)['field']
    c=Column(id='c',label='Масса / D1', group='Верхний фланец',unit='мм')
    assert not column_match(anchor().semantic_columns[1][2], c)['field']


def test_empty_unit_can_inherit_but_explicit_conflicting_unit_cannot():
    ann=anchor().semantic_columns[0][1]
    assert column_match(ann,Column(id='c',label='Номинальное напряжение, кВ',unit=''))['unit']
    assert not column_match(ann,Column(id='c',label='Номинальное напряжение, кВ',unit='мм'))['unit']


def test_source_frequency_and_invented_bounds_are_checked():
    ann=anchor().semantic_columns[0][11]
    c=Column(id='c',label='Разрядное напряжение в загрязненном и увлажненном состоянии',unit='кВ',qualifier='не менее')
    assert not column_match(ann,c)['frequency']
    c=Column(id='c',label='Нормированный разрушающий крутящий момент',unit='кН·м',qualifier='не менее')
    assert not column_match(anchor().semantic_columns[0][3],c)['bounds']


def test_numeric_format_is_equivalent_but_unknown_is_not_a_blank(tmp_path):
    assert equivalent('2,80',2.8)
    assert not equivalent(None,0)
    case=anchor();cells=[{'column_id':f'c{i}','value':v,'state':'blank' if v is None else 'value'} for i,v in enumerate(case.tables[1].rows[0])]
    # Real source blank is not evidence of extraction failure.
    for cell in cells:
        if cell['state']=='blank':cell['state']='unknown'
    assert any(cell['state']=='unknown' for cell in cells)


def test_drawing_dimension_does_not_match_a_longer_number():
    f={'location':'drawings','entity':'dimension','parameter':'holes','value':'Ø14','unit':None}
    d={'tables':[],'figures':[{'title':'Drawing','description':'Ø140','labels':['Ø140']}]}
    assert check('catalog-2-page-149',f,d)['status']=='missing'


def test_source_errata_execution_scope_and_mixed_units():
    f=json.loads(fixture_path('catalog-3-page-111').read_text())['selected_facts'][3]
    assert f['row_key']=='НМЗ-45-1..НМЗ-160-3'
    assert len(f['scope']['products'])==24
    assert 'НМЗ-180-1' not in f['scope']['products']
    assert anchor().semantic_columns[1][6]['unit']=='м'


def test_selected_arm_facts_score_a_missing_page_instead_of_crashing():
    from catalog_bench.semantic import score_facts
    from catalog_bench.schema import PageContent
    case=BenchmarkCase.model_validate_json(fixture_path('catalog-3-page-103').read_text())
    result=score_facts(case,PageContent(title='',text_blocks=[],tables=[],figures=[]))
    assert result['expected']==15 and result['correct']==0


def test_positive_figure_labels_never_match_a_denial_and_negative_labels_handle_dash_glyphs():
    from catalog_bench.benchmark import score_content
    from catalog_bench.schema import PageContent,Figure
    c=PageContent(title='',text_blocks=[],tables=[],figures=[Figure(title='',labels=[],description='На чертеже отсутствуют H±2, L и D.')])
    assert score_content(anchor(),c)['metrics']['figure_labels']['correct']==0
    c.figures[0].labels=['А–А']
    assert score_content(anchor(),c)['metrics']['forbidden_label_absence']['correct']==2


def test_product_identity_is_not_recovered_from_an_unrelated_comment():
    f=json.loads(fixture_path('catalog-1-page-017').read_text())['selected_facts'][0]
    d={'tables':[{'id':'t','title':'','columns':[{'id':'n','label':'Комментарий'}, {'id':'v','label':'Наибольшее длительно допустимое рабочее напряжение','unit':'кВ'}], 'rows':[{'cells':[{'column_id':'n','value':f['entity'],'state':'value'}, {'column_id':'v','value':f['value'],'state':'value'}]}]}], 'figures':[]}
    assert check('catalog-1-page-017',f,d)['status']=='missing'


def test_composite_nominal_and_maximum_voltage_fails_selected_profile():
    f=json.loads(fixture_path('catalog-1-page-017').read_text())['selected_facts'][0]
    d={'tables':[{'id':'t','title':'','columns':[{'id':'n','label':'Наименование'}, {'id':'v','label':'Наибольшее длительно допустимое рабочее напряжение / Номинальное напряжение','unit':'кВ'}], 'rows':[{'cells':[{'column_id':'n','value':f['entity'],'state':'value'}, {'column_id':'v','value':f['value'],'state':'value'}]}]}], 'figures':[]}
    assert check('catalog-1-page-017',f,d)['status']!='passed'


def test_dimension_symbol_cannot_rescue_mass_in_selected_profile():
    from catalog_bench.profiles.arm_iz import field_matches
    assert not field_matches({'column':'d1'},{'label':'Масса / d1','group':'Размеры, мм'})


def test_leaf_condition_may_live_in_qualifier():
    from catalog_bench.dataset import fixture_path
    case=BenchmarkCase.model_validate_json(fixture_path('catalog-4-page-038').read_text())
    col=Column(id='c',label='Выдерживаемое напряжение, кВ',group='50 Гц',qualifier='под дождем')
    assert all(column_match(case.semantic_columns[0][7],col).values())


def test_frequency_50_does_not_match_150_or_multiple_conditions():
    a=anchor()
    for frequency in ['150 Гц','50 Гц и 150 Гц']:
        col=Column(id='c',label=f'Разрядное напряжение {frequency} в загрязненном и увлажненном состоянии',unit='кВ',qualifier='не менее')
        assert not column_match(a.semantic_columns[0][11],col)['frequency']
        col=Column(id='c',label=f'Выдерживаемое напряжение {frequency} в сухом состоянии',unit='кВ')
        assert not all(column_match(a.semantic_columns[0][9],col).values())


def test_pulse_durations_are_not_substrings_of_larger_numbers():
    from catalog_bench.profiles.opn_small import header_matches
    for expected,observed,current in [('8/20','18/20','5 кА'),('30/60','130/60','125 А')]:
        assert not header_matches({'parameter':f'остающееся при {current} {expected}'},{'label':f'Остающееся напряжение при {current} {observed}'})
        assert header_matches({'parameter':f'остающееся при {current} {expected}'},{'label':f'Остающееся напряжение при {current} {expected}'})

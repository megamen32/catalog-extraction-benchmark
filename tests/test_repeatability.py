"""Fast unit: retain failed attempts in repeat statistics; expected<1s/max5s."""
from catalog_bench.repeatability import round_summary,distribution,RATE_LIMIT


def test_failed_page_is_zero_not_removed():
    records=[{'status':'completed','score':{'engineering_facts':{'correct':15}},'elapsed_seconds':1},{'status':'failed','elapsed_seconds':2}]
    result=round_summary(records,{'a':15,'b':15})
    assert result['percent']==50 and result['expected']==30 and result['completed_pages']==1
    assert result['elapsed_seconds_sum']==3


def test_three_round_distribution_keeps_zero_and_scatter():
    result=distribution([100,80,0]);assert result['n']==3 and result['minimum']==0 and result['range']==100
    assert result['sample_standard_deviation']>50
    assert RATE_LIMIT.search('RateLimitError: HTTP 429 Too Many Requests')
    assert not RATE_LIMIT.search('source table has value429')


def test_variant_rejects_duplicate_cases_and_wrong_frozen_version(tmp_path):
    import json,pytest
    from catalog_bench.repeatability import validate_variant
    from catalog_bench.bench_runner import sha
    p=tmp_path/'suite.json';p.write_text('{}');source=tmp_path/'pdf';source.write_bytes(b'pdf')
    suite={'projects':[{'id':'p','version':'1.4.4-frozen','stage':'first_pass'}],'models':['model'],'cases':[{'id':'a','source':str(source),'page':1},{'id':'b','source':str(source),'page':2}]}
    variant={'suite':str(p),'suite_sha256':sha(p),'file_sha256':{},'declared_version':'1.4.4-frozen','model':'model'}
    with pytest.raises(ValueError,match='case IDs'):validate_variant(variant,suite,{'runs':[{'case_id':'a'},{'case_id':'a'}]})
    variant['declared_version']='1.4.5-frozen'
    with pytest.raises(ValueError,match='selection'):validate_variant(variant,suite,{'runs':[]})

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


def test_three_fresh_rounds_start_at_one_and_never_reuse_historical_scores(tmp_path,monkeypatch):
    import json
    from catalog_bench import repeatability
    from catalog_bench.bench_runner import sha
    source=tmp_path/'source';source.write_bytes(b'pdf')
    fixture=tmp_path/'fixture.json';fixture.write_text(json.dumps({'selected_facts':[{}]}))
    cases=[{'id':c,'source':str(source),'page':i,'fixture':str(fixture)} for i,c in enumerate(['a','b'],1)]
    suite={'projects':[{'id':'p','version':'1.4.6-frozen','stage':'first_pass'}],'models':['model'],'cases':cases,'repeats':1}
    path=tmp_path/'suite.json';path.write_text(json.dumps(suite))
    binding=dict(declared_version='1.4.6-frozen',model='model',package_version='1.4.6',git_revision='revision',contract_sha256='contract')
    variant=dict(id='v146',suite=str(path),suite_sha256=sha(path),file_sha256={},**binding)
    plan=dict(initial_mode='fresh',rounds=3,initial_concurrency=2,max_concurrency=2,successes_before_increase=4,
        rate_limit_cooldown_seconds=0,attempt_maximum_seconds=5,deadline_seconds=10,random_seed=1,
        expected_by_case={'a':1,'b':1},expected_bindings={'v146':binding},variants=[variant])
    plan_path=tmp_path/'plan.json';plan_path.write_text(json.dumps(plan));seen=[]
    def fake_run(manifest,output):
        spec=json.loads(manifest.read_text());case=spec['cases'][0]
        number=int(next(x.split('-')[1] for x in output.parts if x.startswith('round-')));seen.append(number)
        output.mkdir(parents=True);artifact=output/'candidate.json';artifact.write_text('{}')
        record=dict(case_id=case['id'],status='completed' if case['id']=='a' else 'failed',elapsed_seconds=1,
            tested_program=binding,artifact_path=str(artifact),artifact_sha256=sha(artifact),
            score={'engineering_facts':{'correct':1,'expected':1}})
        result=dict(complete=True,runs=[record]);(output/'results.json').write_text(json.dumps(result));return result
    monkeypatch.setattr(repeatability,'run_suite',fake_run)
    output=tmp_path/'out';repeatability.run(plan_path,output)
    result=json.loads((output/'results.json').read_text())
    assert seen==[1,1,2,2,3,3]
    assert result['status']=='completed' and result['initial_rounds_retained'] is False
    assert [r['percent'] for r in result['variants']['v146']['rounds']]==[50,50,50]
    assert result['variants']['v146']['distribution']['n']==3
    seen.clear();repeatability.run(plan_path,output);assert seen==[]


def test_fresh_mode_rejects_a_historical_initial_cohort(tmp_path):
    import json,pytest
    from catalog_bench.repeatability import run
    plan=dict(initial_mode='fresh',rounds=3,initial_concurrency=2,max_concurrency=2,
        expected_bindings={'v':{}},variants=[dict(id='v',initial_results='old.json')])
    p=tmp_path/'plan.json';p.write_text(json.dumps(plan))
    with pytest.raises(ValueError,match='Fresh rounds cannot retain'):run(p,tmp_path/'out')

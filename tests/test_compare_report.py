"""Fast unit/focused CLI import contract: expected <1s, maximum 5s."""
import json
from pathlib import Path
from catalog_bench.compare import compare_saved
from catalog_bench.report import summarize
from catalog_bench.schema import PageContent
from catalog_bench.io import write_json
from catalog_bench.bench_runner import sha


def test_failed_attempts_remain_in_the_denominator():
    runs=[{'project':'p','model':'m','stage':'first_pass','case_id':'catalog-1-page-017','status':'failed'},
          {'project':'p','model':'m','stage':'first_pass','case_id':'catalog-1-page-022','status':'completed','score':{'engineering_facts':{'correct':15,'expected':15}}}]
    summary=summarize({'complete':True,'runs':runs})['cohorts'][0]
    assert summary['unavailable_facts']==15
    assert summary['percent_on_attempted_cases']==50


def test_different_case_sets_are_not_claimed_comparable():
    runs=[{'project':p,'model':None,'stage':'imported_result','case_id':c,'status':'failed'} for p,c in [('one','catalog-1-page-017'),('two','catalog-1-page-022')]]
    assert not summarize({'complete':False,'runs':runs})['same_attempted_case_set']


def test_changed_imported_artifact_is_invalid_and_model_stays_unknown(tmp_path):
    candidate=tmp_path/'candidate.json'
    write_json(candidate,PageContent(title='',text_blocks=[],tables=[],figures=[]).model_dump())
    receipt={'stage':'imported_result','runtime_verified':False,'candidate_sha256':sha(candidate)}
    write_json(tmp_path/'import.json',receipt)
    entry={'project':'external','case_id':'catalog-1-page-017','stage':'imported_result','model':None,'candidate':'candidate.json','receipt':'import.json'}
    write_json(tmp_path/'manifest.json',{'artifacts':[entry]})
    run=compare_saved(tmp_path/'manifest.json')['runs'][0]
    assert run['status']=='completed' and run['model'] is None and not run['runtime_verified']
    candidate.write_text(candidate.read_text()+'\n')
    run=compare_saved(tmp_path/'manifest.json')['runs'][0]
    assert run['status']=='invalid_output'
    assert 'hash mismatch' in run['error']

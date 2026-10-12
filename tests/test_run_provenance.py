"""Fast unit/focused subprocess: retain version, method, output and time; expected <1s, max 5s."""
import json
from catalog_bench.compare import compare_saved
from catalog_bench.io import write_json
from catalog_bench.bench_runner import sha
from catalog_bench.schema import PageContent


def test_saved_runtime_keeps_executed_version_method_elapsed_and_copies_output(tmp_path):
    from catalog_bench.dataset import load_dataset
    case=next(c for c in load_dataset()['cases'] if c['id']=='catalog-1-page-017')
    candidate=tmp_path/'input.json';write_json(candidate,PageContent(title='',tables=[],figures=[],text_blocks=[]).model_dump())
    receipt={'status':'completed','model':'m','source_sha256':case['source_sha256'],'physical_page':17,
             'candidate_sha256':sha(candidate),'project_revision':'0123456789abcdef','package_version':'1.2.3',
             'contract_sha256':'c'*64,'elapsed_seconds':12.5,'timeout_seconds':300,'stage':'first_pass'}
    write_json(tmp_path/'receipt.json',receipt)
    write_json(tmp_path/'manifest.json',{'artifacts':[{'project':'p','case_id':case['id'],'model':'m','stage':'first_pass','candidate':'input.json','receipt':'receipt.json'}]})
    result=compare_saved(tmp_path/'manifest.json',tmp_path/'results')
    run=result['runs'][0]
    assert run['elapsed_seconds']==12.5
    assert run['tested_program']['git_revision']=='0123456789abcdef'
    assert run['tested_program']['package_version']=='1.2.3'
    assert run['test_method']['stage']=='first_pass'
    assert run['test_method']['timeout_seconds']==300
    assert sha(tmp_path/'results'/run['archived_artifact'])==sha(candidate)
    candidate.unlink()
    assert (tmp_path/'results'/run['archived_artifact']).exists()
    assert result['summary']['cohorts'][0]['elapsed_seconds_total']==12.5


def test_unknown_saved_version_and_time_are_not_invented(tmp_path):
    candidate=tmp_path/'input.json';write_json(candidate,PageContent(title='',tables=[],figures=[],text_blocks=[]).model_dump())
    write_json(tmp_path/'manifest.json',{'artifacts':[{'project':'external','case_id':'catalog-1-page-017','model':None,'stage':'imported_result','candidate':'input.json'}]})
    result=compare_saved(tmp_path/'manifest.json',tmp_path/'results')
    run=result['runs'][0]
    assert run['tested_program']['git_revision'] is None
    assert run['elapsed_seconds'] is None
    assert result['summary']['cohorts'][0]['elapsed_seconds_total'] is None

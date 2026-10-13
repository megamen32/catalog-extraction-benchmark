"""Fast unit: focused receipt mismatches and unknown tool-log coverage fail safely."""
import hashlib,importlib.util,json
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('focused_collector',Path(__file__).resolve().parents[1]/'ops/publish-focused-drawing-trials.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.fixture
def native(tmp_path):
    work=tmp_path/'page-0027';work.mkdir();artifact={'tables':[],'figures':[]};p=work/'candidate-1.json';p.write_text(json.dumps(artifact));program={'package_version':'1.4.26','source_code_sha256':'sourceprogram'}
    origin={'status':'receipt_verified','source_bound_save':True,'program':program,'physical_page':27,'source_sha256':'sourcepdf','role':'extractor','attempt':1,'model':'minimax','contract_sha256':'contract','artifact_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'started_at':100,'finished_at':110,'receipt':'calls/opaque/result.json'}
    receipt=work/origin['receipt'];receipt.parent.mkdir(parents=True);receipt.write_text(json.dumps({'status':'completed','artifact':artifact,'execution':{k:v for k,v in origin.items() if k not in ('status','source_bound_save','receipt')}}))
    return work,program,origin,{'role':'extractor','attempt':1,'elapsed_seconds':11,'producer':origin}

def test_actual_native_layout_and_sha_binding(native):
    work,program,origin,call=native
    p,bound,receipt=m.validate_call(call,work,program,{'extractor':'minimax'},27,'sourcepdf')
    assert p.name=='candidate-1.json' and receipt.parent.name=='opaque' and bound is origin
    p.write_text('{}')
    with pytest.raises(AssertionError):m.validate_call(call,work,program,{'extractor':'minimax'},27,'sourcepdf')

def test_foreign_model_and_traversal_rejected(native):
    work,program,origin,call=native
    with pytest.raises(AssertionError):m.validate_call(call,work,program,{'extractor':'othermodel'},27,'sourcepdf')
    origin['receipt']='../outside.json'
    with pytest.raises(AssertionError):m.validate_call(call,work,program,{'extractor':'minimax'},27,'sourcepdf')

def test_tool_usage_exact_window_and_partial_log(native):
    work,program,origin,call=native
    assert m.tool_usage(work,origin)['count'] is None
    entry={'time':105,'role':'extractor','attempt':1,'model':'minimax','contract_sha256':'contract','source_sha256':'sourcepdf','page':27,'tool':'read_drawing_paths'}
    wrong=dict(entry,attempt=2);outside=dict(entry,time=111)
    (work/'tools.jsonl').write_text('\n'.join([json.dumps(entry),json.dumps(wrong),json.dumps(outside),'unfinished']))
    result=m.tool_usage(work,origin)
    assert result['count']==1 and result['geometry_calls']==1 and result['coverage']=='partial_unparsed_lines'

def test_public_artifact_copy_never_overwrites(native,tmp_path):
    work,program,origin,call=native;target=tmp_path/'output/candidate.json'
    m.copy(work/'candidate-1.json',target,origin['artifact_sha256']);target.write_text('{}')
    with pytest.raises(AssertionError):m.copy(work/'candidate-1.json',target,origin['artifact_sha256'])

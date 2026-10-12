"""Fast unit: source-bound provider usage, dedup, unknowns and private image compaction.
Expected1s maximum5s; no API calls or native file edits.
"""
import json
from pathlib import Path
from catalog_bench.usage_collector import collect_page,compact


def write_history(work,role,attempt,records,suffix='session'):
    p=work/f'agent-{role}-{attempt}'/'home/sessions'/suffix/f'history_{role}.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'messages':[{'role':'assistant','channels':{'fast-agent-usage':[{'type':'text','text':json.dumps({'schema':'fast-agent.usage/v2','provider_attempts':records})}]}}]}));return p


def record(timestamp=15):
    return {'provider':'anthropic','model':'MiniMax-M3.1-Flash-Preview','timestamp':timestamp,'prompt':{'total':None,'uncached':5,'cache_read':90,'cache_write':None},'completion':{'total':10,'reasoning':3},'tool_calls':2,'timing':{'duration_ms':100}}


def receipt(work,attempt=0,role='extractor',start=10,end=20):
    p=work/'calls'/f'{role}-{attempt}'/'result.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'status':'completed','execution':{'role':role,'attempt':attempt,'source_sha256':'a'*64,'physical_page':27,'model':'anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium','started_at':start,'finished_at':end,'contract_sha256':'c'*64,'artifact_sha256':'f'*64,'program':{'package_version':'1.4.2','source_code_sha256':'b'*64}}}))


def test_dedup_windows_and_reasoning_subset(tmp_path):
    receipt(tmp_path);r=record();write_history(tmp_path,'extractor',0,[r,r,record(25)])
    report=collect_page(tmp_path)
    m=report['bound_usage']['metrics'];assert m['output_total']['sum']==10 and m['reasoning_subset']['sum']==3
    assert m['input_total_reported']['sum'] is None and m['input_uncached_reported']['sum']==5
    assert report['bound_usage']['provider_response_records']==1 and report['unbound_usage_records']==1
    assert report['duplicate_usage_records']==1 and report['coverage_complete'] is False


def test_all_repairs_and_final_attempt_separate(tmp_path):
    for attempt in [0,1]:receipt(tmp_path,attempt);write_history(tmp_path,'extractor',attempt,[record()])
    (tmp_path/'result.json').write_text(json.dumps({'status':'accepted','next_attempt':1}))
    report=collect_page(tmp_path)
    assert report['bound_usage']['metrics']['output_total']['sum']==20
    assert report['final_attempt_usage']['metrics']['output_total']['sum']==10


def test_previous_backups_excluded_and_unknown_failed_not_zero(tmp_path):
    p=write_history(tmp_path,'extractor',0,[record()]);p.with_name('history_extractor_previous.json').write_text(p.read_text())
    failed=tmp_path/'calls/unknown/result.json';failed.parent.mkdir(parents=True);failed.write_text(json.dumps({'status':'failed','error':'provider429'}))
    report=collect_page(tmp_path);assert report['history_files']==1
    assert report['bound_usage']['metrics']['output_total']['sum'] is None
    assert report['unbound_usage_records']==1 and report['unknown_or_failed_native_calls']==1


def test_compact_image_keeps_reference_and_native_history(tmp_path):
    original={'content':[{'type':'image','data':'aGVsbG8=','mimeType':'image/png'},{'type':'text','text':'View dimension274'}]}
    result=compact(original,Path('/private/history.json'))
    image=result['content'][0];assert image['type']=='image_reference' and image['bytes']==5 and len(image['sha256'])==64
    assert image['original_history'].endswith('history.json#/content/0') and original['content'][0]['data']=='aGVsbG8='

def test_repeated_usage_snapshot_metadata_does_not_double_count(tmp_path):
    receipt(tmp_path);r=record();updated={**r,'cost_usd':0.005};write_history(tmp_path,'extractor',0,[r,updated])
    report=collect_page(tmp_path);assert report['bound_usage']['provider_response_records']==1 and report['duplicate_usage_records']==1

def test_tree_keeps_all_attempts_and_strips_private_debug_refs(tmp_path):
    from catalog_bench.usage_collector import collect_tree,public_metrics
    w=tmp_path/'catalog/page-0027';receipt(w);write_history(w,'extractor',0,[record()])
    report=collect_tree(tmp_path,expected_pages=2,private_debug=tmp_path/'debug')
    assert report['observed_pages']==1 and not report['coverage_complete']
    public=public_metrics(report);assert 'private_debug_snapshots' not in public['pages'][0]
    assert public['all_attempts_known_usage']['metrics']['output_total']['sum']==10

def test_native_programs_are_not_mixed_in_role_totals(tmp_path):
    for attempt,version in [(0,'1.4.7'),(1,'1.4.2')]:
        receipt(tmp_path,attempt);p=tmp_path/'calls'/f'extractor-{attempt}'/'result.json';d=json.loads(p.read_text());d['execution']['program']['package_version']=version;d['execution']['program']['source_code_sha256']=('a' if version=='1.4.7' else 'b')*64;p.write_text(json.dumps(d));write_history(tmp_path,'extractor',attempt,[record()])
    report=collect_page(tmp_path);groups=report['native_program_usage']
    assert {g['program']['package_version'] for g in groups}=={'1.4.2','1.4.7'}
    assert all(g['usage']['metrics']['output_total']['sum']==10 for g in groups)


def test_latest_accepted_window_is_not_all_reviews_on_same_attempt(tmp_path):
    receipt(tmp_path,start=10,end=20);first=json.loads((tmp_path/'calls/extractor-0/result.json').read_text())['execution']
    second={**first,'started_at':30,'finished_at':40};p=tmp_path/'calls/repeated/result.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'status':'completed','execution':second}))
    reviewer={**first,'role':'reviewer','started_at':50,'finished_at':60};p=tmp_path/'calls/reviewer/result.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'status':'completed','execution':reviewer}))
    write_history(tmp_path,'extractor',0,[record(15),record(35)]);write_history(tmp_path,'reviewer',0,[record(55)])
    producer=lambda r:{**r,'status':'receipt_verified'}
    (tmp_path/'result.json').write_text(json.dumps({'status':'accepted','next_attempt':0,'candidate_producer':producer(second),'review_producer':producer(reviewer)}))
    report=collect_page(tmp_path)
    assert report['final_attempt_usage']['metrics']['output_total']['sum']==30
    assert report['latest_accepted_producer_usage']['metrics']['output_total']['sum']==20
    assert report['latest_accepted_producer_coverage_complete'] is True


def test_missing_one_receipt_window_history_is_partial(tmp_path):
    receipt(tmp_path);extra=json.loads((tmp_path/'calls/extractor-0/result.json').read_text());extra['execution'].update(started_at=30,finished_at=40)
    p=tmp_path/'calls/second/result.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(extra));write_history(tmp_path,'extractor',0,[record(15)])
    report=collect_page(tmp_path)
    assert report['coverage_complete'] is False
    assert report['attempts'][0]['completed_windows']==2 and report['attempts'][0]['windows_with_usage']==1

def test_completed_response_without_usage_is_not_full_coverage(tmp_path):
    receipt(tmp_path);p=write_history(tmp_path,'extractor',0,[record()]);d=json.loads(p.read_text());d['messages'].append({'role':'assistant','timestamp':'1970-01-01T00:00:16Z','content':[{'type':'text','text':'A response with missing usage'}]});p.write_text(json.dumps(d))
    report=collect_page(tmp_path);assert report['assistant_responses_without_usage']==1 and not report['coverage_complete']

def test_mixed_round_metadata_override_is_readonly_and_source_bound(tmp_path):
    from catalog_bench.usage_collector import collect_tree
    w=tmp_path/'round-1'/'case-27'/'page-0027';receipt(w,role='extractor');receipt(w,role='reviewer');write_history(w,'extractor',0,[record()]);write_history(w,'reviewer',0,[record()])
    producers={}
    for role in ['extractor','reviewer']:
        r=json.loads((w/'calls'/f'{role}-0'/'result.json').read_text())['execution'];producers[role]={**r,'status':'receipt_verified'}
    native_snapshot={str(p):p.read_bytes() for p in w.rglob('*.json')}
    case={'case_id':'case-27','physical_page':27,'source_sha256':'a'*64,'status':'accepted','attempt':0,'candidate_sha256':'f'*64,'review_sha256':'f'*64,'calls':[{'role':role,'status':'completed','producer':producer} for role,producer in producers.items()]}
    (w.parent.parent/'round.json').write_text(json.dumps({'cases':[case]}))
    report=collect_tree(tmp_path,expected_pages=1);page=report['pages'][0]
    assert page['page_status']=='accepted' and page['latest_accepted_producer_coverage_complete'] and page['metadata_binding']=='frozen round case metadata'
    assert page['latest_accepted_producer_usage']['metrics']['output_total']['sum']==20
    assert not (w/'result.json').exists() and native_snapshot=={str(p):p.read_bytes() for p in w.rglob('*.json')}

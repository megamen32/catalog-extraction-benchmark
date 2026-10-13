#!/usr/bin/env python3
"""Read-only receipt-bound scoring of focused repair trials; never calls models."""
import argparse,collections,hashlib,json,os,time
from pathlib import Path
from catalog_bench.dataset import fixture_path
from catalog_bench.language_corrected_grader import score_language_corrected,language_grader_digest
from catalog_bench.ownership_corrected_grader import score_ownership_corrected,ownership_grader_digest

ROOT=Path(__file__).resolve().parents[1]
SCORERS={'0.3.2':score_language_corrected,'0.3.3':score_ownership_corrected}
COLLECTOR_VERSION='0.1.0'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True);pending=p.with_suffix(p.suffix+'.pending')
    with pending.open('w') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    pending.replace(p)

def copy(p,target,expected):
    data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==expected
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert target.read_bytes()==data,'Retained artifact changed'
    else:target.write_bytes(data)

def tool_usage(work,origin):
    p=work/'tools.jsonl'
    if not p.exists():return {'coverage':'unknown_missing_log','count':None,'by_tool':None}
    counts=collections.Counter();bad=0
    for line in p.read_text().splitlines():
        try:d=json.loads(line)
        except ValueError:bad+=1;continue
        if d.get('role')==origin['role'] and d.get('attempt')==origin['attempt'] and d.get('model')==origin['model'] and d.get('contract_sha256')==origin['contract_sha256'] and d.get('source_sha256')==origin['source_sha256'] and d.get('page')==origin['physical_page'] and origin['started_at']<=d.get('time',0)<=origin['finished_at']:
            counts[d['tool']]+=1
    return {'coverage':'partial_unparsed_lines' if bad else 'receipt_window_bound_log','count':sum(counts.values()),'by_tool':dict(counts),'geometry_calls':sum(counts[n] for n in ('inspect_drawing_geometry','read_drawing_paths')),'unparsed_lines':bad,'raw_transcripts_not_published':True}

def validate_call(call,work,program,models,page,source):
    origin=call['producer'];assert origin['status']=='receipt_verified' and origin['source_bound_save'] is True
    assert origin['program']==program and origin['physical_page']==page and origin['source_sha256']==source
    assert origin['role']==call['role'] and origin['attempt']==call['attempt'] and origin['model']==models[call['role']]
    relative=Path(origin['receipt']);assert not relative.is_absolute() and '..' not in relative.parts
    receipt=work/relative;native=json.loads(receipt.read_text());assert native['status']=='completed'
    for k in ('program','physical_page','source_sha256','role','attempt','model','contract_sha256','artifact_sha256','started_at','finished_at'):assert native['execution'][k]==origin[k],k
    name=('candidate' if call['role']=='extractor' else 'review')+f"-{call['attempt']}.json";artifact=work/name
    assert sha(artifact)==origin['artifact_sha256']
    assert json.loads(artifact.read_text())==native['artifact']
    return artifact,origin,receipt

def collect(state_path,output):
    state_bytes=state_path.read_bytes();state=json.loads(state_bytes);assert state['version']=='1.4.26';rounds=[]
    for r in state['rounds']:
        pages=[]
        for p in r['pages']:
            page=p['physical_page'];assert page in (27,39);cid=f'catalog-1-page-{page:03d}';work=state_path.parent/f"round-{r['round']}"/f'page-{page:04d}';dest=output/f"round-{r['round']}"/cid
            source=p['source_sha256'];fixture=fixture_path(cid,'engineering-catalogs-v2');assert json.loads(fixture.read_text())['source_sha256']==source
            baseline=work/'candidate-0.json';copy(baseline,dest/'baseline-candidate.json',p['baseline_candidate_sha256'])
            audit_path=work/'external-audit.json';audit=json.loads(audit_path.read_text()) if audit_path.exists() else None
            if audit:assert audit['source_sha256']==source and audit['pdf_page']==page
            calls=[]
            for call in p['calls']:
                artifact,origin,receipt=validate_call(call,work,state['program'],state['models'],page,source);target=dest/artifact.name;copy(artifact,target,origin['artifact_sha256'])
                record={'role':call['role'],'attempt':call['attempt'],'producer':{k:v for k,v in origin.items() if k!='receipt'},'artifact':str(target.relative_to(ROOT)),'artifact_sha256':sha(target),'receipt_sha256':sha(receipt),'receipt_native_seconds':round(origin['finished_at']-origin['started_at'],3),'worker_elapsed_seconds':call['elapsed_seconds'],'tool_usage':tool_usage(work,origin)}
                if call['role']=='extractor':
                    scores={}
                    for version,scorer in SCORERS.items():
                        score=scorer(fixture,target);score_path=dest/f"score-v{version}-candidate-{call['attempt']}.json";write(score_path,score)
                        scores[version]={'engineering_correct':score['engineering_facts']['correct'],'engineering_expected':score['engineering_facts']['expected'],'drawing_correct':score['drawing_assertions']['correct'],'drawing_expected':score['drawing_assertions']['expected'],'score_file':str(score_path.relative_to(ROOT)),'grader_sha256':score['grader_sha256']}
                    record['scores']=scores;data=json.loads(target.read_text());initial=json.loads(baseline.read_text());record['tables_unchanged_from_seed']=data['tables']==initial['tables']
                    rejected=bool(audit and origin['artifact_sha256'] in audit.get('rejected_candidate_sha256',[]))
                    record['independent_source_audit']={'status':'rejected' if rejected else 'pending','source_sha256':source,'candidate_sha256':origin['artifact_sha256'],'audit_observed_at':audit.get('observed_at') if audit else None,'source_audit_scope':audit.get('audit_scope') if audit else None,'audit_findings_count':len(audit.get('findings',[])) if rejected else None,'model_acceptance_is_not_independent_source_acceptance':True}
                else:record['model_review_verdict']=json.loads(target.read_text())['verdict']
                calls.append(record)
            pages.append({'case_id':cid,'physical_page':page,'source_sha256':source,'baseline_candidate_sha256':p['baseline_candidate_sha256'],'status':p['status'],'latest_attempt':p.get('attempt'),'calls':calls,'failed_error_type':p.get('error_type'),'independent_source_acceptance':'pending unless matching independent proof; never inherited from model review'})
        rounds.append({'round':r['round'],'status':r['status'],'started_at':r['started_at'],'finished_at':r.get('finished_at'),'wall_seconds':r.get('finished_at',time.time())-r['started_at'],'pages':pages})
    result={'schema_version':'1.0','collector_version':COLLECTOR_VERSION,'scope':state['scope'],'profile':'1.4.26 focused drawing repairs','is_fresh_17_page_benchmark':False,'not_comparable_to_17_page_cohort_mean':True,'program':state['program'],'models':state['models'],'graders':{'0.3.2':language_grader_digest(),'0.3.3':ownership_grader_digest()},'state_sha256':hashlib.sha256(state_bytes).hexdigest(),'native_state_complete':state['complete'],'rounds':rounds,'model_calls_by_collector':0,'original_candidates_reviews_and_receipts_unchanged':True,'full_page_accuracy':False,'snapshot_unix':time.time()}
    recovery=state_path.parent/'orchestration-recovery-proof.json'
    if recovery.exists():
        proof=json.loads(recovery.read_text())
        allowed={'drawing-trials.py','drawing-trials-fixed.py','review39_completed_receipt_verified','provider_calls','reusable_review_sha256'}
        result['orchestration_recovery']={k:v for k,v in proof.items() if k in allowed}
        result['orchestration_recovery']['proof_sha256']=sha(recovery)
        result['scope']='Focused two-page drawing repair pilot with controller recovery; retained seeds and feedback; not a fresh full benchmark'
        result['strict_round_sequentiality_not_claimed']=True
        result['round_order_interrupted_by_controller_recovery']=True
    result['available_controller_source_sha256']={p.name:sha(p) for p in (state_path.parent/'drawing-trials.py',state_path.parent/'drawing-trials-fixed.py') if p.exists()}
    result['controller_hashes_are_snapshot_available_sources_not_inferred_per_call_bindings']=True
    write(output/'manifest.json',result);return result

def main():
    a=argparse.ArgumentParser();a.add_argument('--state',type=Path,required=True);a.add_argument('--output',type=Path);a.add_argument('--watch-seconds',type=float,default=0);args=a.parse_args();output=(args.output or (ROOT/'.tmp/drawing-v126/staged-output' if args.watch_seconds>0 else ROOT/'examples/agent-routing/2026-10-13-drawing-v126')).resolve();assert output.is_relative_to(ROOT);deadline=time.monotonic()+min(100800,max(0,args.watch_seconds));previous=None
    while True:
        digest=sha(args.state)+''.join(sha(p) for p in sorted(args.state.parent.glob('round-*/page-*/external-audit.json')))+''.join(sha(p) for p in (args.state.parent/'orchestration-recovery-proof.json',args.state.parent/'drawing-trials-fixed.py') if p.exists())
        if digest!=previous:
            result=collect(args.state,output);previous=digest;print(json.dumps({'snapshot_rounds':len(result['rounds']),'completed_native_calls':sum(len(p['calls']) for r in result['rounds'] for p in r['pages']),'native_complete':result['native_state_complete'],'model_calls':0}),flush=True)
            # Source audits can arrive after native acceptance; keep the finite
            # observer alive to capture those changes without any model call.
            if result['native_state_complete'] and args.watch_seconds<=0:break
        if time.monotonic()>=deadline:break
        time.sleep(min(15,max(0,deadline-time.monotonic())))

if __name__=='__main__':main()

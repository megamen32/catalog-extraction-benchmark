"""Read-only offline FastAgent usage/debug collector, independently versioned.

No provider requests, native source mutation or benchmark instruction changes.
Public metrics contain no chat; optional history snapshots/debug output are private.
"""
import argparse
import base64
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

COLLECTOR_VERSION='1.0.0'
FIELDS={
 'input_total_reported':('prompt','total'),
 'input_uncached_reported':('prompt','uncached'),
 'input_cache_read':('prompt','cache_read'),
 'input_cache_write':('prompt','cache_write'),
 'output_total':('completion','total'),
 'reasoning_subset':('completion','reasoning'),
 'tool_calls':('tool_calls',),
 'inference_duration_ms':('timing','duration_ms')}


def metric(records,path):
    known=[]
    for record in records:
        value=record
        for key in path:value=value.get(key) if isinstance(value,dict) else None
        if type(value) in (int,float):known.append(value)
    return {'sum':sum(known) if known else None,'reported_records':len(known),'missing_records':len(records)-len(known)}


def summarize(records):
    accounted=[];exact=lower=0
    for record in records:
        prompt=record.get('prompt',{});total=prompt.get('total')
        components=[prompt.get(k) for k in ['uncached','cache_read','cache_write']]
        if type(total) in (int,float):accounted.append(total);exact+=1
        elif any(type(v) in (int,float) for v in components):
            accounted.append(sum(v for v in components if type(v) in (int,float)))
            if all(type(v) in (int,float) for v in components):exact+=1
            else:lower+=1
    return {'input_accounted':{'sum':sum(accounted) if accounted else None,'exact_records':exact,'lower_bound_records':lower,'missing_records':len(records)-len(accounted),'definition':'reported prompt total, else sum of known uncached/cache_read/cache_write components; unreported components remain unknown'},'provider_response_records':len(records),'metrics':{name:metric(records,path) for name,path in FIELDS.items()},'reasoning_tokens_are_subset_of_output_total':True,'cache_read_is_subset_of_reported_prompt_total_when_provider_reports_total':True,'unknown_fields_are_null_not_zero':True}


def model_name(spec):
    spec=spec.split('?',1)[0]
    for prefix in ('anthropic.','zai.','openai.'):
        if spec.startswith(prefix):spec=spec[len(prefix):]
    return spec.lower()


def usage_records(history):
    for message in history.get('messages',[]):
        for block in message.get('channels',{}).get('fast-agent-usage',[]):
            if block.get('type')!='text':continue
            try:data=json.loads(block['text'])
            except (json.JSONDecodeError,KeyError):continue
            if data.get('schema')=='fast-agent.usage/v2':
                yield from data.get('provider_attempts',[])


def image_reference(encoded,history,pointer,mime=None):
    try:raw=base64.b64decode(encoded,validate=True)
    except ValueError:raw=encoded.encode()
    return {'type':'image_reference','mimeType':mime,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'original_history':str(history)+'#'+pointer}


def compact(value,history,pointer=''):
    if isinstance(value,dict):
        if value.get('type')=='image' and isinstance(value.get('data'),str):return image_reference(value['data'],history,pointer,value.get('mimeType'))
        return {k:compact(v,history,pointer+'/'+str(k).replace('~','~0').replace('/','~1')) for k,v in value.items()}
    if isinstance(value,list):return [compact(v,history,pointer+'/'+str(i)) for i,v in enumerate(value)]
    if isinstance(value,str) and value.startswith('data:image/') and ';base64,' in value:
        header,data=value.split(';base64,',1);return image_reference(data,history,pointer,header[5:])
    return value


def receipt_identity(receipt):
    program=receipt.get('program') or {}
    return (receipt.get('role'),receipt.get('attempt'),receipt.get('model'),receipt.get('contract_sha256'),program.get('source_code_sha256'),receipt.get('source_sha256'),receipt.get('physical_page'),receipt.get('started_at'),receipt.get('finished_at'),receipt.get('artifact_sha256'))


def collect_page(work,private_debug=None,metadata_override=None):
    work=Path(work);receipts={};unknown=0;errors=[];page_meta={}
    if metadata_override is not None:page_meta=dict(metadata_override)
    elif (work/'result.json').exists():
        try:page_meta=json.loads((work/'result.json').read_text())
        except (OSError,json.JSONDecodeError):errors.append({'kind':'unreadable_page_metadata'})
    expected_source=page_meta.get('source_sha256');expected_page=page_meta.get('pdf_page')
    for path in sorted((work/'calls').glob('*/result.json')):
        try:data=json.loads(path.read_text())
        except (OSError,json.JSONDecodeError) as exc:errors.append({'kind':'unreadable_native_receipt','file':path.name,'error_type':type(exc).__name__});unknown+=1;continue
        execution=data.get('execution',{})
        if data.get('status')!='completed' or not all(k in execution for k in ['role','attempt','model','started_at','finished_at','source_sha256','physical_page']):unknown+=1;continue
        if (expected_source and execution['source_sha256']!=expected_source) or (expected_page and execution['physical_page']!=expected_page):unknown+=1;errors.append({'kind':'receipt_source_page_mismatch'});continue
        receipts[receipt_identity(execution)]=execution
    by_attempt=defaultdict(list);by_receipt=defaultdict(list);bound=[];unbound=[];seen={};duplicates=0;program_records=defaultdict(list);program_bindings={};histories=0;snapshots=[];missing_response_usage=set();missing_response_windows=set()
    for agent in sorted(work.glob('agent-*-*')):
        try:role,attempt=agent.name[len('agent-'):].rsplit('-',1);attempt=int(attempt)
        except (ValueError,TypeError):continue
        if role not in ('extractor','reviewer'):continue
        for path in sorted((agent/'home/sessions').glob(f'*/history_{role}.json')):
            histories+=1
            try:raw=path.read_bytes();data=json.loads(raw)
            except (OSError,json.JSONDecodeError) as exc:errors.append({'kind':'unreadable_history','role':role,'attempt':attempt,'error_type':type(exc).__name__});continue
            if private_debug:
                digest=hashlib.sha256(raw).hexdigest();dest=Path(private_debug)/digest;dest.mkdir(parents=True,exist_ok=True);original=dest/path.name
                if not original.exists():original.write_bytes(raw)
                pretty=dest/(path.stem+'-compact.json');pretty.write_text(json.dumps(compact(data,original),ensure_ascii=False,indent=2)+'\n')
                snapshots.append({'role':role,'attempt':attempt,'history_sha256':digest,'original_snapshot':str(original),'compact_debug':str(pretty),'original_bytes':len(raw),'compact_bytes':pretty.stat().st_size})
            for message in data.get('messages',[]):
                if message.get('role')!='assistant' or list(usage_records({'messages':[message]})):continue
                try:stamp=datetime.fromisoformat(message.get('timestamp','').replace('Z','+00:00')).timestamp()
                except (ValueError,TypeError):continue
                for receipt_key,r in receipts.items():
                    if r['role']==role and r['attempt']==attempt and r['started_at']<=stamp<=r['finished_at']:
                        missing_response_usage.add((role,attempt,stamp));missing_response_windows.add(receipt_key)
            for record in usage_records(data):
                timestamp=record.get('timestamp');identity=(record.get('provider'),record.get('model'),timestamp) if type(timestamp) in (int,float) else (hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest(),);key=(role,attempt,*identity)
                if key in seen:
                    duplicates+=1
                    def richness(r):return sum(metric([r],path)['reported_records'] for path in FIELDS.values())
                    if richness(record)>richness(seen[key]):seen[key].clear();seen[key].update(record)
                    continue
                record=dict(record);seen[key]=record
                matching=[key for key,r in receipts.items() if r['role']==role and r['attempt']==attempt and model_name(r['model'])==model_name(record.get('model','')) and type(timestamp) in (int,float) and r['started_at']<=timestamp<=r['finished_at']]
                if len(matching)!=1:unbound.append(record);continue
                receipt_key=matching[0];execution=receipts[receipt_key];bound.append(record);by_attempt[(role,attempt)].append(record);by_receipt[receipt_key].append(record)
                program=execution.get('program') or {};program_key=(role,execution['model'],execution.get('contract_sha256'),program.get('source_code_sha256'),execution['source_sha256'],execution['physical_page'])
                program_records[program_key].append(record);program_bindings[program_key]={'role':role,'model':execution['model'],'contract_sha256':execution.get('contract_sha256'),'program':program,'source_sha256':execution['source_sha256'],'physical_page':execution['physical_page']}
    final_attempt=page_meta.get('next_attempt',page_meta.get('attempt'));final=[r for (role,attempt),records in by_attempt.items() if attempt==final_attempt for r in records]
    attempt_reports=[]
    for (role,attempt),records in sorted(by_attempt.items()):
        matching=[(key,r) for key,r in receipts.items() if r['role']==role and r['attempt']==attempt];native_seconds=sum(max(0,r['finished_at']-r['started_at']) for key,r in matching)
        attempt_reports.append({'role':role,'attempt':attempt,'usage':summarize(records),'native_receipt_wall_seconds':round(native_seconds,3),'completed_windows':len(matching),'windows_with_usage':sum(bool(by_receipt[key]) for key,r in matching),'programs':[r.get('program') for key,r in matching]})
    latest=[];latest_rows=[];latest_complete=page_meta.get('status')=='accepted'
    for role,field in [('extractor','candidate_producer'),('reviewer','review_producer')]:
        producer=page_meta.get(field) or {};key=receipt_identity(producer)
        if page_meta.get('status')=='accepted' and producer.get('status')=='receipt_verified' and key in receipts and by_receipt[key]:
            records=by_receipt[key];latest.extend(records);execution=receipts[key];latest_complete=latest_complete and key not in missing_response_windows;latest_rows.append({'role':role,'producer':producer,'usage':summarize(records),'native_receipt_wall_seconds':round(execution['finished_at']-execution['started_at'],3)})
        else:latest_complete=False
    receipt_identities={(r['source_sha256'],r['physical_page']) for r in receipts.values()}
    final_keys=[key for key,r in receipts.items() if r['attempt']==final_attempt]
    return {'collector_version':COLLECTOR_VERSION,'source_sha256':next(iter(receipt_identities))[0] if len(receipt_identities)==1 else None,'physical_page':next(iter(receipt_identities))[1] if len(receipt_identities)==1 else None,'metadata_binding':'frozen round case metadata' if metadata_override is not None else 'native per-page metadata','page_status':page_meta.get('status'),'final_attempt':final_attempt,'history_files':histories,'completed_native_calls':len(receipts),'unknown_or_failed_native_calls':unknown,'duplicate_usage_records':duplicates,'unbound_usage_records':len(unbound),'assistant_responses_without_usage':len(missing_response_usage),'coverage_complete':not unknown and not unbound and not errors and not missing_response_usage and bool(receipts) and all(bool(by_receipt[key]) for key in receipts),'bound_usage':summarize(bound),'final_attempt_usage':summarize(final),'final_attempt_definition':'all completed native windows on final numeric attempt, including repeated review epochs','final_attempt_coverage_complete':bool(final_keys) and all(bool(by_receipt[key]) and key not in missing_response_windows for key in final_keys),'latest_accepted_producer_usage':summarize(latest),'latest_accepted_producer_coverage_complete':latest_complete,'latest_accepted_producers':latest_rows,'attempts':attempt_reports,'native_program_usage':[{**program_bindings[key],'usage':summarize(records)} for key,records in sorted(program_records.items(),key=lambda kv:str(kv[0]))],'errors':errors,'limitations':['Usage is reported provider responses, not a provider billing reconciliation.','FailedSDK/429 attempts may omit usage; unknown usage is not zero.','Reasoning is an output subset and is never added again.','Provider-reported prompt total may be null; cache/uncached fields are separate and not invented.'],'private_debug_snapshots':snapshots}


def aggregate(summaries):
    summaries=list(summaries)
    metrics={}
    for field in FIELDS:
        values=[s['metrics'][field] for s in summaries]
        known=[m['sum'] for m in values if m['sum'] is not None]
        metrics[field]={'sum':sum(known) if known else None,'reported_records':sum(m['reported_records'] for m in values),'missing_records':sum(m['missing_records'] for m in values)}
    accounted=[s['input_accounted'] for s in summaries];known=[a['sum'] for a in accounted if a['sum'] is not None]
    return {'provider_response_records':sum(s['provider_response_records'] for s in summaries),'metrics':metrics,'input_accounted':{'sum':sum(known) if known else None,'exact_records':sum(a['exact_records'] for a in accounted),'lower_bound_records':sum(a['lower_bound_records'] for a in accounted),'missing_records':sum(a['missing_records'] for a in accounted)}}


def collect_tree(root,expected_pages=None,private_debug=None):
    root=Path(root)
    dirs=sorted(set(root.glob('*/page-*'))|set(root.glob('round-*/*/page-*')))
    pages=[]
    for work in dirs:
        if not (work/'calls').is_dir() and not any(work.glob('agent-*-*')):continue
        metadata_override=None;round_metadata=work.parent.parent/'round.json'
        if round_metadata.exists():
            try:
                state=json.loads(round_metadata.read_text());matching=[case for case in state.get('cases',[]) if case.get('case_id')==work.parent.name and case.get('physical_page')==int(work.name.split('-')[-1])]
                if len(matching)==1:
                    case=matching[0];metadata_override={'status':case['status'],'next_attempt':case['attempt'],'source_sha256':case['source_sha256'],'pdf_page':case['physical_page']}
                    for role,key,artifact_key in [('extractor','candidate_producer','candidate_sha256'),('reviewer','review_producer','review_sha256')]:
                        calls=[call for call in case.get('calls',[]) if call.get('role')==role and call.get('status')=='completed' and call.get('producer',{}).get('artifact_sha256')==case.get(artifact_key)]
                        if calls:metadata_override[key]=calls[-1]['producer']
            except (OSError,json.JSONDecodeError,ValueError,KeyError):pass
        page=collect_page(work,Path(private_debug)/str(work.relative_to(root)) if private_debug else None,metadata_override)
        page['relative_page_directory']=str(work.relative_to(root));pages.append(page)
    program_groups=defaultdict(list);identities={}
    for page in pages:
        for group in page['native_program_usage']:
            identity=json.dumps({k:group[k] for k in ['role','model','contract_sha256','program','source_sha256','physical_page']},sort_keys=True);identities[identity]={k:group[k] for k in ['role','model','contract_sha256','program','source_sha256','physical_page']};program_groups[identity].append(group['usage'])
    return {'native_program_usage':[{**identities[key],'usage':aggregate(values)} for key,values in sorted(program_groups.items())],'collector_version':COLLECTOR_VERSION,'observed_pages':len(pages),'expected_pages':expected_pages,'coverage_complete':bool(pages) and (expected_pages is None or len(pages)==expected_pages) and all(p['coverage_complete'] for p in pages),'all_attempts_known_usage':aggregate(p['bound_usage'] for p in pages),'final_attempts_known_usage':aggregate(p['final_attempt_usage'] for p in pages),'latest_accepted_producers_known_usage':aggregate(p['latest_accepted_producer_usage'] for p in pages),'latest_accepted_producer_complete_pages':sum(p['latest_accepted_producer_coverage_complete'] for p in pages),'assistant_responses_without_usage':sum(p['assistant_responses_without_usage'] for p in pages),'unknown_or_failed_native_calls':sum(p['unknown_or_failed_native_calls'] for p in pages),'unbound_usage_records':sum(p['unbound_usage_records'] for p in pages),'pages':pages,'unknown_tokens_are_not_zero':True}


def public_metrics(report):
    """Drop private transcript references; keep source/page identity and numbers."""
    if isinstance(report,list):return [public_metrics(value) for value in report]
    if isinstance(report,dict):return {key:public_metrics(value) for key,value in report.items() if key not in ('private_debug_snapshots','relative_page_directory','receipt')}
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('work',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--private-debug',type=Path);parser.add_argument('--tree',action='store_true');parser.add_argument('--expected-pages',type=int);parser.add_argument('--public-metrics',action='store_true');args=parser.parse_args()
    report=collect_tree(args.work,args.expected_pages,args.private_debug) if args.tree else collect_page(args.work,args.private_debug)
    if args.public_metrics:report=public_metrics(report)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'collector_version':COLLECTOR_VERSION,'observed_pages':report.get('observed_pages',1),'coverage_complete':report['coverage_complete']}))


if __name__=='__main__':main()

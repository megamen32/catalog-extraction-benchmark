"""Read-only failed-call usage, kept separate from successful native receipts.

The frozen mixed runner retains role/attempt/time windows even when native receipts
lack execution metadata. Those windows permit a weaker, explicitly partial cost
observation; they never turn a failed output into an accepted source-bound artifact.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
try:
    from .usage_collector import usage_records,model_name,summarize,aggregate,metric,FIELDS
except ImportError:
    from usage_collector import usage_records,model_name,summarize,aggregate,metric,FIELDS

PARTIAL_COLLECTOR_VERSION='0.1.0'


def collect_failed_round(root,plan):
    root=Path(root);state=json.loads((root/'round.json').read_text());cases={c['id']:c for c in plan['cases']};rows=[]
    for case in state['cases']:
        failed=[call for call in case['calls'] if call['status'] in ('failed','cancelled_owned_call')]
        counts=Counter((call['role'],call['attempt']) for call in failed)
        work=root/case['case_id']/f"page-{case['physical_page']:04d}"
        completed=[]
        for path in (work/'calls').glob('*/result.json'):
            try:receipt=json.loads(path.read_text());r=receipt.get('execution',{})
            except (OSError,json.JSONDecodeError):continue
            if receipt.get('status')=='completed' and all(k in r for k in ('role','attempt','model','started_at','finished_at')):completed.append(r)
        for call in failed:
            role=call['role'];attempt=call['attempt'];expected=cases.get(case['case_id'],{});model=plan[role];start=call.get('started_unix');elapsed=call.get('elapsed_seconds');end=start+elapsed if type(start) in (int,float) and type(elapsed) in (int,float) else None
            row={'case_id':case['case_id'],'source_sha256':case['source_sha256'],'physical_page':case['physical_page'],'role':role,'attempt':attempt,'status':call['status'],'model':model,'declared_native_runtime':state['roles'].get(role),'source_binding':'frozen_plan_and_failed_call_window_not_successful_receipt','started_unix':start,'finished_window_unix':end,'coverage_complete':False,'missing_usage_is_unknown_not_zero':True};seen={};histories=0
            if expected.get('source_sha256')!=case['source_sha256'] or expected.get('page')!=case['physical_page']:row['binding_failure']='source_page_mismatch'
            elif counts[role,attempt]!=1:row['binding_failure']='multiple_failed_windows_same_role_attempt'
            elif end is None or end<start:row['binding_failure']='missing_time_window'
            else:
                for path in (work/f'agent-{role}-{attempt}/home/sessions').glob(f'*/history_{role}.json'):
                    try:history=json.loads(path.read_text())
                    except (OSError,json.JSONDecodeError):continue
                    histories+=1
                    for record in usage_records(history):
                        stamp=record.get('timestamp')
                        if type(stamp) not in (int,float) or not start<=stamp<=end or model_name(record.get('model',''))!=model_name(model):continue
                        if any(r['role']==role and r['attempt']==attempt and model_name(r['model'])==model_name(model) and r['started_at']<=stamp<=r['finished_at'] for r in completed):continue
                        identity=(record.get('provider'),record.get('model'),stamp)
                        if identity not in seen or sum(metric([record],path)['reported_records'] for path in FIELDS.values())>sum(metric([seen[identity]],path)['reported_records'] for path in FIELDS.values()):seen[identity]=record
                response=work/f'agent-{role}-{attempt}/response.json'
                if response.exists():
                    try:
                        data=json.loads(response.read_text());row['native_reported_elapsed_seconds']=data.get('elapsed_seconds');row['native_stop_reason']=data.get('stop_reason')
                    except (OSError,json.JSONDecodeError):pass
            row['canonical_histories_observed']=histories;row['usage']=summarize(list(seen.values()));rows.append(row)
    return {'partial_collector_version':PARTIAL_COLLECTOR_VERSION,'failed_calls':len(rows),'calls_with_observed_usage':sum(bool(r['usage']['provider_response_records']) for r in rows),'known_failed_usage':aggregate(r['usage'] for r in rows),'coverage_complete':False,'successful_receipt_bound_usage_is_excluded':True,'failed_sdk_attempts_may_omit_usage':True,'declared_model_reasoning_comes_from_frozen_plan_not_usage_confirmation':True,'model_calls_performed':0,'calls':rows}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('round',type=Path);parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();report=collect_failed_round(args.round,json.loads(args.plan.read_text()));args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print({k:report[k] for k in ('partial_collector_version','failed_calls','calls_with_observed_usage','coverage_complete')})


if __name__=='__main__':main()

"""Three sequential fresh rounds of pinned production native roles.

The extraction/review subprocesses never receive fixtures or scoring code. Gold is
read only after each round; failed/nonaccepted deliveries remain zero in accuracy.
One extra live call per provider; production catalogue jobs are read-only neighbors.
This separate component uses offline grader 0.3.2 and naturally drains accepted
native calls on admission stop or finite window expiry. Legacy frozen source is unchanged.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from .io import write_json
from .language_corrected_grader import score_language_corrected as score_file, language_grader_digest

RUNNER_VERSION="0.2.0-checkpoint"
CONTROLLER_VERSION="0.1.0"

class AdmissionClosed(Exception):
    pass

def external_stop(plan):
    path=plan.get("admission_stop_file")
    if not path or not Path(path).exists():return None
    try:
        data=json.loads(Path(path).read_text())
        if type(data.get("stop_new_calls")) is not bool:return "invalid admission control"
        return data.get("reason") or "operator stop" if data["stop_new_calls"] else None
    except (OSError,ValueError,TypeError):return "unreadable admission control"


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_pins(plan):
    for name,expected in plan['file_sha256'].items():
        if digest(name)!=expected:raise ValueError('Frozen benchmark input changed: '+name)


class ActiveBudget:
    def __init__(self):self.started=time.monotonic();self.paused_since=None;self.paused_total=0;self.holders=0
    def pause(self):
        if self.holders==0:self.paused_since=time.monotonic()
        self.holders+=1
    def resume(self):
        self.holders-=1
        if self.holders==0:self.paused_total+=time.monotonic()-self.paused_since;self.paused_since=None
    def held(self):return self.paused_total+(time.monotonic()-self.paused_since if self.paused_since is not None else 0)
    def elapsed(self):return time.monotonic()-self.started-self.held()


async def wait_neighbor_pacing(path,provider,hold_path=None,model=None,budget=None,admission_check=None):
    """Honor a fresh neighbor cooldown, without resetting/replaying its work."""
    while True:
        if admission_check and admission_check():raise AdmissionClosed(admission_check())
        p=Path(path)
        if not p.exists():raise ValueError('Production provider pacing is unavailable')
        state=json.loads(p.read_text());age=max(0,time.time()-p.stat().st_mtime)
        slot=state['method']['provider_pacing'][provider]
        quota_remaining=0
        if hold_path:
            holds=json.loads(Path(hold_path).read_text());hold=holds.get('providers',{}).get(provider,{})
            if hold and hold.get('model')!=model:raise ValueError('Neighbor quota model identity differs')
            quota_remaining=max(0,hold.get('not_before_unix',0)-time.time())
        remaining=max(0,slot['backoff_remaining_seconds']-age,quota_remaining)
        if remaining<=0:return
        if quota_remaining and budget:budget.pause()
        try:await asyncio.sleep(min(30,remaining))
        finally:
            if quota_remaining and budget:budget.resume()


def load_checkpoint(plan,number):
    """Read retained state; a directory without state is ambiguous, never fresh."""
    directory=Path(plan['output'])/f'round-{number}'
    if not directory.exists():return None
    path=directory/'round.json'
    state=json.loads(path.read_text())
    if state['round']!=number:raise ValueError('Checkpoint round differs')
    if state.get('primary_grader_sha256')!=language_grader_digest():raise ValueError('Checkpoint grader differs')
    state['_saved_unix']=state.get('checkpoint_unix',path.stat().st_mtime)
    return state


def next_stage(record):
    if record['status'] in ('accepted','failed'):return None
    attempt=record['attempt']
    invoked=[c for c in record['calls'] if c['attempt']==attempt]
    if any(c['status']!='completed' for c in invoked):raise ValueError('Unreconciled call cannot be admitted again')
    if any(c['role']=='reviewer' for c in invoked):raise ValueError('Completed review must determine next attempt')
    return 'reviewer' if any(c['role']=='extractor' for c in invoked) else 'extractor'


def restore_records(plan,previous,records,pair):
    """Validate every complete producer and reconcile interrupted invocation once.

    Calls with no exact completed receipt become terminal unknown failures. An
    uninvoked quota waiter resumes its next stage. The frozen roles stay unchanged.
    Wall budget includes server downtime; active budget excludes no-process downtime.
    """
    from catalog_json.staged import role_contract,validate_role_receipt
    from catalog_json.provenance import artifact_origin
    from catalog_json.schema import PageContent,Review
    old={r['case_id']:r for r in previous['cases']}
    if set(old)!=set(records):raise ValueError('Checkpoint selected cases differ')
    downtime=max(0,time.time()-previous['_saved_unix'])
    for cid,(case,record,work) in records.items():
        retained=old[cid]
        if retained['physical_page']!=case['page'] or retained['source_sha256']!=case['source_sha256']:raise ValueError('Checkpoint source differs')
        record.clear();record.update(retained)
        native=work/f"page-{case['page']:04d}"
        for call in record['calls']:
            role=call['role'];attempt=call['attempt']
            target=native/(f'candidate-{attempt}.json' if role=='extractor' else f'review-{attempt}.json')
            if call['status']=='completed':
                origin=artifact_origin(native,target,case['source_sha256'],case['page'],attempt,role,getattr(pair,role),role_contract(pair,role))
                if origin['status']!='receipt_verified' or origin!=call['producer'] or origin['program']!=pair.role_runtimes[role]['program']:raise ValueError('Checkpoint complete producer differs')
                continue
            if call['status']!='running':continue
            matches=[]
            used={c.get('producer',{}).get('receipt') for c in record['calls'] if c['status']=='completed'}
            for result_path in native.glob('calls/*/result.json'):
                relative=str(result_path.relative_to(native))
                if relative in used:continue
                completed=json.loads(result_path.read_text())
                if completed.get('status')!='completed':continue
                execution=completed.get('execution',{})
                if execution.get('role')!=role or execution.get('attempt')!=attempt or execution.get('started_at',0)<call['started_unix']:continue
                validate_role_receipt(completed,native,target,case['source_sha256'],case['page'],attempt,role,getattr(pair,role),role_contract(pair,role),pair.role_runtimes[role]['program'])
                matches.append(completed)
            if len(matches)>1:raise ValueError('Multiple receipts for interrupted invocation')
            call['native_call_paths']=[str(p) for p in native.glob('calls/*') if p.stat().st_mtime>=call['started_unix']]
            if not matches:
                call.update(status='failed',error='Server restart interrupted invocation; no completed native receipt; external outcome unknown; no replay',elapsed_seconds=max(0,previous['_saved_unix']-call['started_unix']),elapsed_is_checkpoint_lower_bound=True,native_end_unknown=True)
                record['errors'].append({'role':role,'attempt':attempt,'error':call['error'],'time':time.time()});record['status']='failed';record['elapsed_seconds']+=call['elapsed_seconds']
                continue
            artifact=(PageContent if role=='extractor' else Review).model_validate(matches[0]['artifact'])
            origin=artifact_origin(native,target,case['source_sha256'],case['page'],attempt,role,getattr(pair,role),role_contract(pair,role))
            call.update(status='completed',producer=origin,reconciled_completed_receipt=True,elapsed_seconds=max(0,origin['finished_at']-call['started_unix']));record['elapsed_seconds']+=call['elapsed_seconds']
            if role=='extractor':record.update(candidate=str(target),candidate_sha256=digest(target),status='awaiting_review')
            else:
                record.update(review=str(target),review_sha256=digest(target))
                candidate=PageContent.model_validate_json(Path(record['candidate']).read_text())
                if artifact.accepts(candidate):record['status']='accepted'
                else:record.update(status='needs_review',attempt=attempt+1)
        indexed={Path(p) for c in record['calls'] for p in c.get('native_call_paths',[])}
        indexed.update(native/Path(c['producer']['receipt']).parent for c in record['calls'] if c.get('producer'))
        if set(native.glob('calls/*'))-indexed:raise ValueError('Unindexed native invocation: retain unknown outcome without replay')
        next_stage(record)
    return downtime


async def round_run(plan,number,gates):
    from catalog_json.agents import AgentPair
    from catalog_json.staged import isolated_call,load_role_runtimes,role_contract,RATE_LIMIT,validate_role_receipt
    from catalog_json.provenance import artifact_origin,program_version
    from catalog_json.schema import PageContent,Review
    check_pins(plan)
    out=Path(plan['output'])/f'round-{number}'
    previous=load_checkpoint(plan,number)
    if previous is None:out.mkdir(parents=True,exist_ok=False)
    pair=AgentPair(Path(plan['config']),plan['extractor'],plan['reviewer'],timeout=1200,max_tokens=16384)
    load_role_runtimes(pair,plan['role_runtimes'])
    pair.rate_limit_observer=lambda role:gates[role].rate_limited()
    extraction=asyncio.PriorityQueue();review=asyncio.Queue();records={};start=time.monotonic();budget=ActiveBudget();seq=0;active_native=0;drain_reason=None;scorer_digest=language_grader_digest()
    for case in plan['cases']:
        work=out/case['id'];work.mkdir(exist_ok=previous is not None)
        record={'case_id':case['id'],'physical_page':case['page'],'source_sha256':case['source_sha256'],'status':'pending','attempt':0,'calls':[],'errors':[],'elapsed_seconds':0}
        records[case['id']]=(case,record,work)
        if previous is None:extraction.put_nowait((0,seq,case['id']));seq+=1
    restoration_downtime=0
    if previous is not None:
        restoration_downtime=restore_records(plan,previous,records,pair)
        start-=previous['elapsed_seconds']+restoration_downtime
        budget.started-=previous['active_budget_seconds']+previous['quota_hold_seconds']
        budget.paused_total=previous['quota_hold_seconds']
        for role,gate in gates.items():gate.restore(previous['provider_pacing'][role],restoration_downtime)
        for case,record,_ in records.values():
            stage=next_stage(record)
            if stage=='extractor':extraction.put_nowait((0 if record['attempt']==0 else 1,seq,case['id']));seq+=1
            elif stage=='reviewer':review.put_nowait(case['id'])
    def admission_reason():
        nonlocal drain_reason
        if drain_reason:return drain_reason
        stop=external_stop(plan)
        if stop:drain_reason='operator:'+stop
        elif budget.elapsed()>=plan['round_deadline_seconds']:drain_reason='active_budget_expired'
        elif time.monotonic()-start>=plan.get('round_wall_maximum_seconds',28800):drain_reason='wall_window_expired'
        return drain_reason
    def snapshot():
        state={'checkpoint_unix':time.time(),'checkpoint_controller_version':CONTROLLER_VERSION,'restoration_downtime_seconds':restoration_downtime+(previous.get('restoration_downtime_seconds',0) if previous else 0),'runner_component_version':RUNNER_VERSION,'primary_grader_release':'0.3.2','primary_grader_sha256':scorer_digest,'owned_native_calls_active':active_native,'admission_closed_reason':drain_reason,'round':number,'complete':all(r['status']=='accepted' for _,r,_ in records.values()) and drain_reason is None,'elapsed_seconds':round(time.monotonic()-start,3),'active_budget_seconds':round(budget.elapsed(),3),'quota_hold_seconds':round(budget.held(),3),'runner_program':program_version(),'roles':{k:{'program':v['program'],'contract_sha256':v['contract_sha256']} for k,v in pair.role_runtimes.items()},'provider_pacing':{k:g.snapshot() for k,g in gates.items()},'cases':[r for _,r,_ in records.values()]}
        write_json(out/'round.json',state);return state
    async def worker(role):
        nonlocal seq,active_native
        queue=extraction if role=='extractor' else review
        while True:
            task=await queue.get();cid=task[2] if role=='extractor' else task
            case,record,work=records[cid];attempt=record['attempt'];began=time.monotonic();call_record=None;native_started=False;nativework=work/f"page-{case['page']:04d}";before_calls=set(nativework.glob('calls/*'))
            try:
                if admission_reason():raise AdmissionClosed(drain_reason)
                record['status']='extracting' if role=='extractor' else 'reviewing';snapshot()
                await wait_neighbor_pacing(plan['neighbor_batch'],plan['providers'][role],plan.get('neighbor_holds'),getattr(pair,role),budget,admission_reason)
                async with gates[role]:
                    # Own gate waits can outlast a neighbor's new hold. Recheck
                    # immediately before every native admission, including repairs.
                    await wait_neighbor_pacing(plan['neighbor_batch'],plan['providers'][role],plan.get('neighbor_holds'),getattr(pair,role),budget,admission_reason)
                    if admission_reason():raise AdmissionClosed(drain_reason)
                    check_pins(plan)
                    active_native+=1;native_started=True
                    call_record={'role':role,'attempt':attempt,'status':'running','started_unix':time.time()};record['calls'].append(call_record);snapshot()
                    try:artifact=await isolated_call(pair,role,Path(case['source']),work,case['page'],attempt)
                    except Exception:
                        # Reconcile an exact completed native receipt before
                        # declaring failure; never invoke the model twice.
                        artifact=None
                        target=work/f"page-{case['page']:04d}"/(f'candidate-{attempt}.json' if role=='extractor' else f'review-{attempt}.json')
                        for call_path in set(nativework.glob('calls/*'))-before_calls:
                            result_path=call_path/'result.json'
                            if not result_path.exists():continue
                            completed=json.loads(result_path.read_text())
                            if completed.get('status')!='completed':continue
                            validate_role_receipt(completed,target.parent,target,case['source_sha256'],case['page'],attempt,role,getattr(pair,role),role_contract(pair,role),pair.role_runtimes[role]['program'])
                            artifact=(PageContent if role=='extractor' else Review).model_validate(completed['artifact']);call_record['reconciled_completed_receipt']=True;break
                        if artifact is None:raise
                await gates[role].succeeded()
                artifact_path=work/f"page-{case['page']:04d}"/(f'candidate-{attempt}.json' if role=='extractor' else f'review-{attempt}.json')
                origin=artifact_origin(artifact_path.parent,artifact_path,case['source_sha256'],case['page'],attempt,role,getattr(pair,role),role_contract(pair,role))
                if origin['status']!='receipt_verified':raise ValueError('Missing native saved-artifact receipt')
                call_record.update(status='completed',producer=origin)
                if role=='extractor':
                    record.update(candidate=str(artifact_path),candidate_sha256=digest(artifact_path),status='awaiting_review');review.put_nowait(cid)
                else:
                    record.update(review=str(artifact_path),review_sha256=digest(artifact_path))
                    candidate=PageContent.model_validate_json(Path(record['candidate']).read_text())
                    if artifact.accepts(candidate):record['status']='accepted'
                    else:
                        record.update(status='needs_review',attempt=attempt+1);extraction.put_nowait((1,seq,cid));seq+=1
            except AdmissionClosed:
                record['status']='deferred_without_new_call'
                return
            except asyncio.CancelledError:
                record['status']='checkpointed'
                if call_record is not None:call_record['status']='cancelled_owned_call'
                raise
            except Exception as exc:
                record['errors'].append({'role':role,'attempt':attempt,'error':f'{type(exc).__name__}: {exc}','time':time.time()})
                if RATE_LIMIT.search(str(exc)):await gates[role].rate_limited()
                # No ambiguous call replay. Native isolated_call already captured
                # and cleaned its owned process tree; failed artifacts are kept.
                record['status']='failed'
                if call_record is not None:call_record.update(status='failed',error=record['errors'][-1]['error'])
            finally:
                if native_started:active_native-=1
                elapsed=round(time.monotonic()-began,3);record['elapsed_seconds']+=elapsed
                if call_record is not None:call_record.update(elapsed_seconds=elapsed,native_call_paths=[str(p) for p in sorted(set(nativework.glob('calls/*'))-before_calls)])
                queue.task_done();snapshot()
    workers=[asyncio.create_task(worker(role)) for role in gates]
    try:
        while not all(r['status'] in ('accepted','failed') for _,r,_ in records.values()):
            admission_reason()
            if drain_reason and active_native==0:break
            snapshot();await asyncio.sleep(plan.get('poll_seconds',1))
    finally:
        for worker_task in workers:worker_task.cancel()
        await asyncio.gather(*workers,return_exceptions=True)
    admission_reason()
    state=snapshot();engineering_correct=drawing_correct=draft_correct=first_pass_correct=draft_engineering_correct=draft_drawing_correct=first_pass_engineering_correct=first_pass_drawing_correct=0;draft_pages=first_pass_pages=0;scored=[]
    for case,r,_ in records.values():
        result={'case_id':case['id'],'status':r['status'],'engineering_correct':0,'engineering_expected':case['engineering_expected'],'drawing_correct':0,'drawing_expected':case['drawing_expected']}
        # Production acceptance gates delivery accuracy; drafts are retained and
        # independently scored separately, never silently counted as delivery.
        if r.get('candidate'):
            score=score_file(case['fixture'],r['candidate']);write_json(out/(case['id']+'-score.json'),score)
            result['draft_engineering_correct']=score['engineering_facts']['correct'];result['draft_drawing_correct']=score['drawing_assertions']['correct'];draft_correct+=result['draft_engineering_correct']+result['draft_drawing_correct'];draft_engineering_correct+=result['draft_engineering_correct'];draft_drawing_correct+=result['draft_drawing_correct'];draft_pages+=1
            if r['status']=='accepted':result.update(engineering_correct=score['engineering_facts']['correct'],drawing_correct=score['drawing_assertions']['correct'])
        initial_call=next((c for c in r['calls'] if c['role']=='extractor' and c['attempt']==0 and c['status']=='completed'),None)
        if initial_call:
            first_path=records[case['id']][2]/f"page-{case['page']:04d}"/'candidate-0.json'
            initial_score=score_file(case['fixture'],first_path);write_json(out/(case['id']+'-first-pass-score.json'),initial_score)
            result['first_pass_engineering_correct']=initial_score['engineering_facts']['correct'];result['first_pass_drawing_correct']=initial_score['drawing_assertions']['correct'];result['first_pass_correct']=result['first_pass_engineering_correct']+result['first_pass_drawing_correct'];first_pass_engineering_correct+=result['first_pass_engineering_correct'];first_pass_drawing_correct+=result['first_pass_drawing_correct'];first_pass_correct+=result['first_pass_correct'];first_pass_pages+=1
        engineering_correct+=result['engineering_correct'];drawing_correct+=result['drawing_correct'];scored.append(result)
    denominator=sum(c['engineering_expected']+c['drawing_expected'] for c in plan['cases'])
    report={'grader_release':'0.3.2','grader_sha256':language_grader_digest(),'runner_component_version':RUNNER_VERSION,'window_expired':drain_reason in ('active_budget_expired','wall_window_expired'),'operator_stopped':bool(drain_reason and drain_reason.startswith('operator:')),'drain_reason':drain_reason,'natural_native_drain':True,'round':number,'complete':state['complete'],'all_pages_attempted':all(any(c['role']=='extractor' for c in r['calls']) for _,r,_ in records.values()),'draft_correct':draft_correct,'draft_engineering_correct':draft_engineering_correct,'draft_drawing_correct':draft_drawing_correct,'first_pass_engineering_correct':first_pass_engineering_correct,'first_pass_drawing_correct':first_pass_drawing_correct,'draft_pages':draft_pages,'draft_percent_with_missing_zero':round(100*draft_correct/denominator,2),'first_pass_correct':first_pass_correct,'first_pass_pages':first_pass_pages,'first_pass_percent_with_missing_zero':round(100*first_pass_correct/denominator,2),'engineering_correct':engineering_correct,'engineering_expected':sum(c['engineering_expected'] for c in plan['cases']),'drawing_correct':drawing_correct,'drawing_expected':sum(c['drawing_expected'] for c in plan['cases']),'correct':engineering_correct+drawing_correct,'expected':denominator,'percent':round(100*(engineering_correct+drawing_correct)/denominator,2),'accepted_pages':sum(r['status']=='accepted' for _,r,_ in records.values()),'selected_pages':len(records),'elapsed_seconds':state['elapsed_seconds'],'active_budget_seconds':state['active_budget_seconds'],'quota_hold_seconds':state['quota_hold_seconds'],'cases':scored,'full_page_accuracy':False}
    write_json(out/'report.json',report);return report


async def run(plan):
    from catalog_json.staged import ProviderGate
    check_pins(plan);wall_started=time.time()
    restore_path=Path(plan['output'])/'summary.json'
    saved_summary=json.loads(restore_path.read_text()) if restore_path.exists() else None
    while time.time()<plan.get('not_before_unix',0):
        if external_stop(plan):break
        write_json(Path(plan['output'])/'admission.json',{'status':'provider_quota_hold','started_unix':wall_started,'reset_unix':plan['not_before_unix'],'remaining_seconds':round(plan['not_before_unix']-time.time(),3),'round_work_budget_started':False})
        await asyncio.sleep(min(30,plan['not_before_unix']-time.time()))
    gates={r:ProviderGate(1,30,1) for r in ['extractor','reviewer']};reports=[]
    for number in range(1,4):
        if external_stop(plan):break
        report_path=Path(plan['output'])/f'round-{number}'/'report.json'
        if report_path.exists():
            reports.append(json.loads(report_path.read_text()))
            snapshot_path=report_path.parent/'round.json'
            old=json.loads(snapshot_path.read_text())
            for role,gate in gates.items():gate.restore(old['provider_pacing'][role],max(0,time.time()-snapshot_path.stat().st_mtime))
        else:reports.append(await round_run(plan,number,gates))
        percents=[100*r['correct']/r['expected'] for r in reports]
        distributions={}
        for stage,prefix in [('accepted_delivery',''),('available_draft','draft_'),('first_pass','first_pass_')]:
            for metric,field,denom in [('engineering',prefix+'engineering_correct',sum(c['engineering_expected'] for c in plan['cases'])),('drawing',prefix+'drawing_correct',sum(c['drawing_expected'] for c in plan['cases'])),('combined','correct' if not prefix else prefix+'correct',sum(c['engineering_expected']+c['drawing_expected'] for c in plan['cases']))]:
                xs=[100*r[field]/denom for r in reports];distributions[stage+'_'+metric]={'expected_per_round':denom,'correct_per_round':[r[field] for r in reports],'rounds':len(xs),'mean_percent':statistics.mean(xs),'minimum_percent':min(xs),'maximum_percent':max(xs),'sample_sd_pp':statistics.stdev(xs) if len(xs)>1 else None}
        write_json(Path(plan['output'])/'summary.json',{'primary_grader_release':'0.3.2','primary_grader_sha256':language_grader_digest(),'runner_component_version':RUNNER_VERSION,'percentage_distributions_from_unrounded_counts':True,'stage_distributions':distributions,'operator_stopped':bool(external_stop(plan)) or any(r['operator_stopped'] for r in reports),'rounds_finished':len(reports)==3,'complete':len(reports)==3 and all(r['complete'] for r in reports),'all_pages_attempted':len(reports)==3 and all(r['all_pages_attempted'] for r in reports),'wall_elapsed_seconds':round(sum(r['elapsed_seconds'] for r in reports)+max(0,plan.get('not_before_unix',0)-wall_started),3),'initial_quota_wait_seconds':max(0,plan.get('not_before_unix',0)-wall_started),'rounds':reports,'mean_percent':statistics.mean(percents),'minimum_percent':min(percents),'maximum_percent':max(percents),'sample_standard_deviation_pp':statistics.stdev(percents) if len(percents)>1 else None,'method':'three fresh sequential native mixed-role rounds, unchanged inputs; nonaccepted/failed delivery facts zero; weighted selected facts + scoped drawing assertions','provider_pacing':{r:g.snapshot() for r,g in gates.items()},'full_page_accuracy':False})
        if reports[-1]['operator_stopped']:break
    if not reports:
        write_json(Path(plan['output'])/'summary.json',{'primary_grader_release':'0.3.2','primary_grader_sha256':language_grader_digest(),'runner_component_version':RUNNER_VERSION,'rounds_finished':False,'complete':False,'all_pages_attempted':False,'operator_stopped':bool(external_stop(plan)),'rounds':[],'wall_elapsed_seconds':round(sum(r['elapsed_seconds'] for r in reports)+max(0,plan.get('not_before_unix',0)-wall_started),3)})
    return reports


def main():
    plan=json.loads(Path(sys.argv[1]).read_text());asyncio.run(run(plan))
    summary=json.loads((Path(plan['output'])/'summary.json').read_text())
    raise SystemExit(0 if summary['complete'] else 2)


if __name__=='__main__':main()

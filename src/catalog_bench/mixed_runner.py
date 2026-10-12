"""Three sequential fresh rounds of pinned production native roles.

The extraction/review subprocesses never receive fixtures or scoring code. Gold is
read only after each round; failed/nonaccepted deliveries remain zero in accuracy.
One extra live call per provider; production catalogue jobs are read-only neighbors.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time
from .io import write_json
from .benchmark import score_file


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


async def wait_neighbor_pacing(path,provider,hold_path=None,model=None,budget=None):
    """Honor a fresh neighbor cooldown, without resetting/replaying its work."""
    while True:
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


async def round_run(plan,number,gates):
    from catalog_json.agents import AgentPair
    from catalog_json.staged import isolated_call,load_role_runtimes,role_contract,RATE_LIMIT,validate_role_receipt
    from catalog_json.provenance import artifact_origin,program_version
    from catalog_json.schema import PageContent,Review
    check_pins(plan)
    out=Path(plan['output'])/f'round-{number}';out.mkdir(parents=True,exist_ok=False)
    pair=AgentPair(Path(plan['config']),plan['extractor'],plan['reviewer'],timeout=1200,max_tokens=16384)
    load_role_runtimes(pair,plan['role_runtimes'])
    pair.rate_limit_observer=lambda role:gates[role].rate_limited()
    extraction=asyncio.PriorityQueue();review=asyncio.Queue();records={};start=time.monotonic();budget=ActiveBudget();seq=0
    for case in plan['cases']:
        work=out/case['id'];work.mkdir()
        record={'case_id':case['id'],'physical_page':case['page'],'source_sha256':case['source_sha256'],'status':'pending','attempt':0,'calls':[],'errors':[],'elapsed_seconds':0}
        records[case['id']]=(case,record,work);extraction.put_nowait((0,seq,case['id']));seq+=1
    def snapshot():
        state={'round':number,'complete':all(r['status']=='accepted' for _,r,_ in records.values()),'elapsed_seconds':round(time.monotonic()-start,3),'active_budget_seconds':round(budget.elapsed(),3),'quota_hold_seconds':round(budget.held(),3),'runner_program':program_version(),'roles':{k:{'program':v['program'],'contract_sha256':v['contract_sha256']} for k,v in pair.role_runtimes.items()},'provider_pacing':{k:g.snapshot() for k,g in gates.items()},'cases':[r for _,r,_ in records.values()]}
        write_json(out/'round.json',state);return state
    async def worker(role):
        nonlocal seq
        queue=extraction if role=='extractor' else review
        while True:
            task=await queue.get();cid=task[2] if role=='extractor' else task
            case,record,work=records[cid];attempt=record['attempt'];began=time.monotonic();call_record=None;nativework=work/f"page-{case['page']:04d}";before_calls=set(nativework.glob('calls/*'))
            try:
                record['status']='extracting' if role=='extractor' else 'reviewing';snapshot()
                await wait_neighbor_pacing(plan['neighbor_batch'],plan['providers'][role],plan.get('neighbor_holds'),getattr(pair,role),budget)
                async with gates[role]:
                    check_pins(plan)
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
                elapsed=round(time.monotonic()-began,3);record['elapsed_seconds']+=elapsed
                if call_record is not None:call_record.update(elapsed_seconds=elapsed,native_call_paths=[str(p) for p in sorted(set(nativework.glob('calls/*'))-before_calls)])
                queue.task_done();snapshot()
    workers=[asyncio.create_task(worker(role)) for role in gates]
    try:
        while not all(r['status'] in ('accepted','failed') for _,r,_ in records.values()):
            if budget.elapsed()>=plan['round_deadline_seconds'] or time.monotonic()-start>=plan.get('round_wall_maximum_seconds',86400):break
            snapshot();await asyncio.sleep(1)
    finally:
        for worker_task in workers:worker_task.cancel()
        await asyncio.gather(*workers,return_exceptions=True)
    state=snapshot();engineering_correct=drawing_correct=draft_correct=first_pass_correct=0;draft_pages=first_pass_pages=0;scored=[]
    for case,r,_ in records.values():
        result={'case_id':case['id'],'status':r['status'],'engineering_correct':0,'engineering_expected':case['engineering_expected'],'drawing_correct':0,'drawing_expected':case['drawing_expected']}
        # Production acceptance gates delivery accuracy; drafts are retained and
        # independently scored separately, never silently counted as delivery.
        if r.get('candidate'):
            score=score_file(case['fixture'],r['candidate']);write_json(out/(case['id']+'-score.json'),score)
            result['draft_engineering_correct']=score['engineering_facts']['correct'];result['draft_drawing_correct']=score['drawing_assertions']['correct'];draft_correct+=result['draft_engineering_correct']+result['draft_drawing_correct'];draft_pages+=1
            if r['status']=='accepted':result.update(engineering_correct=score['engineering_facts']['correct'],drawing_correct=score['drawing_assertions']['correct'])
        initial_call=next((c for c in r['calls'] if c['role']=='extractor' and c['attempt']==0 and c['status']=='completed'),None)
        if initial_call:
            first_path=records[case['id']][2]/f"page-{case['page']:04d}"/'candidate-0.json'
            initial_score=score_file(case['fixture'],first_path);write_json(out/(case['id']+'-first-pass-score.json'),initial_score)
            result['first_pass_correct']=initial_score['engineering_facts']['correct']+initial_score['drawing_assertions']['correct'];first_pass_correct+=result['first_pass_correct'];first_pass_pages+=1
        engineering_correct+=result['engineering_correct'];drawing_correct+=result['drawing_correct'];scored.append(result)
    denominator=sum(c['engineering_expected']+c['drawing_expected'] for c in plan['cases'])
    report={'round':number,'complete':state['complete'],'all_pages_attempted':all(any(c['role']=='extractor' for c in r['calls']) for _,r,_ in records.values()),'draft_correct':draft_correct,'draft_pages':draft_pages,'draft_percent_with_missing_zero':round(100*draft_correct/denominator,2),'first_pass_correct':first_pass_correct,'first_pass_pages':first_pass_pages,'first_pass_percent_with_missing_zero':round(100*first_pass_correct/denominator,2),'engineering_correct':engineering_correct,'engineering_expected':sum(c['engineering_expected'] for c in plan['cases']),'drawing_correct':drawing_correct,'drawing_expected':sum(c['drawing_expected'] for c in plan['cases']),'correct':engineering_correct+drawing_correct,'expected':denominator,'percent':round(100*(engineering_correct+drawing_correct)/denominator,2),'accepted_pages':sum(r['status']=='accepted' for _,r,_ in records.values()),'selected_pages':len(records),'elapsed_seconds':state['elapsed_seconds'],'active_budget_seconds':state['active_budget_seconds'],'quota_hold_seconds':state['quota_hold_seconds'],'cases':scored,'full_page_accuracy':False}
    write_json(out/'report.json',report);return report


async def run(plan):
    from catalog_json.staged import ProviderGate
    check_pins(plan);wall_started=time.time()
    while time.time()<plan.get('not_before_unix',0):
        write_json(Path(plan['output'])/'admission.json',{'status':'provider_quota_hold','started_unix':wall_started,'reset_unix':plan['not_before_unix'],'remaining_seconds':round(plan['not_before_unix']-time.time(),3),'round_work_budget_started':False})
        await asyncio.sleep(min(30,plan['not_before_unix']-time.time()))
    gates={r:ProviderGate(1,30,1) for r in ['extractor','reviewer']};reports=[]
    for number in range(1,4):
        reports.append(await round_run(plan,number,gates))
        percents=[r['percent'] for r in reports]
        write_json(Path(plan['output'])/'summary.json',{'rounds_finished':len(reports)==3,'complete':len(reports)==3 and all(r['complete'] for r in reports),'all_pages_attempted':len(reports)==3 and all(r['all_pages_attempted'] for r in reports),'wall_elapsed_seconds':round(time.time()-wall_started,3),'initial_quota_wait_seconds':max(0,plan.get('not_before_unix',0)-wall_started),'rounds':reports,'mean_percent':statistics.mean(percents),'minimum_percent':min(percents),'maximum_percent':max(percents),'sample_standard_deviation_pp':statistics.stdev(percents) if len(percents)>1 else None,'method':'three fresh sequential native mixed-role rounds, unchanged inputs; nonaccepted/failed delivery facts zero; weighted selected facts + scoped drawing assertions','provider_pacing':{r:g.snapshot() for r,g in gates.items()},'full_page_accuracy':False})
    return reports


def main():
    plan=json.loads(Path(sys.argv[1]).read_text());asyncio.run(run(plan))
    summary=json.loads((Path(plan['output'])/'summary.json').read_text())
    raise SystemExit(0 if summary['complete'] else 2)


if __name__=='__main__':main()

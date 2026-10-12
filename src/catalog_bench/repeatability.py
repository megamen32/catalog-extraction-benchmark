"""Frozen first-pass rounds with bounded adaptive concurrency and retained failures."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import time

from .bench_runner import run_suite, sha
from .io import write_json


RATE_LIMIT=re.compile(r'RateLimitError|rate_limit_exceeded|429[^\n]{0,100}(?:Too Many|rate.?limit)|(?:status|HTTP)[^\n]{0,60}\b429\b',re.I)


def round_summary(records,expected_by_case):
    """Missing/failed outputs stay in the same fixed denominator."""
    correct=0;expected=sum(expected_by_case.values());times=[]
    for record in records:
        correct+=record.get('score',{}).get('engineering_facts',{}).get('correct',0) if record['status']=='completed' else 0
        if record.get('elapsed_seconds') is not None:times.append(record['elapsed_seconds'])
    return {'correct':correct,'expected':expected,'percent':100*correct/expected,
            'completed_pages':sum(r['status']=='completed' for r in records),'expected_pages':len(expected_by_case),
            'elapsed_seconds_sum':sum(times),'time_measurement':'sum of per-attempt durations, not parallel wall duration',
            'statuses':{status:sum(r['status']==status for r in records) for status in sorted({r['status'] for r in records})}}


def distribution(values):
    return {'n':len(values),'mean':statistics.mean(values),'minimum':min(values),'maximum':max(values),
            'range':max(values)-min(values),'sample_standard_deviation':statistics.stdev(values) if len(values)>1 else None}


def validate_variant(variant,suite,initial=None):
    if sha(variant['suite'])!=variant['suite_sha256']:raise ValueError('Frozen suite changed')
    for filename,digest in variant['file_sha256'].items():
        if sha(filename)!=digest:raise ValueError('Frozen executable/config input changed')
    project=suite['projects'][0]
    if project['version']!=variant['declared_version'] or suite['models']!=[variant['model']]:raise ValueError('Frozen model/program selection changed')
    cases={c['id']:c for c in suite['cases']}
    if len(cases)!=len(suite['cases']):raise ValueError('Initial cohort case IDs must match exactly once')
    if initial is None:return
    if len({r['case_id'] for r in initial['runs']})!=len(initial['runs']) or {r['case_id'] for r in initial['runs']}!=set(cases):raise ValueError('Initial cohort case IDs must match exactly once')
    for record in initial['runs']:
        case=cases[record['case_id']]
        if record['source_sha256']!=sha(case['source']) or record['page']!=case['page'] or record['model']!=variant['model'] or record['project']!=project['id'] or record['stage']!=project['stage']:raise ValueError('Retained initial source/model/stage binding changed')
        if record['project_state']['declared_version']!=variant['declared_version']:raise ValueError('Retained declared version changed')
        if record['status']=='completed':
            actual=record['tested_program']
            if any(actual.get(k)!=variant[k] for k in ('package_version','git_revision','contract_sha256')):raise ValueError('Retained executed program version contradicts frozen selection')


def run(plan_file,output):
    plan_file=Path(plan_file).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    plan=json.loads(plan_file.read_text());started=time.monotonic();maximum=plan['max_concurrency']
    if not 1<=plan['initial_concurrency']<=maximum<=4:raise ValueError('Concurrency must stay in the measured finite budget, maximum4')
    if plan['rounds']<3:raise ValueError('At least3 complete rounds required')
    mode=plan.get('initial_mode','retained')
    if mode not in ('fresh','retained'):raise ValueError('Initial mode must be fresh or retained')
    fresh=mode=='fresh'
    if fresh and any('initial_results' in v or 'initial_sha256' in v for v in plan['variants']):raise ValueError('Fresh rounds cannot retain a historical initial cohort')
    ids=[v['id'] for v in plan['variants']]
    if len(ids)!=len(set(ids)) or set(ids)!=set(plan['expected_bindings']):raise ValueError('Unique variants and independent expected bindings are required')
    variants={};bindings={};expected={};rounds={};limit=plan['initial_concurrency'];history=[];good=0;cooldown=0
    for variant in plan['variants']:
        suite=json.loads(Path(variant['suite']).read_text());initial=None
        if not fresh:
            initial=json.loads(Path(variant['initial_results']).read_text())
            if sha(variant['initial_results'])!=variant['initial_sha256']:raise ValueError('Retained first round changed')
            if not initial['complete'] or len(initial['runs'])!=len(suite['cases']):raise ValueError('Initial round lacks a complete attempted cohort')
        if len(suite['projects'])!=1 or len(suite['models'])!=1 or suite['repeats']!=1:raise ValueError('Each frozen variant requires one project/model per round')
        if any(variant.get(k)!=v for k,v in plan['expected_bindings'][variant['id']].items()):raise ValueError('Variant contradicts independently recorded expected bindings')
        validate_variant(variant,suite,initial)
        bindings[variant['id']]=variant
        variants[variant['id']]=suite;rounds[variant['id']]=[] if fresh else [initial['runs']]
        records=suite['cases'] if fresh else initial['runs']
        for record in records:
            case_id=record['id'] if fresh else record['case_id']
            fixture=next(c['fixture'] for c in suite['cases'] if c['id']==case_id)
            golden=json.loads(Path(fixture).read_text())
            # A fresh series derives its denominator from the frozen independent annotations.
            count=sum(sum(len(row) for row in table['rows']) for table,_ in zip(golden.get('tables',[]),golden.get('semantic_columns',[])))+len(golden.get('selected_facts',[])) if fresh else record.get('score',{}).get('engineering_facts',{}).get('expected')
            if count is None:count=plan['expected_by_case'][case_id]
            if case_id in expected and expected[case_id]!=count:raise ValueError('Different fixed denominators')
            expected[case_id]=count
    if set(expected)!=set(plan['expected_by_case']) or expected!=plan['expected_by_case']:raise ValueError('Fixed denominator contradicts first round')
    def attempt(variant,case,round_number):
        work=output/f'round-{round_number}'/variant/case['id'];work.mkdir(parents=True,exist_ok=True)
        for filename,digest in bindings[variant]['file_sha256'].items():
            if sha(filename)!=digest:raise ValueError('Frozen runtime changed before attempt')
        manifest=work/'suite.json';single={**variants[variant],'cases':[case],'deadline_seconds':plan['attempt_maximum_seconds']}
        write_json(manifest,single)
        retained=work/'matrix/results.json'
        if retained.exists():
            result=json.loads(retained.read_text())
            if result.get('complete') and len(result['runs'])==1:
                record=result['runs'][0]
                if record['status']=='completed' and (not Path(record['artifact_path']).exists() or sha(record['artifact_path'])!=record['artifact_sha256']):raise ValueError('Retained output changed')
                return record,False
            raise ValueError('Interrupted attempt retained without replay; reconcile its receipt first')
        result=run_suite(manifest,work/'matrix')
        record=result['runs'][0]
        if record['status']=='completed' and any(record['tested_program'].get(k)!=bindings[variant][k] for k in ('package_version','git_revision','contract_sha256')):raise ValueError('Fresh execution contradicts frozen version')
        logs='\n'.join(p.read_text(errors='replace') for p in (work/'matrix').glob('*/process.log'))
        limited=bool(RATE_LIMIT.search(logs));record['rate_limit_observed']=limited
        return record,limited
    def snapshot(status):
        result={'status':status,'rounds_required':plan['rounds'],'initial_rounds_retained':not fresh,
                'concurrency_history':history,'variants':{},'whole_page_accuracy':False,'failed_attempts_in_denominator':True}
        for variant,cohorts in rounds.items():
            summaries=[round_summary(records,expected) for records in cohorts]
            full=[x['percent'] for x in summaries if x['expected_pages']==len(expected) and sum(x['statuses'].values())==len(expected)]
            result['variants'][variant]={'rounds':summaries,'distribution':distribution(full) if full else None,
                'per_case':{case:distribution([100*r.get('score',{}).get('engineering_facts',{}).get('correct',0)/expected[case] if r['status']=='completed' else 0 for rows in cohorts for r in rows if r['case_id']==case]) for case in expected if any(r['case_id']==case for rows in cohorts for r in rows)},
                'records':cohorts}
        write_json(output/'results.json',result)
    snapshot('running')
    with concurrent.futures.ThreadPoolExecutor(max_workers=maximum) as pool:
        for number in range(1 if fresh else 2,plan['rounds']+1):
            cases=list(next(iter(variants.values()))['cases']);random.Random(plan['random_seed']+number).shuffle(cases)
            pending=[(v,next(c for c in variants[v]['cases'] if c['id']==case['id'])) for case in cases for v in variants]
            for v in variants:rounds[v].append([])
            active={}
            while pending or active:
                if time.monotonic()-started>plan['deadline_seconds']:snapshot('deadline');return
                now=time.monotonic()
                while pending and len(active)<limit and now>=cooldown:
                    v,case=pending.pop(0);f=pool.submit(attempt,v,case,number);active[f]=(v,case)
                if not active:
                    time.sleep(min(1,max(.01,cooldown-time.monotonic())));continue
                done,_=concurrent.futures.wait(active,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
                for f in done:
                    v,case=active.pop(f);record,limited=f.result();rounds[v][-1].append(record)
                    if limited:
                        old=limit;limit=max(1,limit//2);good=0;cooldown=time.monotonic()+plan['rate_limit_cooldown_seconds']
                        history.append({'round':number,'case':case['id'],'reason':'provider_rate_limit','previous':old,'next':limit,'attempt_replayed':False})
                    elif record['status']=='completed':
                        good+=1
                        if good>=plan['successes_before_increase'] and limit<maximum:
                            old=limit;limit+=1;good=0;history.append({'round':number,'case':case['id'],'reason':'successful_attempts_within_budget','previous':old,'next':limit})
                    snapshot('running')
            # No round3 call starts before every round2 attempt is retained.
            snapshot('running')
    snapshot('completed')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.plan,a.output)

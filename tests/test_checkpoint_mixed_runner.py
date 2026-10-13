"""Focused integration: restart recovery without replay; expected 2s, max20s.

No provider requests. Detect reset budgets, duplicate initial calls, and forgotten
interrupted calls; the frozen native identities and graders remain unchanged.
"""
import asyncio
import json
import time
from pathlib import Path
import pytest
from catalog_bench import checkpoint_mixed_runner as runner
import test_corrected_mixed_runner as original


def test_next_stage_never_replays_recorded_failed_call():
    r=dict(status='reviewing',attempt=0,calls=[dict(role='reviewer',attempt=0,status='running')])
    with pytest.raises(ValueError):runner.next_stage(r)
    r['status']='failed'
    assert runner.next_stage(r) is None
    r=dict(status='extracting',attempt=1,calls=[dict(role='extractor',attempt=0,status='completed'),dict(role='reviewer',attempt=0,status='completed')])
    assert runner.next_stage(r)=='extractor'
    r['calls'].append(dict(role='extractor',attempt=1,status='completed'))
    assert runner.next_stage(r)=='reviewer'


def test_partial_directory_is_not_treated_as_fresh(tmp_path):
    p=original.plan(tmp_path)
    (Path(p['output'])/'round-1').mkdir(parents=True)
    with pytest.raises(FileNotFoundError):runner.load_checkpoint(p,1)


def test_changed_grader_rejected_before_calls(tmp_path):
    p=original.plan(tmp_path);d=Path(p['output'])/'round-1';d.mkdir(parents=True)
    (d/'round.json').write_text(json.dumps(dict(round=1,primary_grader_sha256='bad')))
    with pytest.raises(ValueError):runner.load_checkpoint(p,1)


def test_resume_only_uninvoked_stage_preserves_completed_initial(monkeypatch,tmp_path):
    monkeypatch.setattr(original,'mixed_runner',runner)
    trace=[];original.install(monkeypatch,trace)
    p=original.plan(tmp_path);p['cases']=p['cases'][1:]
    gates={r:original.Gate() for r in ('extractor','reviewer')}
    # Obtain the genuine runner snapshot layout using synthetic native tools.
    asyncio.run(runner.round_run(p,1,gates))
    out=Path(p['output'])/'round-1';state=json.loads((out/'round.json').read_text())
    state['cases'][0]['status']='awaiting_review'
    state['cases'][0]['calls']=state['cases'][0]['calls'][:1]
    # Simulate a review that was never admitted, not an invocation with lost metadata.
    import shutil
    shutil.rmtree(out/'case-2'/'page-0002'/'calls'/'reviewer-0')
    (out/'case-2'/'page-0002'/'review-0.json').unlink()
    # The already accepted neighbor is retained. Complete producer verification
    # remains a separate boundary and must run before the next native admission.
    import sys
    pair_cls=sys.modules['catalog_json.agents'].AgentPair
    native_program=pair_cls(None,'M3','GLMcoding').role_runtimes['extractor']['program']
    for c in state['cases']:
        for call in c['calls']:
            call['producer']['program']=native_program if call['role']=='extractor' else {'package_version':'1.4.17'}
            call['producer']['receipt']=f"calls/{call['role']}-{call['attempt']}/result.json"
    def origin(*args):return {'status':'receipt_verified','program':native_program if args[5]=='extractor' else {'package_version':'1.4.17'},'receipt':f'calls/{args[5]}-{args[4]}/result.json'}
    sys.modules['catalog_json.provenance'].artifact_origin=origin
    monkeypatch.setattr(original.Gate,'restore',lambda self,state,elapsed:None,raising=False)
    state['active_budget_seconds']=.2;state['quota_hold_seconds']=.3;state['elapsed_seconds']=.5
    state['checkpoint_unix']=time.time()-.05
    (out/'round.json').write_text(json.dumps(state));trace.clear()
    report=asyncio.run(runner.round_run(p,1,gates))
    assert trace==[('round-1','reviewer',2,0)]
    assert report['complete'] and report['first_pass_pages']==2
    restored=json.loads((out/'round.json').read_text())
    assert restored['active_budget_seconds']>=.2 and restored['quota_hold_seconds']==.3
    assert restored['elapsed_seconds']>=.55 and restored['restoration_downtime_seconds']>=.05


def test_interrupted_no_receipt_is_failed_unknown_not_replayed(monkeypatch,tmp_path):
    monkeypatch.setattr(original,'mixed_runner',runner);trace=[];original.install(monkeypatch,trace)
    from catalog_json.agents import AgentPair
    p=original.plan(tmp_path);p['cases']=p['cases'][:1];case=p['cases'][0]
    work=Path(p['output'])/'round-1'/case['id'];native=work/'page-0001';(native/'calls'/'interrupted').mkdir(parents=True)
    (native/'calls'/'interrupted'/'worker.log').write_text('')
    r=dict(case_id=case['id'],physical_page=1,source_sha256=case['source_sha256'],status='reviewing',attempt=0,calls=[dict(role='reviewer',attempt=0,status='running',started_unix=time.time()-1)],errors=[],elapsed_seconds=0)
    previous=dict(cases=[r],_saved_unix=time.time()-.1)
    records={case['id']:(case,{},work)}
    runner.restore_records(p,previous,records,AgentPair(None,'M3','GLMcoding'))
    got=records[case['id']][1]
    assert got['status']=='failed' and got['calls'][0]['native_end_unknown']
    assert got['calls'][0]['elapsed_is_checkpoint_lower_bound']
    assert runner.next_stage(got) is None and not trace

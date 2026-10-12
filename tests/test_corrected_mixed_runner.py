"""Focused integration: fresh native routing/round fairness, errors, cooldown and result gates.
Synthetic native calls only; expected3s maximum20s, no providers or full queue mutation.
"""
import asyncio,json,re,sys,types
from pathlib import Path
from catalog_bench import corrected_mixed_runner as mixed_runner

class Artifact:
    def __init__(self,accept=True):self.accept=accept
    def accepts(self,candidate):return self.accept
    @classmethod
    def model_validate_json(cls,text):return cls()
    @classmethod
    def model_validate(cls,data):return cls()

class Gate:
    def __init__(self,*args):self.signals=0
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass
    async def succeeded(self):pass
    async def rate_limited(self):self.signals+=1
    def snapshot(self):return {'signals':self.signals}


def install(monkeypatch,trace,fail=False,reconcile=False):
    class Pair:
        def __init__(self,config,extractor,reviewer,**kwargs):self.extractor=extractor;self.reviewer=reviewer;self.role_runtimes={r:dict(program={'package_version':v},contract_sha256=r) for r,v in [('extractor','1.4.15'),('reviewer','1.4.17')]}
    async def call(pair,role,source,out,page,attempt):
        # The tested role gets source/out/page/attempt only, no gold/audit paths.
        trace.append((out.parent.name,role,page,attempt));w=out/f'page-{page:04d}';w.mkdir(exist_ok=True);c=w/'calls'/f'{role}-{attempt}';c.mkdir(parents=True)
        await asyncio.sleep(.002)
        if fail and page==1 and role=='extractor':
            if reconcile:
                (w/f'candidate-{attempt}.json').write_text('{}');(c/'result.json').write_text(json.dumps({'status':'completed','artifact':{}}))
            raise RuntimeError('native provider failure')
        (w/(f'candidate-{attempt}.json' if role=='extractor' else f'review-{attempt}.json')).write_text('{}')
        return Artifact(accept=attempt>0 if page==1 else True)
    for name,module in {
      'catalog_json.agents':types.SimpleNamespace(AgentPair=Pair),
      'catalog_json.staged':types.SimpleNamespace(isolated_call=call,load_role_runtimes=lambda p,x:None,role_contract=lambda p,r:r,RATE_LIMIT=re.compile('429'),validate_role_receipt=lambda *a:None,ProviderGate=Gate),
      'catalog_json.provenance':types.SimpleNamespace(artifact_origin=lambda *a:{'status':'receipt_verified'},program_version=lambda:{'package_version':'1.4.11'}),
      'catalog_json.schema':types.SimpleNamespace(PageContent=Artifact,Review=Artifact)
    }.items():monkeypatch.setitem(sys.modules,name,module)
    monkeypatch.setattr(mixed_runner,'score_file',lambda f,c:{'engineering_facts':{'correct':1},'drawing_assertions':{'correct':1}})


def plan(tmp_path):
    neighbor=tmp_path/'neighbor.json';neighbor.write_text(json.dumps({'method':{'provider_pacing':{p:{'backoff_remaining_seconds':0} for p in ['anthropic','zai']}}}))
    return dict(poll_seconds=.005,file_sha256={},output=str(tmp_path/'rounds'),config='protectedconfig',role_runtimes='nativepins',extractor='M3',reviewer='GLMcoding',neighbor_batch=str(neighbor),providers={'extractor':'anthropic','reviewer':'zai'},round_deadline_seconds=2,cases=[dict(id=f'case-{p}',page=p,source='original.pdf',source_sha256='a'*64,fixture='gold-not-passed-to-worker',engineering_expected=1,drawing_expected=1) for p in [1,2,3]])


def test_three_rounds_are_fresh_sequential_and_first_passes_fair(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);asyncio.run(mixed_runner.run(p))
    summary=json.loads((Path(p['output'])/'summary.json').read_text());assert summary['complete'] and summary['rounds_finished']
    assert [r['round'] for r in summary['rounds']]==[1,2,3]
    for n in range(1,4):
        extracts=[(page,a) for rnd,role,page,a in trace if rnd==f'round-{n}' and role=='extractor']
        assert extracts==[(1,0),(2,0),(3,0),(1,1)]
        state=json.loads((Path(p['output'])/f'round-{n}'/'round.json').read_text());assert state['roles']['extractor']['program']['package_version']=='1.4.15';assert state['roles']['reviewer']['program']['package_version']=='1.4.17'
        assert not list((Path(p['output'])/f'round-{n}').rglob('external-audit.json'))
    assert [x[0] for x in trace]==sorted([x[0] for x in trace])


def test_unknown_native_error_is_retained_once_not_replayed(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace,fail=True);p=plan(tmp_path);asyncio.run(mixed_runner.run(p))
    summary=json.loads((Path(p['output'])/'summary.json').read_text());assert not summary['complete'] and summary['all_pages_attempted']
    assert [t for t in trace if t[2]==1]==[(f'round-{n}','extractor',1,0) for n in range(1,4)]
    assert all(r['accepted_pages']==2 and r['correct']==4 and r['expected']==6 for r in summary['rounds'])
    calls=json.loads((Path(p['output'])/'round-1'/'round.json').read_text())['cases'][0]['calls'];assert calls[0]['status']=='failed' and calls[0]['native_call_paths'] and calls[0]['elapsed_seconds']>=0


def test_changed_pin_blocks_calls(tmp_path):
    f=tmp_path/'native.py';f.write_text('new');p=plan(tmp_path);p['file_sha256']={str(f):'0'*64}
    try:mixed_runner.check_pins(p)
    except ValueError:pass
    else:raise AssertionError('changed native input allowed')

def test_quota_hold_excludes_active_budget_and_checks_model(tmp_path):
    p=plan(tmp_path);hold=tmp_path/'holds.json';hold.write_text(json.dumps({'providers':{'anthropic':{'model':'M3','not_before_unix':__import__('time').time()+.02}}}))
    budget=mixed_runner.ActiveBudget()
    asyncio.run(mixed_runner.wait_neighbor_pacing(p['neighbor_batch'],'anthropic',str(hold),'M3',budget))
    assert budget.held()>=.015 and budget.elapsed()<.02
    try:asyncio.run(mixed_runner.wait_neighbor_pacing(p['neighbor_batch'],'anthropic',str(hold),'WRONG',budget))
    except ValueError:pass
    else:raise AssertionError('quota model mismatch ignored')


def test_completed_native_receipt_reconciles_actual_page_calls_directory(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace,fail=True,reconcile=True);p=plan(tmp_path)
    asyncio.run(mixed_runner.round_run(p,1,{'extractor':Gate(),'reviewer':Gate()}))
    state=json.loads((Path(p['output'])/'round-1'/'round.json').read_text());calls=state['cases'][0]['calls']
    assert calls[0]['reconciled_completed_receipt'] is True
    assert all('/page-0001/calls/' in path for path in calls[0]['native_call_paths'])
    assert [x for x in trace if x[1]=='extractor' and x[2]==1]==[('round-1','extractor',1,0),('round-1','extractor',1,1)]


def test_operator_stop_drains_owned_native_call_without_starting_review(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);stop=tmp_path/'stop.json';p['admission_stop_file']=str(stop)
    old=sys.modules['catalog_json.staged'].isolated_call
    async def call(*args):
        stop.write_text(json.dumps({'stop_new_calls':True,'reason':'switch profile'}))
        await asyncio.sleep(.04)
        return await old(*args)
    sys.modules['catalog_json.staged'].isolated_call=call
    asyncio.run(mixed_runner.run(p));summary=json.loads((Path(p['output'])/'summary.json').read_text())
    assert len(trace)==1 and trace[0][1]=='extractor'
    assert not summary['rounds_finished'] and summary['operator_stopped']
    state=json.loads((Path(p['output'])/'round-1'/'round.json').read_text());c=state['cases'][0]['calls'][0]
    assert c['status']=='completed' and state['owned_native_calls_active']==0
    assert not list((Path(p['output'])/'round-2').glob('*'))


def test_work_deadline_stops_admission_then_finishes_existing_call(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);p['round_deadline_seconds']=.01
    old=sys.modules['catalog_json.staged'].isolated_call
    async def call(*args):
        await asyncio.sleep(.04)
        return await old(*args)
    sys.modules['catalog_json.staged'].isolated_call=call
    result=asyncio.run(mixed_runner.round_run(p,1,{'extractor':Gate(),'reviewer':Gate()}))
    assert result['window_expired'] and not result['complete'] and len(trace)==1
    state=json.loads((Path(p['output'])/'round-1'/'round.json').read_text());assert state['cases'][0]['calls'][0]['status']=='completed'
    assert state['cases'][0]['calls'][0]['elapsed_seconds']>=.04
    assert result['grader_release']=='0.3.2' and result['first_pass_pages']==1


def test_neighbor_hold_is_rechecked_after_own_gate(monkeypatch,tmp_path):
    import time
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);p['cases']=p['cases'][:1];hold=tmp_path/'holds.json';p['neighbor_holds']=str(hold);hold.write_text(json.dumps({'providers':{}}));ends=[]
    class MutatingGate(Gate):
        async def __aenter__(self):
            until=time.time()+.03;ends.append(until);hold.write_text(json.dumps({'providers':{'anthropic':{'model':'M3','not_before_unix':until}}}));return self
    old=sys.modules['catalog_json.staged'].isolated_call
    async def call(*args):
        if args[1]=='extractor':assert time.time()>=ends[-1]
        return await old(*args)
    sys.modules['catalog_json.staged'].isolated_call=call
    asyncio.run(mixed_runner.round_run(p,1,{'extractor':MutatingGate(),'reviewer':Gate()}))
    assert trace and trace[0][1]=='extractor'


def test_stop_before_initial_quota_hold_writes_incomplete_summary(monkeypatch,tmp_path):
    import time
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);p['not_before_unix']=time.time()+100
    stop=tmp_path/'stop.json';p['admission_stop_file']=str(stop);stop.write_text(json.dumps({'stop_new_calls':True,'reason':'new profile'}))
    asyncio.run(mixed_runner.run(p));summary=json.loads((Path(p['output'])/'summary.json').read_text())
    assert not trace and summary['operator_stopped'] and not summary['complete'] and summary['rounds']==[]


def test_stop_appearing_inside_gate_prevents_native_admission(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);stop=tmp_path/'stop.json';p['admission_stop_file']=str(stop)
    class StopGate(Gate):
        async def __aenter__(self):
            stop.write_text(json.dumps({'stop_new_calls':True,'reason':'stop during own gate'}));return self
    result=asyncio.run(mixed_runner.round_run(p,1,{'extractor':StopGate(),'reviewer':Gate()}))
    assert not trace and result['operator_stopped'] and not result['all_pages_attempted']


def test_stage_distributions_keep_engineering_and_drawing_separate(monkeypatch,tmp_path):
    trace=[];install(monkeypatch,trace);p=plan(tmp_path);asyncio.run(mixed_runner.run(p));d=json.loads((Path(p['output'])/'summary.json').read_text())
    assert d['percentage_distributions_from_unrounded_counts']
    for stage in ('first_pass','available_draft','accepted_delivery'):
        assert d['stage_distributions'][stage+'_engineering']['expected_per_round']==3
        assert d['stage_distributions'][stage+'_drawing']['expected_per_round']==3
        assert d['stage_distributions'][stage+'_engineering']['correct_per_round']==[3,3,3]
    assert d['stage_distributions']['first_pass_combined']['expected_per_round']==6

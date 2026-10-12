"""Fast unit: failed calls keep observable cost without pretending a receipt exists.
Expected0.2s/max10s; shields omitted failure costs, replay ambiguity and double counting.
"""
import json
from catalog_bench.partial_usage_collector import collect_failed_round

def make(tmp_path):
 root=tmp_path/'round-1';work=root/'case'/ 'page-0027';history=work/'agent-extractor-0/home/sessions/session/history_extractor.json';history.parent.mkdir(parents=True)
 case={'case_id':'case','physical_page':27,'source_sha256':'a'*64,'calls':[{'role':'extractor','attempt':0,'status':'failed','started_unix':100,'elapsed_seconds':100}]}
 state={'cases':[case],'roles':{'extractor':{'program':{'package_version':'1.4.2','source_code_sha256':'b'*64},'contract_sha256':'c'*64}}};(root/'round.json').write_text(json.dumps(state))
 record={'provider':'anthropic','model':'MiniMax-M3.1-Flash-Preview','timestamp':150,'prompt':{'uncached':11,'cache_read':20,'total':None,'cache_write':None},'completion':{'total':3,'reasoning':1}}
 history.write_text(json.dumps({'messages':[{'channels':{'fast-agent-usage':[{'type':'text','text':json.dumps({'schema':'fast-agent.usage/v2','provider_attempts':[record,dict(record,cost=9)]})}]}}]}))
 plan={'extractor':'anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium','reviewer':'zai.glm-5.3-flash?reasoning=low','cases':[{'id':'case','page':27,'source_sha256':'a'*64}]}
 return root,work,history,state,record,plan

def test_observable_failed_usage_is_partial_and_deduplicated(tmp_path):
 root,work,h,state,record,plan=make(tmp_path);before=h.read_bytes();d=collect_failed_round(root,plan)
 assert d['failed_calls']==1 and d['calls_with_observed_usage']==1 and not d['coverage_complete'];assert d['known_failed_usage']['provider_response_records']==1
 assert d['known_failed_usage']['input_accounted']['sum']==31 and d['known_failed_usage']['input_accounted']['lower_bound_records']==1
 assert d['known_failed_usage']['metrics']['output_total']['sum']==3;assert h.read_bytes()==before
 assert d['calls'][0]['source_binding']=='frozen_plan_and_failed_call_window_not_successful_receipt'

def test_completed_receipt_usage_is_never_counted_as_failed(tmp_path):
 root,work,h,state,record,plan=make(tmp_path);p=work/'calls/c/result.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'status':'completed','execution':{'role':'extractor','attempt':0,'model':plan['extractor'],'started_at':140,'finished_at':160}}))
 d=collect_failed_round(root,plan);assert d['known_failed_usage']['provider_response_records']==0 and d['calls'][0]['usage']['input_accounted']['sum'] is None

def test_ambiguous_replayed_window_and_source_mismatch_stay_unknown(tmp_path):
 root,work,h,state,record,plan=make(tmp_path);state['cases'][0]['calls']*=2;(root/'round.json').write_text(json.dumps(state));d=collect_failed_round(root,plan);assert d['calls_with_observed_usage']==0
 assert all(c['binding_failure']=='multiple_failed_windows_same_role_attempt' for c in d['calls'])
 state['cases'][0]['calls']=state['cases'][0]['calls'][:1];state['cases'][0]['source_sha256']='d'*64;(root/'round.json').write_text(json.dumps(state));d=collect_failed_round(root,plan);assert d['calls'][0]['binding_failure']=='source_page_mismatch'

def test_unrelated_model_or_outside_window_is_not_assigned(tmp_path):
 root,work,h,state,record,plan=make(tmp_path);record.update(model='unrelated',timestamp=300);h.write_text(json.dumps({'messages':[{'channels':{'fast-agent-usage':[{'type':'text','text':json.dumps({'schema':'fast-agent.usage/v2','provider_attempts':[record]})}]}}]}));d=collect_failed_round(root,plan);assert d['calls_with_observed_usage']==0;assert d['known_failed_usage']['metrics']['output_total']['sum'] is None

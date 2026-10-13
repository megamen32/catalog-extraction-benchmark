"""Regrade existing source-bound catalog outputs; zero model calls or edits."""
import hashlib,json,statistics
from pathlib import Path
from catalog_bench.dataset import load_dataset,fixture_path,validate_dataset
from catalog_bench.ownership_corrected_grader import score_ownership_corrected,ownership_grader_digest
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/retained-agent-comparison-v033'
DIGEST='6df48353cac09b55dee5d3157e6dd93517a214ad4e2cdd9d259a76fd88550d80'
assert ownership_grader_digest()==DIGEST

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def verified(case,path,producer):
 assert producer['status']=='receipt_verified' and producer['source_bound_save']
 assert producer['source_sha256']==case['source_sha256'] and producer['physical_page']==case['physical_page']
 assert producer['role']=='extractor' and sha(path)==producer['artifact_sha256']
 target=OUT/'candidates'/f'{sha(path)}.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
 return target,{k:v for k,v in producer.items() if k!='receipt'}
def totals(items):
 eng=sum(x['engineering_correct'] for x in items);draw=sum(x['drawing_correct'] for x in items)
 return {'engineering_correct':eng,'engineering_expected':520,'engineering_percent':100*eng/520,'drawing_correct':draw,'drawing_expected':21,'drawing_percent':100*draw/21,'combined_correct':eng+draw,'combined_expected':541,'combined_percent':100*(eng+draw)/541,'valid_pages':sum(x['candidate'] is not None for x in items),'selected_pages':17}
def main():
 assert validate_dataset('engineering-catalogs-v2')['engineering_facts']==520
 dataset=load_dataset('engineering-catalogs-v2');cases=dataset['cases'];rows=[];source_inputs=[]
 def stage(profile,n,stage,selected,timing,roles,closure=None):
  items=[]
  for case in cases:
   cid=case['id'];p,producer=selected.get(cid,(None,None));item={'case_id':cid,'physical_page':case['physical_page'],'source_sha256':case['source_sha256'],'fixture_sha256':sha(fixture_path(cid,'engineering-catalogs-v2')),'candidate':None,'engineering_correct':0,'drawing_correct':0,'engineering_expected':case['coverage']['engineering_facts'],'drawing_expected':case['coverage'].get('drawing_assertions',0)}
   if p is not None:
    candidate,origin=verified(case,p,producer);assert origin['program']['source_code_sha256']==roles['extractor']['program']['source_code_sha256'] and origin['contract_sha256']==roles['extractor']['contract_sha256'] and origin['model']==roles['extractor']['model'];score=score_ownership_corrected(fixture_path(cid,'engineering-catalogs-v2'),candidate);grade=OUT/'grades'/f'{cid}-{sha(candidate)}.json';write(grade,score);item.update(candidate=str(candidate.relative_to(ROOT)),candidate_sha256=sha(candidate),producer=origin,score=str(grade.relative_to(ROOT)),engineering_correct=score['engineering_facts']['correct'],drawing_correct=score['drawing_assertions']['correct'])
   items.append(item)
  row={'profile':profile,'round':n,'stage':stage,'native_roles':roles,'timing':timing,'totals':totals(items),'cases':items,'full_page_accuracy':False}
  if closure is not None:row['closure']=closure
  rows.append(row)
 legacy=ROOT/'examples/agent-routing/2026-10-12-mixed-v2';old_manifest=json.loads((legacy/'manifest.json').read_text())
 for n in (1,2):
  d=legacy/f'first-pass-round-{n}';p=d/'summary.json';source_inputs.append({'file':str(p.relative_to(ROOT)),'sha256':sha(p)});s=json.loads(p.read_text());selected={x['case_id']:(d/x['candidate']['file'],x['producer']) for x in s['cases'] if x.get('candidate')}
  stage('extractor1.4.2→reviewer1.4.8',n,'first_pass',selected,{'snapshot_wall_seconds':s['round_wall_elapsed_seconds'],'snapshot_active_seconds':s['round_active_elapsed_seconds']},old_manifest['native_roles'])
 corrected=ROOT/'examples/agent-routing/2026-10-12-corrected-v032';new_manifest=json.loads((corrected/'manifest.json').read_text())
 for n in (1,2,3):
  d=ROOT/f'.tmp/corrected-v032/runs/round-{n}';state=json.loads((d/'round.json').read_text());report=json.loads((d/'report.json').read_text());selected={x:{} for x in ('first_pass','available_draft','accepted_delivery')}
  for c in state['cases']:
   calls=[x for x in c['calls'] if x['role']=='extractor' and x['status']=='completed'];initial=next((x for x in calls if x['attempt']==0),None)
   if initial:selected['first_pass'][c['case_id']]=(d/c['case_id']/f"page-{c['physical_page']:04d}"/'candidate-0.json',initial['producer'])
   if c.get('candidate'):
    p=Path(c['candidate']);origin=next((x['producer'] for x in reversed(calls) if x['producer']['artifact_sha256']==sha(p)),None);assert origin
    selected['available_draft'][c['case_id']]=(p,origin)
    if c['status']=='accepted':selected['accepted_delivery'][c['case_id']]=(p,origin)
  for which,data in selected.items():stage('extractor1.4.15→reviewer1.4.17',n,which,data,{'round_wall_seconds':state['elapsed_seconds'],'round_active_seconds':state['active_budget_seconds'],'quota_hold_seconds':state['quota_hold_seconds']},new_manifest['native_roles'],{k:report[k] for k in ('complete','all_pages_attempted','window_expired','drain_reason','natural_native_drain','accepted_pages')})
 aggregates=[]
 for profile,which in dict.fromkeys((r['profile'],r['stage']) for r in rows):
  subset=[r for r in rows if r['profile']==profile and r['stage']==which];a={'profile':profile,'stage':which,'rounds':len(subset)}
  for metric in ('engineering_percent','drawing_percent','combined_percent'):
   v=[r['totals'][metric] for r in subset];a[metric]={'values':v,'mean':statistics.mean(v),'population_sd':statistics.pstdev(v),'min':min(v),'max':max(v)}
  aggregates.append(a)
 result={'schema_version':'1.0','dataset':'engineering-catalogs-v2','grader_release':'0.3.3','grader_sha256':DIGEST,'model_calls_performed':0,'historical_500_facts_excluded':True,'failed_or_missing_candidates_count_zero':True,'full_page_accuracy':False,'reviewer_only_gain_identifiable':False,'production_profile15_to21_not_tested_on_17_pages':True,'source_inputs':source_inputs,'rounds':rows,'aggregates':aggregates,'limitations':['Legacy profile is142→148, not15→148. Both extractor tools and reviewer changed; attribution to reviewer alone is invalid.','First pass has no reviewer effects. Available draft includes incomplete/failed delivery. Accepted delivery means native workflow acceptance, not independent source audit.','Timing for legacy is first-pass snapshot; corrected timing is whole closed round with repairs, so they are not speed A/B.','033 supports selected language aliases and ownership rules; missing means unsupported wording or omitted fact, not necessarily factual falsehood.']}
 probe_root=ROOT.parent/'catalog-to-json/.tmp/full-digitization/reviewer-units-v1.4.21'
 proof=json.loads((probe_root/'native-blind-consumer-proof.json').read_text());old_root=ROOT/'.tmp/corrected-v032/runs/round-1/catalog-1-page-027/page-0027';new_root=probe_root/'review-only/page-0027'
 assert sha(old_root/'candidate-0.json')==sha(new_root/'candidate-0.json')==proof['candidate_sha256']
 assert sha(new_root/'review-0.json')==proof['review_sha256'] and sha(new_root/'source-observation-0.json')==proof['fresh_blind_source_observation_sha256']
 probe=OUT/'reviewer17-vs21-probe';observations=[]
 for version,directory in [('1.4.17',old_root),('1.4.21',new_root)]:
  dest=probe/version;dest.mkdir(parents=True,exist_ok=True)
  for name in ('review-0.json','source-observation-0.json'):(dest/name).write_bytes((directory/name).read_bytes())
  observation=score_ownership_corrected(fixture_path('catalog-1-page-027','engineering-catalogs-v2'),dest/'source-observation-0.json');write(dest/'observation-score-v0.3.3.json',observation)
  review=json.loads((dest/'review-0.json').read_text());false_paths=proof['removed_old_false_paths'];observations.append({'reviewer_version':version,'review_sha256':sha(dest/'review-0.json'),'source_observation_sha256':sha(dest/'source-observation-0.json'),'verdict':review['verdict'],'engineering_correct':observation['engineering_facts']['correct'],'engineering_expected':10,'drawing_correct':observation['drawing_assertions']['correct'],'drawing_expected':13,'false_unit_or_column_paths':sorted({x['path'] for x in review['issues'] if x['path'] in false_paths}),'observation_is_postrepair_output':False})
 result['separate_reviewer_probe']={'case_id':'catalog-1-page-027','physical_page':27,'source_sha256':proof['source_sha256'],'candidate_sha256':proof['candidate_sha256'],'not_148_vs21':True,'not_17_page_accuracy_gain':True,'observations':observations,'source_bound21_producer':{k:v for k,v in proof['native_reviewer'].items() if k!='receipt'},'blind_observation_before_candidate':proof['blind_observation_saved_before_candidate_read'],'remaining21_native_verdict':'revise','native21_elapsed_seconds':proof['native_seconds'],'matched_candidate_not_repaired':True}
 write(OUT/'comparison.json',result)
 artifacts=[{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*.json')) if p.name not in ('artifacts.json','public-verification.json')]
 write(OUT/'artifacts.json',{'model_calls_performed':0,'files':artifacts})
 print(json.dumps({'rows':[{k:r[k] for k in ('profile','round','stage','totals')} for r in rows],'aggregates':aggregates},ensure_ascii=False))
if __name__=='__main__':main()

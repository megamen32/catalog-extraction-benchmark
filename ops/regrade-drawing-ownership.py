"""Offline033 regrade of retained27/39 outputs, preserving old files and bytes."""
import argparse,hashlib,json,shutil
from pathlib import Path
from catalog_bench.dataset import fixture_path
from catalog_bench.language_corrected_grader import score_language_corrected,language_grader_digest
from catalog_bench.ownership_corrected_grader import score_ownership_corrected,ownership_grader_digest


def main():
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--include-native-state',type=Path);args=a.parse_args();b=args.root.resolve();out=b/'examples/corrected-results-v033';out.mkdir(exist_ok=True)
    sources=[]
    for p in (b/'examples/project-x/2026-10-12-native-vision-v1-full').glob('*/round-*/catalog-1-page-*/catalogue-page.json'):
        cid=p.parent.name
        if cid in ('catalog-1-page-027','catalog-1-page-039'):sources.append((cid,p,{'public_reference':str(p.relative_to(b)),'profile':'Project X'}))
    for p in (b/'examples/agent-routing').glob('*/first-pass-round-*/catalog-1-page-*/candidate-*.json'):
        if p.parent.name in ('catalog-1-page-027','catalog-1-page-039'):sources.append((p.parent.name,p,{'public_reference':str(p.relative_to(b)),'profile':'catalog-to-json retained initial'}))
    if args.include_native_state:
        state=json.loads(args.include_native_state.read_text())
        for case in state['cases']:
            if case['case_id'] not in ('catalog-1-page-027','catalog-1-page-039'):continue
            for call in case['calls']:
                if call['role']!='extractor' or call['status']!='completed':continue
                p=args.include_native_state.parent/case['case_id']/f"page-{case['physical_page']:04d}"/f"candidate-{call['attempt']}.json";origin=call['producer'];assert hashlib.sha256(p.read_bytes()).hexdigest()==origin['artifact_sha256']
                sources.append((case['case_id'],p,{'profile':'composition15 retained native output','round':state['round'],'attempt':call['attempt'],'producer':{k:v for k,v in origin.items() if k!='receipt'}}))
    items={}
    for cid,p,ref in sources:
        before=p.read_bytes();sha=hashlib.sha256(before).hexdigest();key=cid+'-'+sha[:16]
        if key in items:items[key]['sources'].append(ref);continue
        directory=out/'candidates'/key;directory.mkdir(parents=True,exist_ok=True);target=directory/'candidate.json';target.write_bytes(before);fixture=fixture_path(cid,'engineering-catalogs-v2');old=score_language_corrected(fixture,target);new=score_ownership_corrected(fixture,target)
        assert p.read_bytes()==before and old['engineering_facts']==new['engineering_facts'] and old['metrics']==new['metrics'] and old['candidate_sha256']==new['candidate_sha256']==sha
        for version,result in [('0.3.2',old),('0.3.3',new)]: (directory/f'score-v{version}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        changes=[{'id':n['id'],'old_status':o['status'],'new_status':n['status']} for o,n in zip(old['drawing_assertions']['checks'],new['drawing_assertions']['checks']) if o['status']!=n['status']]
        items[key]={'case_id':cid,'candidate_sha256':sha,'candidate':str(target.relative_to(b)),'old_score':str((directory/'score-v0.3.2.json').relative_to(b)),'new_score':str((directory/'score-v0.3.3.json').relative_to(b)),'engineering_correct':new['engineering_facts']['correct'],'old_drawing_correct':old['drawing_assertions']['correct'],'new_drawing_correct':new['drawing_assertions']['correct'],'drawing_expected':new['drawing_assertions']['expected'],'status_changes':changes,'sources':[ref]}
    result={'schema_version':'1.0','method':'same retained candidate bytes, offline032 and033 sidecars; no models or frozen cohort changes','old_grader_release':'0.3.2','old_grader_sha256':language_grader_digest(),'new_grader_release':'0.3.3','new_grader_sha256':ownership_grader_digest(),'model_calls_performed':0,'engineering_and_literal_scores_unchanged':True,'original_scores_and_candidates_unchanged':True,'primary_live_cohort_grader_unchanged':'0.3.2','candidate_count':len(items),'changed_candidate_count':sum(bool(i['status_changes']) for i in items.values()),'candidates':list(items.values()),'full_page_accuracy':False}
    (out/'regrading.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'candidates':len(items),'changed':result['changed_candidate_count'],'new_algorithm':result['new_grader_sha256']}))


if __name__=='__main__':main()

"""Grade supplied artifacts without presenting them as fresh model executions."""
import json
from pathlib import Path
from .benchmark import score_file
from .dataset import fixture_path, validate_dataset, load_dataset
from .bench_runner import sha
from .report import summarize


def compare_saved(manifest):
    manifest=Path(manifest).resolve()
    entries=json.loads(manifest.read_text())['artifacts']
    runs=[]; identities=set()
    for entry in entries:
        project=entry['project'];cid=entry['case_id'];model=entry.get('model');stage=entry.get('stage','saved_artifact')
        key=(project,cid,model,stage,entry.get('repeat',1))
        if key in identities:raise ValueError('Duplicate saved-artifact identity')
        identities.add(key)
        candidate=(manifest.parent/entry['candidate']).resolve()
        run={'project':project,'case_id':cid,'model':model,'stage':stage,'repeat':entry.get('repeat',1),
             'runtime_verified':False,'status':'completed','tokens':None,'cost':None,'elapsed_seconds':None}
        try:
            if entry.get('receipt'):
                receipt=json.loads((manifest.parent/entry['receipt']).read_text())
                if receipt.get('candidate_sha256')!=sha(candidate):raise ValueError('Receipt/artifact hash mismatch')
                if stage=='imported_result':
                    if receipt.get('stage')!='imported_result' or receipt.get('runtime_verified') is not False or model is not None:
                        raise ValueError('An imported baseline has no verified model runtime')
                    run['import_provenance']=receipt
                elif receipt.get('status')=='completed':
                    case=load_dataset()
                    source=next(c for c in case['cases'] if c['id']==cid)
                    if receipt.get('source_sha256')!=source['source_sha256'] or receipt.get('physical_page')!=source['physical_page'] or receipt.get('model')!=model:
                        raise ValueError('Receipt contradicts declared source/page/model')
                    run['adapter_receipt']=receipt
                    run['receipt_binding_verified']=True
                else:raise ValueError('Unsuccessful runtime receipt cannot prove a saved candidate')
            run['artifact_sha256']=sha(candidate)
            run['score']=score_file(fixture_path(cid),candidate)
        except (ValueError,OSError,KeyError) as exc:
            run.update(status='invalid_output',error=f'{type(exc).__name__}: {exc}')
        runs.append(run)
    result={'complete':True,'dataset':validate_dataset(),'manifest_sha256':sha(manifest),'runs':runs}
    result['summary']=summarize(result)
    return result

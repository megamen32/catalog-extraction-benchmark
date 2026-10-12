"""Synthetic installation canary. It is never presented as real catalogue performance."""
import hashlib
from pathlib import Path
import sys
import pymupdf
from .bench_runner import run_suite
from .io import write_json


def run_demo(output):
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Demo needs a fresh output directory')
    output.mkdir(parents=True, exist_ok=True)
    source = output/'synthetic.pdf'
    with pymupdf.open() as doc:
        page = doc.new_page(); page.insert_text((72,72),'Synthetic fixture: X | 12 kV')
        doc.save(source)
    fixture = {'id':'synthetic-demo','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
               'page':1,'provenance':'Synthetic installer test, unrelated to the reviewed catalogue dataset.',
               'tables':[{'rows':[['X','12']]}], 'headers':[{'table':0,'column':1,'field':'unit','expected':'кВ','mode':'unit'}],
               'semantic_columns':[[{'field':'Name','tokens':['name'],'unit':None}, {'field':'Voltage','tokens':['voltage'],'unit':'кВ'}]]}
    write_json(output/'fixture.json',fixture)
    # Two intentionally fixed synthetic adapters. Model argument demonstrates routing, not a real model call.
    command=[sys.executable,'-m','catalog_bench.demo','{run_dir}','{model}']
    suite={'cases':[{'id':'synthetic-demo','source':str(source),'page':1,'fixture':'fixture.json'}],
           'projects':[{'id':'synthetic-correct','version':'demo-v1','cwd':str(output),'command':command+['correct'],'artifact':'candidate.json'},
                       {'id':'synthetic-wrong-unit','version':'demo-v1','cwd':str(output),'command':command+['wrong-unit'],'artifact':'candidate.json'}],
           'models':['synthetic-model-a','synthetic-model-b'],'timeout_seconds':10,'deadline_seconds':60}
    write_json(output/'suite.json',suite)
    results = run_suite(output/'suite.json',output/'matrix')
    resumed = run_suite(output/'suite.json',output/'matrix',resume=True)
    if not results['complete'] or not all(r['status']=='completed' for r in results['runs']):
        raise ValueError('Installation demo matrix did not complete')
    if [r['artifact_sha256'] for r in results['runs']] != [r['artifact_sha256'] for r in resumed['runs']]:
        raise ValueError('Resume changed the synthetic artifacts')
    for r in results['runs']:
        want = 2 if r['project']=='synthetic-correct' else 1
        if r['score']['engineering_facts']['correct'] != want:
            raise ValueError('Synthetic unit discrimination failed')
    return {'synthetic':True,'matrix_runs':4,'same_artifacts_on_resume':True,
            'correct_adapter_facts':'2/2','wrong_unit_adapter_facts':'1/2', 'results':str(output/'matrix/results.json')}


def adapter(output,model,variant):
    output=Path(output)
    page={'title':'Synthetic demo','printed_page':None,'text_blocks':[], 'figures':[],
          'tables':[{'id':'t1','title':'Demo','columns':[{'id':'name','label':'Name'}, {'id':'voltage','label':'Voltage','unit':'кВ' if variant=='correct' else 'мм'}],
                     'rows':[{'cells':[{'column_id':'name','value':'X','state':'value'},{'column_id':'voltage','value':'12','state':'value'}]}]}]}
    write_json(output/'candidate.json',page)


if __name__=='__main__':
    adapter(*sys.argv[1:])

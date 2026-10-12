"""Verify all published fresh 1.4.6 candidates with installed released grader 0.2.4."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import statistics
import time
import urllib.request
from catalog_bench import __version__
from catalog_bench.benchmark import grader_digest,score_file
from catalog_bench.dataset import fixture_path

p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
assert version('catalog-extraction-benchmark')==__version__=='0.2.4'
base='https://raw.githubusercontent.com/megamen32/catalog-extraction-benchmark/'+a.revision+'/examples/agent-routing/2026-10-12-fresh-v1.4.6/'
read=lambda path:urllib.request.urlopen(base+path,timeout=30).read()
started=time.monotonic();m=json.loads(read('manifest.json'));assert m['complete'] and m['fresh_attempts']==m['total_attempts']==45 and m['initial_rounds_retained'] is False and m['grader_algorithm_sha256']==grader_digest()
files=0;scores=[];failed=[]
assert len(m['rounds'])==3
for r in m['rounds']:
    total=0;errors=[];assert len(r['cases'])==15 and sum(c['expected'] for c in r['cases'])==500
    for c in r['cases']:
        if c['output'] is None:
            assert c['status']!='completed' and c['correct']==0;errors.append(c['case_id']);continue
        assert c['status']=='completed' and c['tested_program']['package_version']=='1.4.6'
        assert c['tested_program']['git_revision']==m['protocol']['published_revision'] and c['tested_program']['contract_sha256']==m['protocol']['contract_sha256']
        data=read(c['output']['file']);assert hashlib.sha256(data).hexdigest()==c['output']['sha256'] and len(data)==c['output']['bytes']
        target=a.output/c['output']['file'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        s=score_file(fixture_path(c['case_id']),target)
        assert s['candidate_sha256']==c['output']['sha256'] and s['fixture_sha256']==c['fixture_sha256'] and s['grader_sha256']==grader_digest()
        assert s['engineering_facts']['correct']==c['correct'] and s['engineering_facts']['expected']==c['expected']
        total+=s['engineering_facts']['correct'];files+=1
    assert total==r['correct'];scores.append(total);failed.append(errors)
v=[s/5 for s in scores]
for k,want in dict(mean=statistics.mean(v),minimum=min(v),maximum=max(v),range=max(v)-min(v),sample_standard_deviation=statistics.stdev(v)).items():assert abs(m['distribution'][k]-want)<1e-9
proof=dict(public_revision=a.revision,public_files_verified=files,public_attempts_verified=45,downloaded_sha_matches=True,all_outputs_regraded=True,grader_distribution_version=version('catalog-extraction-benchmark'),grader_module_version=__version__,grader_algorithm_sha256=grader_digest(),round_correct=scores,failed_attempts=failed,failed_attempts_in_fixed_denominator=True,elapsed_seconds=time.monotonic()-started)
(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))

"""Download every published candidate and regrade it with released grader 0.2.4."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import statistics
import time
import urllib.request

from catalog_bench import __version__
from catalog_bench.benchmark import grader_digest, score_file
from catalog_bench.dataset import fixture_path

p=argparse.ArgumentParser()
p.add_argument('--revision',required=True,help='Published benchmark Git commit')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
assert version('catalog-extraction-benchmark')==__version__=='0.2.4'
base='https://raw.githubusercontent.com/megamen32/catalog-extraction-benchmark/'+a.revision+'/examples/agent-routing/2026-10-12-repeated-runs/'
read=lambda path:urllib.request.urlopen(base+path,timeout=30).read()
start=time.monotonic();m=json.loads(read('manifest.json'));g=json.loads(read('regrade-v0.2.4.json'))
assert m['complete'] and g['complete'] and g['attempts']==m['total_attempts']==90
assert g['grader_algorithm_sha256']==grader_digest()
files=0;scores={};failures={}
for variant,x in g['variants'].items():
    scores[variant]=[];failures[variant]=[]
    assert len(x['rounds'])==3
    for round,historical in zip(x['rounds'],m['variants'][variant]['rounds']):
        correct=0;failed=[]
        assert len(round['cases'])==15 and sum(c['expected'] for c in round['cases'])==500
        for c,old in zip(round['cases'],historical['cases']):
            assert c['case_id']==old['case_id'] and c['output']==old['output'] and c['status']==old['status']
            if c['output'] is None:
                assert c['status']!='completed' and c['correct']==0
                failed.append(c['case_id']);continue
            data=read(c['output']['file'])
            assert hashlib.sha256(data).hexdigest()==c['output']['sha256'] and len(data)==c['output']['bytes']
            target=a.output/c['output']['file'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            score=score_file(fixture_path(c['case_id']),target)
            assert score['candidate_sha256']==c['output']['sha256'] and score['fixture_sha256']==c['fixture_sha256']
            assert score['grader_sha256']==g['grader_algorithm_sha256']
            assert score['engineering_facts']['expected']==c['expected'] and score['engineering_facts']['correct']==c['correct']
            correct+=score['engineering_facts']['correct'];files+=1
        assert correct==round['correct'];scores[variant].append(correct);failures[variant].append(failed)
    values=[c/5 for c in scores[variant]]
    for key,want in dict(mean=statistics.mean(values),minimum=min(values),maximum=max(values),range=max(values)-min(values),sample_standard_deviation=statistics.stdev(values)).items():
        assert abs(x['distribution'][key]-want)<1e-9
proof=dict(public_revision=a.revision,public_files_verified=files,public_attempts_verified=90,
    downloaded_sha_matches=True,all_outputs_regraded=True,grader_distribution_version=version('catalog-extraction-benchmark'),
    grader_module_version=__version__,grader_algorithm_sha256=grader_digest(),round_correct=scores,failed_attempts=failures,
    failed_attempts_in_fixed_denominator=True,elapsed_seconds=time.monotonic()-start)
(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))

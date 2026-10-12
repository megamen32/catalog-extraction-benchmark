"""Corrected offline drawing grader0.3.1 layered over immutable benchmark0.3.0.

Only fixes numeric charge-group scope boundaries. Native contexts, fixture bytes
and historical scores stay unchanged. New results always carry a new digest.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from catalog_bench.benchmark import BenchmarkCase,score_file,grader_digest
from catalog_bench.drawing import score_drawing_assertions
from catalog_bench.schema import PageContent

CORRECTED_GRADER_VERSION='0.3.1'


def corrected_assertions(assertions):
    assertions=copy.deepcopy(assertions)
    for assertion in assertions:
        assertion['scope_patterns']=[r'(?<![\d.,])'+pattern+r'(?!\d)(?![.,]\d)' if pattern in ('1[,.]2','1[,.]6') else pattern for pattern in assertion.get('scope_patterns',[])]
    return assertions


def corrected_grader_digest():
    return hashlib.sha256(grader_digest().encode()+b'\0'+Path(__file__).read_bytes()).hexdigest()


def score_corrected(fixture,candidate):
    fixture=Path(fixture);candidate=Path(candidate);result=score_file(fixture,candidate);original_digest=result['grader_sha256'];case=BenchmarkCase.model_validate_json(fixture.read_text());data=json.loads(candidate.read_text())
    if 'pages' in data:data=next(page['content'] for page in data['pages'] if page['pdf_page']==case.page)
    content=PageContent.model_validate(data);drawing=score_drawing_assertions(corrected_assertions(case.drawing_assertions),content.model_dump());result['drawing_assertions']=drawing
    # Every other score/all-check property is inherited; only drawing checks can
    # change because the scope fix does not alter source engineering assertions.
    if case.drawing_assertions and not case.tables:
        result['all_verified_checks_passed']=result['engineering_facts']['correct']==result['engineering_facts']['expected'] and drawing['correct']==drawing['expected']
    else:result['all_verified_checks_passed']=result['all_verified_checks_passed'] and drawing['correct']==drawing['expected']
    result.update(grader_release=CORRECTED_GRADER_VERSION,grader_sha256=corrected_grader_digest(),retained_original_grader_sha256=original_digest,correction='Numeric boundaries around source charge scopes1.2/1.6; original annotation bytes unchanged')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('candidate',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args();result=score_corrected(args.fixture,args.candidate);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'grader_release':CORRECTED_GRADER_VERSION,'engineering':result['engineering_facts']['correct'],'drawing':result['drawing_assertions']['correct']}))


if __name__=='__main__':main()

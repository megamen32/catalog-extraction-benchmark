"""Offline grader0.3.3: diameter ownership cannot cross compared objects.

Layers over unchanged0.3.2 engineering/literal scores. Only scoped circle-owner
matches are filtered; comparison alone supplies neither positive nor wrong proof.
"""
import argparse,hashlib,json,re,importlib.util,sys
from pathlib import Path
from catalog_bench.benchmark import BenchmarkCase
from catalog_bench.schema import PageContent
try:
    from catalog_bench.language_corrected_grader import score_language_corrected,language_grader_digest,matching_content,language_assertions
except ModuleNotFoundError as error:
    if error.name!='catalog_bench.language_corrected_grader':raise
    # Standalone release: immutable032 companion plus the original030 wheel.
    companion=Path(__file__).with_name('catalog-language-grader-v0.3.2.py')
    if hashlib.sha256(companion.read_bytes()).hexdigest()!='e268c25f302e051d6b34295298eac6603dba8ff9f108003bb9bd3f3a2685972d':raise ValueError('Released032 companion changed')
    spec=importlib.util.spec_from_file_location('catalog_bench.language_corrected_grader',companion)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    from catalog_bench.language_corrected_grader import score_language_corrected,language_grader_digest,matching_content,language_assertions
if language_grader_digest()!='f091872c67af7e410490df6b590cb8ac03a05eb6e615351ed281c4ae1687e21d':raise ValueError('Required032 baseline algorithm changed')
from catalog_bench.drawing import scopes,negated

OWNERSHIP_GRADER_VERSION='0.3.3'
NUMBER=r'[φØø]?\s*(?P<number>\d+)(?!\d)(?![.,]\d)'
NEUTRAL=r'(?:окружност\w*|контур\w*|диаметр\w*|кольц\w*)\s+'
OWNER=r'(?P<owner>наружн\w*|внешн\w*|внутренн\w*|центральн\w*|штрих\w*|пунктир\w*)\s+(?:контур\w*|окружност\w*|кольц\w*|диаметр\w*|поверхн\w*|кра\w*|гран\w*|сторон\w*)'
BETWEEN=r'\b(?:между|between)\s+(?:the\s+)?'
JOIN=r'\s+(?:и|and)\s+(?:the\s+)?'
COMPARISONS=[re.compile(BETWEEN+'(?:'+NEUTRAL+')?'+NUMBER+JOIN+OWNER,re.I),re.compile(BETWEEN+OWNER+JOIN+'(?:'+NEUTRAL+')?'+NUMBER,re.I)]


def cross_object_comparison(text,match):
    """Suppress only the number in one object and owner word in the other.

    'between outer circle Ø116 and center' still asserts thatØ116 belongs to
    the outer circle: no neutral numbered-object pattern exempts that claim.
    """
    if 'claim' not in match.re.groupindex:return False
    number=re.search(r'\d+',match.group())
    if not number:return False
    ns=(match.start()+number.start(),match.start()+number.end());cs=match.span('claim')
    for pattern in COMPARISONS:
        for comparison in pattern.finditer(text):
            n=comparison.span('number');c=comparison.span('owner')
            if n[0]<=ns[0] and ns[1]<=n[1] and c[0]<=cs[0] and cs[1]<=c[1]:return True
    return False


def ownership_drawing_assertions(assertions,data):
    checks=[]
    for a in assertions:
        evidence=[];bad=[];filtered=[];candidates=list(scopes(data,a))
        guarded=a['id'].endswith(('outer140','pitch116'))
        for index,text in candidates:
            for kind,patterns in [('forbidden',a.get('forbidden_patterns',[])),('positive',a.get('positive_patterns',[]))]:
                for pattern in patterns:
                    for match in re.finditer(pattern,text,re.I):
                        if negated(text,match):continue
                        item={'figure_index':index,'text':text,'pattern':pattern}
                        if guarded and cross_object_comparison(text,match):filtered.append(dict(item,match_kind=kind,reason='different_objects_in_between_relation'));continue
                        (bad if kind=='forbidden' else evidence).append(item)
        positive=not a.get('positive_patterns') or bool(evidence)
        status='wrong' if bad else 'passed' if candidates and positive else 'missing'
        checks.append({'id':a['id'],'expected':a['source_fact'],'category':a['category'],'status':status,'evidence':evidence,'contradictions':bad,'excluded_cross_object_matches':filtered})
    count=sum(c['status']=='passed' for c in checks)
    return {'correct':count,'expected':len(checks),'percent':round(100*count/len(checks),2) if checks else None,'checks':checks,'full_drawing_accuracy':False,'method':'scoped deterministic assertions with compared-object ownership guard; unknown wording is missing'}


def ownership_grader_digest():
    return hashlib.sha256(language_grader_digest().encode()+b'\0'+Path(__file__).read_bytes()).hexdigest()


def score_ownership_corrected(fixture,candidate):
    fixture=Path(fixture);candidate=Path(candidate);base=score_language_corrected(fixture,candidate);case=BenchmarkCase.model_validate_json(fixture.read_text());raw=json.loads(candidate.read_text())
    if 'pages' in raw:raw=next(p['content'] for p in raw['pages'] if p['pdf_page']==case.page)
    matched,_=matching_content(case,PageContent.model_validate(raw));old=base['drawing_assertions'];drawing=ownership_drawing_assertions(language_assertions(case.drawing_assertions),matched.model_dump())
    base['drawing_assertions']=drawing
    # Preserve literal/engineering/raw-source grading exactly, only replacing
    # the drawing conjunction that could have failed in the retained032 result.
    if drawing['correct']!=drawing['expected']:base['all_verified_checks_passed']=False
    elif old['correct']==old['expected']:pass
    else:
        from catalog_bench.benchmark import score_file
        original=score_file(fixture,candidate)
        base['all_verified_checks_passed']=base['engineering_facts']['correct']==base['engineering_facts']['expected'] and (original['all_verified_checks_passed'] if case.tables else True)
    base.update(grader_release=OWNERSHIP_GRADER_VERSION,retained_v032_grader_sha256=base['grader_sha256'],grader_sha256=ownership_grader_digest(),correction='Retained032 aliases and engineering scores; Ø116/Ø140 ownership cannot cross objects compared with between/между')
    return base


def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('candidate',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=score_ownership_corrected(a.fixture,a.candidate);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print({'grader_release':OWNERSHIP_GRADER_VERSION,'engineering':r['engineering_facts']['correct'],'drawing':r['drawing_assertions']['correct']})


if __name__=='__main__':main()

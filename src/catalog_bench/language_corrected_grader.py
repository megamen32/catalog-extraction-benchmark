"""Offline grader0.3.2: scoped physical-symbol and geometry-language aliases.

Original030/031 results, source annotations and candidate bytes stay immutable.
Aliases affect matching only; identifiers and raw literal metrics remain exact.
"""
import argparse,copy,hashlib,json,re
from pathlib import Path
from collections import Counter
from catalog_bench.benchmark import BenchmarkCase,score_file,grader_digest
from catalog_bench.schema import PageContent
from catalog_bench.semantic import score_facts
from catalog_bench.drawing import score_drawing_assertions

LANGUAGE_GRADER_VERSION='0.3.2'
UNITS={'A':'А','kA':'кА','kV':'кВ','kN':'кН','kg':'кг','mm':'мм','cm':'см','kJ/kV':'кДж/кВ'}
GEOMETRY_ALIASES=[
 (r'\bbolt[- ]circle(?:\s+diameter)?\b','окружность центров отверстий'),
 (r'\bflange\s+diameter\b','наружный диаметр фланца'),
 (r'\bcross[- ]arm\s+tube\b','труба поперечины'),
 (r'\b(?:outer|external)\s+(?:contour|circle|circumference)\b','наружный контур'),
 (r'\b(?:inner|internal)\s+(?:contour|circle|diameter)\b','внутренний диаметр'),
 (r'\bcentral\s+holes?\b','центральные отверстия'),
 (r'\b(?:ring|rounded)\s+(?:profile|element)\b','кольцевой профиль'),
 (r'\b(?:porcelain|ceramic)\b','фарфоровый'),
 (r'\b(?:is\s+)?not\s+(?:specified|indicated|stated|printed)\b','не указан'),
 (r'\bnot\b','не'),(r'\bbut\b','но'),
 (r'\bside\s+view\b','вид сбоку'),(r'\btop\s+view\b','вид сверху'),
 (r'\bplate\s+(?:height|width)\b','ширина пластины'),
 (r'\b(?:support|supporting)\s+(?:flat\s+)?bar\b','опорная планка'),
 (r'\belectrode\s+coatings?\b','электродное покрытие'),
 (r'\belectrode\s+ribs?\b','электродные ребра'),
 (r'\bbetween\s+(?:the\s+)?(?:axes|centers|centres)\s+of\s+(?:the\s+)?holes\b','между центрами отверстий'),
 (r'\bhole[- ](?:center|centre)\s+(?:distance|spacing)\b','между центрами отверстий'),
 (r'\bupper\s+and\s+lower\s+plate\s+faces\b','верхняя и нижняя грани пластины'),
 (r'\blower\s+edge\b','нижний край'),(r'\bupper\s+edge\b','верхний край'),
 (r'\bring\b','кольцо'),(r'\bprofile\b','профиль'),
 (r'\bdiameter\b','диаметр')]


def geometry_aliases(text):
    text=str(text).replace('⌀','φ')
    # Distinct diameter clauses may not borrow each other's ownership words.
    text=re.sub(r',\s*(?=(?:flange\s+diameter|bolt[- ]circle|(?:outer|inner|external|central)\b|four\s+holes)\b[^;.,]{0,60}[φØ]\s*\d)', '; ', text, flags=re.I)
    text=re.sub(r'\bsection\s+([AB])\s*[-–]\s*([AB])\b',lambda m:'сечение '+{'A':'А','B':'Б'}[m[1].upper()]+'-'+{'A':'А','B':'Б'}[m[2].upper()],text,flags=re.I)
    text=re.sub(r'\b(?:view|вид)\s+([AB])\b',lambda m:'Вид '+{'A':'А','B':'Б'}[m[1].upper()],text,flags=re.I)
    for pattern,replacement in GEOMETRY_ALIASES:text=re.sub(pattern,replacement,text,flags=re.I)
    return text


def language_assertions(assertions):
    result=copy.deepcopy(assertions)
    for a in result:
        a['scope_patterns']=[r'(?<![\d.,])'+p+r'(?!\d)(?![.,]\d)' if p in ('1[,.]2','1[,.]6') else p for p in a.get('scope_patterns',[])]
        if a['id']=='material-source-absence':a['category']='unsupported_material_reference'
        if a['id']=='ring500':
            number=r'(?<![\d.,φ])φ?\s*500(?!\d)(?![.,]\d)'
            claim=r'(?P<claim>труб\w*[^.;\d]{0,40}диаметр\w*|диаметр\w*[^.;\d]{0,40}труб\w*)'
            a['forbidden_patterns'] += [number+r'[^.;\d]{0,70}'+claim,claim+r'[^.;\d]{0,70}'+number]
    return result


def matching_content(case,content):
    data=copy.deepcopy(content.model_dump());notes=[]
    for ti,table in enumerate(data['tables']):
        pollution_field=ti<len(case.semantic_columns) and any('сз' in a.get('tokens',[]) for a in case.semantic_columns[ti])
        for ci,column in enumerate(table['columns']):
            for field in ('label','group','qualifier','unit'):
                raw=column.get(field)
                if not isinstance(raw,str):continue
                value=UNITS.get(raw,raw) if field=='unit' else re.sub(r'(?<![\w.,])(\d+(?:[.,]\d+)?)\s*(kA|кA|A)(?![\w])',lambda m:m[1]+' '+{'kA':'кА','кA':'кА','A':'А'}[m[2]],raw)
                if pollution_field and re.search(r'степень\s+загряз', ' '.join(str(column.get(k) or '') for k in ('label','group','qualifier')),re.I):
                    fixed=re.sub(r'\([СC]3\)', '(СЗ)',value)
                    if fixed!=value:notes.append({'location':f'tables[{ti}].columns[{ci}].{field}','raw':raw,'matching_only':fixed,'classification':'contextual_header_abbreviation_typo'})
                    value=fixed
                if value!=raw and not any(n.get('location')==f'tables[{ti}].columns[{ci}].{field}' for n in notes):notes.append({'location':f'tables[{ti}].columns[{ci}].{field}','raw':raw,'matching_only':value,'classification':'physical_unit_symbol_alias'})
                column[field]=value
    for figure in data['figures']:
        for field in ('title','description'):figure[field]=geometry_aliases(figure[field])
        figure['labels']=[geometry_aliases(s) for s in figure['labels']]
    return PageContent.model_validate(data),notes


def language_grader_digest():
    return hashlib.sha256(grader_digest().encode()+b'\0'+Path(__file__).read_bytes()).hexdigest()


def score_language_corrected(fixture,candidate):
    fixture=Path(fixture);candidate=Path(candidate);case=BenchmarkCase.model_validate_json(fixture.read_text());raw=json.loads(candidate.read_text());base=score_file(fixture,candidate)
    if 'pages' in raw:raw=next(p['content'] for p in raw['pages'] if p['pdf_page']==case.page)
    matched,notes=matching_content(case,PageContent.model_validate(raw));engineering=score_facts(case,matched)
    for check in engineering['checks']:
        # Quantity+metric thread symbol is a dimensional designation, not a
        # product identifier. Correct only exact script differences with every
        # preexisting identity/field/unit/state condition already satisfied.
        expected=str(check.get('expected') or '');observed=str(check.get('observed') or '')
        if check.get('status')=='wrong' and check.get('field') in ('d1','d2','d3') and re.fullmatch(r'\d+М\d+',expected) and observed.replace('M','М')==expected and re.fullmatch(r'\d+M\d+',observed) and check.get('observed_state')=='value' and {'field','unit','bounds','frequency'}.issubset(check.get('conditions',{})) and all(check['conditions'].values()):
            check.update(status='passed',value_and_state=True,literal_match=False,normalization='metric_thread_script_alias');notes.append({'check_id':check['id'],'raw':observed,'source_literal':expected,'classification':'literal_script_only_physical_thread_equivalent'})
    counts=dict(Counter(c['status'] for c in engineering['checks']));engineering.update(correct=counts.get('passed',0),statuses=counts,percent=round(100*counts.get('passed',0)/engineering['expected'],2) if engineering['expected'] else None)
    drawing=score_drawing_assertions(language_assertions(case.drawing_assertions),matched.model_dump());base['engineering_facts']=engineering;base['drawing_assertions']=drawing
    complete=engineering['correct']==engineering['expected'] and drawing['correct']==drawing['expected'];base['all_verified_checks_passed']=complete and (base['all_verified_checks_passed'] if case.tables else True)
    base.update(grader_release=LANGUAGE_GRADER_VERSION,retained_original_grader_sha256=base['grader_sha256'],grader_sha256=language_grader_digest(),literal_format_differences=notes,unsupported_material_reference_policy='Strict source-absence proxy for material mentions including appearance analogies; not an assertion that the candidate claims manufacture from that material',raw_literal_metrics_unchanged=True,source_fixture_bytes_unchanged=True,identifiers_are_not_globally_normalized=True,correction='Matching-only physical A/А aliases, supported English geometry, contextual pollution abbreviation and dimensional metric-thread script difference; numeric/scoped/negation guards retained')
    return base


def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('candidate',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=score_language_corrected(a.fixture,a.candidate);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({'grader_release':LANGUAGE_GRADER_VERSION,'engineering':result['engineering_facts']['correct'],'drawing':result['drawing_assertions']['correct']})


if __name__=='__main__':main()

"""Independent supplemental13-check source audit; leaves frozen grades unchanged."""
import argparse,hashlib,json,re,importlib.util,sys
from pathlib import Path
from catalog_bench.schema import PageContent
try:
    from catalog_bench.language_corrected_grader import geometry_aliases,language_grader_digest
except ModuleNotFoundError as error:
    if error.name!='catalog_bench.language_corrected_grader':raise
    companion=Path(__file__).with_name('catalog-language-grader-v0.3.2.py')
    if hashlib.sha256(companion.read_bytes()).hexdigest()!='e268c25f302e051d6b34295298eac6603dba8ff9f108003bb9bd3f3a2685972d':raise ValueError('Released032 companion changed')
    spec=importlib.util.spec_from_file_location('catalog_bench.language_corrected_grader',companion);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    from catalog_bench.language_corrected_grader import geometry_aliases,language_grader_digest
from catalog_bench.drawing import negated

VERSION='1.0.0'
EXPECTED_BASE='f091872c67af7e410490df6b590cb8ac03a05eb6e615351ed281c4ae1687e21d'
NUMBER=r'(?<![\d.,φØ⌀])(?:67[,.]5|135|45)(?!\d)(?![.,]\d)'
HEAD=re.compile(r'(?P<numbers>'+NUMBER+r'(?:\s*(?:и|and|,)\s*'+NUMBER+r')*)\s*(?:мм\s*)?[—–:=\-]\s*',re.I)
LEFT=r'лев\w*\s+(?:кра\w*|гран\w*|кромк\w*)\s+(?:пластин\w*|плит\w*)'
AXIS=r'(?:центральн\w*\s+(?:ось|оси|осью)|(?:ось|оси)\s+корпус\w*|(?:ось|оси)\s+симметр\w*)'
FIRST=r'(?:центр\w*|ос\w*)\s+(?:перв\w*|лев\w*)\s+отверсти\w*'
SECOND=r'(?:центр\w*|ос\w*)\s+(?:втор\w*|средн\w*|центральн\w*)\s+отверсти\w*'
TWO=r'между\s+(?:центр\w*|ос\w*)\s+(?:перв\w*\s+)?двух\s+(?:лев\w*\s+)?отверсти\w*'
FULL=r'\b(?:полн\w*|общ\w*|вс\w*)\s+длин\w*\s+(?:пластин\w*|плит\w*)'

def has(text,pattern):
    return any(not negated(text,m) for m in re.finditer('(?P<claim>'+pattern+')',text,re.I))

def scoped_views(data,fact):
    charge=r'(?<![\d.,])'+fact['charge'].replace('.',r'[,.]')+r'(?!\d)(?![.,]\d)';execution=r'\b'+fact['execution']+r'\b'
    for i,f in enumerate(data['figures']):
        title=geometry_aliases(f['title']);description=geometry_aliases(f['description']).replace('ё','е')
        # Title owns the charge/execution; comparative prose cannot borrow scope.
        if not re.search(charge,title) or not re.search(execution,title):continue
        other_charge='1.6' if fact['charge']=='1.2' else '1.2';other_execution='IV' if fact['execution']=='III' else 'III'
        if re.search(r'(?<![\d.,])'+other_charge.replace('.',r'[,.]')+r'(?!\d)',title) or re.search(r'\b'+other_execution+r'\b',title):continue
        markers=list(re.finditer(r'\bвид\s+([АБ])\s*:',description,re.I))
        for j,m in enumerate(markers):
            if m[1].upper()=='А':yield i,description[m.end():markers[j+1].start() if j+1<len(markers) else len(description)]

def relations(text,dimension):
    wanted=dimension.replace(',','.')
    for clause in re.split(r'[;\n]|\.(?!\d)',text):
        heads=list(HEAD.finditer(clause))
        if heads:
            for i,h in enumerate(heads):
                numbers=[x.group().replace(',','.') for x in re.finditer(NUMBER,h['numbers'])]
                if wanted in numbers:yield clause[h.end():heads[i+1].start() if i+1<len(heads) else len(clause)]
        else:
            numbers=[x.group().replace(',','.') for x in re.finditer(NUMBER,clause)]
            if numbers==[wanted]:yield clause

def endpoint(text,pattern):
    return has(text,r'(?:от|до|между|и)\s+(?:самого\s+)?'+pattern)

def axis_endpoints(text):
    body_axis=False;hole_owned=False
    pattern=re.compile(r'(?P<claim>(?:от|до|между|и)\s+'+AXIS+')',re.I)
    for match in pattern.finditer(text):
        if negated(text,match):continue
        tail=text[match.end():match.end()+90]
        # A central axis explicitly owned by a hole or plate is not the body axis.
        # An explicit body owner takes priority over later contextual holes.
        owned=not re.match(r'\s+корпус\w*\b',tail,re.I) and bool(re.match(r'\s+(?:\w+\s+){0,4}(?:отверсти\w*|пластин\w*|плит\w*)\b',tail,re.I))
        if owned:hole_owned=True
        else:body_axis=True
    return body_axis,hole_owned

def dimension_status(body,dimension):
    left=endpoint(body,LEFT);axis,hole_axis=axis_endpoints(body)
    two=has(body,TWO) or (endpoint(body,FIRST) and endpoint(body,SECOND))
    first=endpoint(body,FIRST);second=endpoint(body,SECOND);full=has(body,FULL)
    if dimension=='45':return ('wrong' if left or axis or full else 'passed' if two else 'missing')
    if dimension=='67.5':return ('wrong' if left or two or full or hole_axis or (first and axis and not second) else 'passed' if second and axis else 'missing')
    return 'wrong' if full or two or hole_axis or (second and axis and not left) else 'passed' if left and axis else 'missing'

def creepage_check(data,fact):
    result={'id':fact['id'],'expected':fact['source_fact'],'status':'missing','evidence':[]}
    matches_tables=[t for t in data['tables'] if any(isinstance(c.get('value'),str) and re.search(fact['lower_table_charge_product_pattern'],c['value']) for r in t['rows'] for c in r['cells'])]
    if len(matches_tables)!=1:return result
    table=matches_tables[0];table_index=data['tables'].index(table)
    matches=[c for c in table['columns'] if re.search(fact['label_pattern'],c['label'],re.I)]
    if len(matches)!=1:return result
    c=matches[0];own=' '.join(str(c.get(k) or '') for k in ('label','group','qualifier')).replace('«','').replace('»','').replace('"','')
    if c.get('unit') not in ('см','cm') and not re.search(r'\b(?:см|cm)\b',c['label']):return result
    asserted=[]
    for m in re.finditer(r'(?P<claim>\bне\s+менее\b)',own,re.I):
        prefix=own[max(0,m.start()-40):m.start()]
        if negated(own,m) or re.search(r'\bбез\s+(?:услови\w*\s*)?$',prefix,re.I):continue
        asserted.append(m.group())
    result.update(status='wrong' if asserted else 'passed',evidence=[{'table_index':table_index,'column_id':c['id'],'own_label':c['label'],'own_group':c.get('group'),'own_qualifier':c.get('qualifier'),'unit':c.get('unit')}]);return result

def audit(fixture,candidate):
    if language_grader_digest()!=EXPECTED_BASE:raise ValueError('Frozen032 language baseline changed')
    fixture=Path(fixture);candidate=Path(candidate);case=json.loads(fixture.read_text());raw=json.loads(candidate.read_text());binding='bare content; exact source/page require external native producer'
    if 'pages' in raw:
        assert raw['source']['sha256']==case['source_sha256'];pages=[p['content'] for p in raw['pages'] if p['pdf_page']==case['physical_page']];assert len(pages)==1;raw=pages[0];binding='wrapper source and physical page verified'
    data=PageContent.model_validate(raw).model_dump();checks=[]
    for fact in case['drawing_facts']:
        evidence=[];wrong=[]
        for i,text in scoped_views(data,fact):
            for body in relations(text,fact['dimension']):
                status=dimension_status(body,fact['dimension']);item={'figure_index':i,'relation_text':body.strip()}
                if status=='passed':evidence.append(item)
                elif status=='wrong':wrong.append(item)
        checks.append({'id':fact['id'],'expected':fact['source_fact'],'status':'wrong' if wrong else 'passed' if evidence else 'missing','evidence':evidence,'contradictions':wrong})
    checks.append(creepage_check(data,case['column_fact']))
    return {'supplemental_audit_version':VERSION,'source_sha256':case['source_sha256'],'physical_page':case['physical_page'],'source_binding':binding,'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'algorithm_sha256':hashlib.sha256(Path(__file__).read_bytes()+EXPECTED_BASE.encode()).hexdigest(),'checks':checks,'passed':sum(c['status']=='passed' for c in checks),'wrong':sum(c['status']=='wrong' for c in checks),'missing':sum(c['status']=='missing' for c in checks),'expected_checks':13,'new_overall_benchmark_percent':False,'original_primary_scores_unchanged':True,'full_page_accuracy':False,'method':'Selected scoped endpoint relations and one own-column source-absence condition; supported Russian wording, unknown wording missing; no model calls'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('candidate',type=Path);a=p.parse_args();r=audit(a.fixture,a.candidate);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print({k:r[k] for k in ('passed','wrong','missing','expected_checks')})
if __name__=='__main__':main()

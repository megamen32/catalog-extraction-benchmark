"""Offline supplemental1.0.1; released1.0.0 endpoint checks stay immutable."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

BASE_SOURCE_SHA='23f14700ff03e08f0090b8509ca418f30bf1de09a68926a903948a2517c6092d'
try:
    from catalog_bench import supplemental_drawing_audit as base
except ImportError:
    path=Path(__file__).with_name('catalog-supplemental-drawing-audit-v1.py')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=BASE_SOURCE_SHA:
        raise ValueError('Released supplemental1.0.0 companion changed')
    spec=importlib.util.spec_from_file_location('catalog_bench.supplemental_drawing_audit',path)
    base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
if hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest()!=BASE_SOURCE_SHA:
    raise ValueError('Released supplemental1.0.0 source changed')

VERSION='1.0.1'
LABEL=re.compile(r'длина\s+пути\s+утечки(?:\s+тока)?(?:\s*[,;]?\s*\(?\s*(?:см|cm)\s*\)?)?\.?',re.I)
BOUND_NAME=r'(?:не\s+(?:менее|более|ниже|выше)|at\s+(?:least|most)|минимум|максимум|minimum|maximum)'
ABSENCE=re.compile(r'(?:условие\s+(?:'+BOUND_NAME+r'\s+)?не\s+указано|без\s+условия\s+'+BOUND_NAME+r'|без\s+минимального\s+условия|минимум\s+не\s+указан|no\s+minimum\s+condition|minimum\s+(?:condition\s+)?not\s+specified|without\s+(?:the\s+)?condition\s+at\s+(?:least|most))\.?',re.I)
BOUND=re.compile(r'(?<!\w)(?:не\s+(?:менее|более|ниже|выше)|at\s+(?:least|most)|минимум|максимум|minimum|maximum|min|max)(?!\w)|[≥≤]|>=|<=',re.I)

def clean(value):
    return re.sub(r'\s+',' ',str(value or '').replace('«','').replace('»','').replace('"','')).strip()

def own_condition_check(data,fact):
    result=base.creepage_check(data,fact)
    if result['status']!='passed':return result
    evidence=result['evidence'][0]
    column=next(c for c in data['tables'][evidence['table_index']]['columns'] if c['id']==evidence['column_id'])
    fields={k:clean(column.get(k)) for k in ('label','group','qualifier')}
    # A complete, explicit absence statement may pass. One disclaimer never
    # erases a separate asserted bound or an unknown clause in the same field.
    assertions=[]
    for k,v in fields.items():
        if not v or ABSENCE.fullmatch(v):continue
        for match in BOUND.finditer(v):
            # Unsupported negated English phrases remain unknown, never an
            # affirmative bound. Only complete supported absence can pass.
            prefix=v[max(0,match.start()-15):match.start()]
            if re.search(r'\b(?:not|no|without)\s*$',prefix,re.I):continue
            assertions.append(k);break
    unknown=[k for k in ('group','qualifier') if fields[k] and not ABSENCE.fullmatch(fields[k])]
    if not LABEL.fullmatch(fields['label']):unknown.append('label')
    result.update(status='wrong' if assertions else 'missing' if unknown else 'passed',
                  recognized_unprinted_bound_fields=assertions,unknown_condition_fields=unknown)
    return result

def audit(fixture,candidate):
    result=base.audit(fixture,candidate)
    case=json.loads(Path(fixture).read_text());raw=json.loads(Path(candidate).read_text())
    if 'pages' in raw:raw=next(p['content'] for p in raw['pages'] if p['pdf_page']==case['physical_page'])
    data=base.PageContent.model_validate(raw).model_dump()
    prior={k:result[k] for k in ('passed','wrong','missing')}
    replacement=own_condition_check(data,case['column_fact'])
    result['checks']=[replacement if c['id']==case['column_fact']['id'] else c for c in result['checks']]
    for status in ('passed','wrong','missing'):result[status]=sum(c['status']==status for c in result['checks'])
    result.update(supplemental_audit_version=VERSION,base_supplemental_source_sha256=BASE_SOURCE_SHA,
                  base_supplemental_v1_counts=prior,
                  algorithm_sha256=hashlib.sha256(Path(__file__).read_bytes()+BASE_SOURCE_SHA.encode()+base.EXPECTED_BASE.encode()).hexdigest(),
                  method='Immutable supplemental1.0.0 endpoint checks; own-column condition1.0.1 supports empty or explicit absent conditions and selected bound phrases. Unknown own conditions are missing; no model calls.')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('candidate',type=Path);a=p.parse_args()
    result=audit(a.fixture,a.candidate);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({k:result[k] for k in ('passed','wrong','missing','expected_checks')})

if __name__=='__main__':main()

"""Frozen, deterministic drawing assertions: scope, relation coverage and hallucinations.

No model judge. Supported phrases are a conservative text proxy, not universal
natural-language comprehension. Report every matched evidence and missing check.
"""
import re
import unicodedata


def normalized(text):
    return ' '.join(re.sub(r'[ØФф](?=\s*\d)', 'φ', unicodedata.normalize('NFC', str(text)).replace('ё','е')).split())


def figure_text(figure):
    return normalized(' '.join([figure.get('title',''),figure.get('description',''),*figure.get('labels',[])]))


def scopes(data, assertion):
    for index, figure in enumerate(data.get('figures', [])):
        text=figure_text(figure)
        # Group assertions may not borrow evidence from another charge/execution.
        if not all(re.search(p,text,re.I) for p in assertion.get('scope_patterns',[])):continue
        view=assertion.get('view')
        if view:
            marker=re.compile(r'(?:(?i:вид\s*(?:сверху|снизу|сбоку)?\s*[«"\(]?)|\b)([АБ])(?:[»"\)]|\b)')
            matches=list(marker.finditer(text));parts=[]
            for k,m in enumerate(matches):
                if m.group(1).upper()==view:
                    end=matches[k+1].start() if k+1<len(matches) else len(text)
                    parts.append(text[max(0,m.start()-12):end])
            title=normalized(figure.get('title',''))
            title_views={m.group(1).upper() for m in marker.finditer(title)}
            if title_views=={view} and not any(m.group(1).upper()!=view for m in matches):parts=[text]
            for part in parts:yield index,part
        else:yield index,text


def negated(text, match):
    claim_start=match.start('claim') if 'claim' in match.re.groupindex else match.start()
    claim_end=match.end('claim') if 'claim' in match.re.groupindex else match.end()
    before=re.split(r'[;,.!?]|\b(?:но|а|однако)\b',text[max(0,claim_start-80):claim_start],flags=re.I)[-1]
    if re.search(r'\bне\s+(?:\w+\s+){0,3}$',before,re.I):return True
    after=text[claim_end:claim_end+45]
    return bool(re.match(r'\s+не\s+(?:указан\w*|напечатан\w*|подтвержден\w*|назван\w*|обозначен\w*)\b',after,re.I))


def score_drawing_assertions(assertions,data):
    checks=[]
    for a in assertions:
        evidence=[];bad=[]
        candidates=list(scopes(data,a))
        for index,text in candidates:
            for pattern in a.get('forbidden_patterns',[]):
                for match in re.finditer(pattern,text,re.I):
                    if not negated(text,match):bad.append({'figure_index':index,'text':text,'pattern':pattern})
            for pattern in a.get('positive_patterns',[]):
                for match in re.finditer(pattern,text,re.I):
                    if not negated(text,match):evidence.append({'figure_index':index,'text':text,'pattern':pattern})
        positive=not a.get('positive_patterns') or bool(evidence)
        # Absence-only checks still require actual scoped figure coverage.
        status='wrong' if bad else 'passed' if candidates and positive else 'missing'
        checks.append({'id':a['id'],'expected':a['source_fact'],'category':a['category'],'status':status,'evidence':evidence,'contradictions':bad})
    correct=sum(c['status']=='passed' for c in checks)
    return {'correct':correct,'expected':len(checks),'percent':round(100*correct/len(checks),2) if checks else None,'checks':checks,'full_drawing_accuracy':False,'method':'frozen scoped deterministic relation/claim assertions; unsupported wording is missing, never inferred'}

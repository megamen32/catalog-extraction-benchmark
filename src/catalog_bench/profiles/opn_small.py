"""Selected surge-arrester and cross-reference facts, source-audit v2."""
import re, decimal, collections, unicodedata
from .header_rules import clean_header

def norm(s):
    return re.sub('\\s+', '', unicodedata.normalize('NFC', str(s or ''))).replace('–', '-').replace('−', '-')

def text(c):
    return ' '.join((str(c.get(k) or '') for k in ['label', 'group', 'qualifier', 'unit']))

def alpha(s):
    return norm(s).lower().replace('ё', 'е')

def literal(s):
    return re.sub('\\s+', '', unicodedata.normalize('NFC', str(s or '')))

def valmatch(a, b):
    if literal(a) == literal(b):
        return (True, 'literal')
    if norm(a) == norm(b):
        return (True, 'dash_glyph_format')
    try:
        if decimal.Decimal(str(a).replace(',', '.')) == decimal.Decimal(str(b).replace(',', '.')):
            return (True, 'decimal_format')
    except:
        pass
    if norm(a).replace('х', 'x').replace('×', 'x') == norm(b).replace('х', 'x').replace('×', 'x'):
        return (True, 'multiplication_glyph')
    if norm(a).replace('С', 'C') == norm(b).replace('С', 'C'):
        return (True, 'source_glyph_alias')
    return (False, None)

def amps(s):
    return set((norm(x) for x in re.findall('(?<![\\d.,])(\\d+(?:[,.]\\d+)?\\s*(?:кА|А))(?![а-яA-Za-z])', s)))

def header_matches(f, c):
    p = alpha(f['parameter'])
    h = alpha(text(c))
    if 'остающеесяпри' in p:
        if 'остающ' not in h:
            return False
        if 'грозов' in p and 'грозов' not in h:
            return False
        want = amps(f['parameter'])
        have = amps(text(c))
        if want and (not want.issubset(have) or len(have) > len(want)):
            return False
        for duration in ['8/20', '30/60']:
            if duration in p and not re.search(r'(?<!\d)(?<!\d[.,])' + duration.replace('/', r'\s*/\s*') + r'(?!\d)(?![.,]\d)', text(c)):
                return False
        return True
    if 'наибольшее' in p:
        return 'наиболь' in h and 'длительно' in h and ('напряж' in h)
    if 'номинальноенапряжение' in p:
        return 'номиналь' in h and 'напряж' in h and ('классиф' not in h)
    if 'зарядпропускной' in p:
        return 'заряд' in h and 'пропуск' in h
    if 'тепловойзаряд' in p:
        return 'теплов' in h and 'заряд' in h
    if 'тепловаяэнергия' in p:
        return 'теплов' in h and 'энерги' in h
    if 'токимпульса' in p:
        return 'ток' in h and '4/10' in h
    if 'разрушающаянагрузка' in p:
        return 'разрушающ' in h and 'нагрузк' in h
    if p == 'сечение':
        return 'сечени' in h
    if 'исходныйсмешанныйстолбец' in p:
        return 'сечени' in h and 'диаметр' in h
    if p == 'рис.':
        return 'рис' in h and len(h) < 25
    if 'класснапряжениясети' in p:
        return 'класс' in h and 'напряж' in h and ('сети' in h)
    if 'строительнаявысота' in p:
        return 'строитель' in h and 'высот' in h
    if 'изоляционнаявысота' in p:
        return 'изоляцион' in h and 'высот' in h
    if 'длинапутиутечки' in p:
        return 'путьутечки' in h or ('длина' in h and 'утечки' in h)
    if p == 'масса':
        return 'масса' in h
    if 'степеньзагрязнения' in p:
        return 'степень' in h and 'загрязнен' in h
    if 'нормированнаяразрушающаясила' in p:
        return 'разрушающ' in h and 'изгиб' in h
    if 'интервалдиаметров' in p:
        return 'диаметр' in h and 'провод' in h
    if 'токвзрывобезопасности' in p:
        duration = '0,2' if '0,2' in p else '2'
        return 'взрывобезопас' in h and duration + 'с' in h and (duration == '0,2' or '0,2с' not in h)
    return False

def unit_matches(f, c):
    want = f.get('unit')
    h = text(c)
    if not want:
        return (True, None)
    if f.get('unit_policy') == 'faithful_original_combination':
        raw = c.get('unit') or text(c)
        u = norm(raw).replace('²', '2')
        ok = 'мм2' in u and re.search('мм(?!2)', u) is not None
        return (ok, None if ok else 'Original mixed mm²/mm unit combination lost.')
    explicit = c.get('unit')
    suffixes = {'мм²': ['мм²', 'мм2', 'мм 2'], 'кДж/кВ': ['кДж/кВ'], 'кВ': ['кВ'], 'кН': ['кН'], 'кА': ['кА'], 'Кл': ['Кл'], 'мм': ['мм'], 'см': ['см'], 'кг': ['кг'], 'А': ['А']}.get(want, [want])
    found = any((re.search('(?<![а-яА-ЯA-Za-z])' + re.escape(x) + '(?![а-яА-ЯA-Za-z²\\d])', h) for x in suffixes))
    if not found and want == 'мм²':
        found = 'мм' in h and re.search('мм\\s*(?:²|2)', h) is not None
    note = None
    if explicit and norm(explicit) != norm(want):
        note = f'Column.unit={explicit!r} conflicts with expected physical unit {want!r}; semantic unit may remain recoverable from header/group.'
    return (False if note else found, note)

def eligible_table(cid, loc, d):
    if cid.startswith('catalog-1') or cid.endswith('185'):
        idx = 0 if loc.startswith('top') else 1
        return [(idx, d['tables'][idx])] if len(d['tables']) > idx else []
    return list(enumerate(d.get('tables', [])))

def check(cid, f, d):
    base = dict(expected=f, status='missing', reason='No matching model / parameter association.', candidate_evidence=[], literal_value_match=None, normalization=None)
    loc = f['location']
    ent = f['entity']
    tables = eligible_table(cid, loc, d)
    if 'drawings' in loc:
        want = str(f['value'])
        figs = d.get('figures', [])
        tokens = [norm(x) for x in re.split(';\\s*', want)]
        cand = []
        for (i, fig) in enumerate(figs):
            tx = ' '.join([fig.get('title', ''), fig.get('description', '')] + fig.get('labels', []))
            nt = norm(tx)
            if 'lower' in loc and '1,1' not in tx and ('1.1' not in tx):
                continue
            if 'IV' in ent and (not re.search('\\bIV\\b', tx)):
                continue
            if 'вид А' in loc and (not re.search('(?:вид|по)\\s*А\\b', tx, re.I)):
                continue
            if 'вид Б' in loc and (not re.search('(?:вид|фланца\\s*\\()\\s*Б\\b', tx, re.I)):
                continue
            for tok in tokens:
                tok = tok.replace('Ø', 'φ')
                nt = nt.replace('Ø', 'φ')
                if not re.search(r'(?<![\d.,])' + re.escape(tok) + r'(?![\d.,])', nt):
                    break
            else:
                cand.append((i, fig))
        if not cand:
            return base
        ev = [dict(figure_index=i, title=g.get('title'), labels=g.get('labels'), description=g.get('description')) for (i, g) in cand]
        base['candidate_evidence'] = ev
        base.update(status='passed', reason='Matching lower charge-group/execution/view figure contains selected dimension or hole tokens with source association; drawing unit accuracy explicitly unscored in source-v2.', literal_value_match=True, normalization='figure_dimension_association', unit_scoring_scope='unscored_no_explicit_source_legend')
        return base
    if 'header' in loc and f['parameter'] == 'subcolumn list':
        if not tables:
            return base
        (ti, t) = tables[0]
        cols = [(j, c) for (j, c) in enumerate(t['columns']) if re.search(r'(?<![\d.,])30/60(?![\d.,])', text(c)) and 'остающ' in alpha(text(c))]
        have = set().union(*(amps(text(c)) for (j, c) in cols)) if cols else set()
        want = amps(f['value'])
        base['candidate_evidence'] = [dict(table_index=ti, table_id=t['id'], column_index=j, column=c) for (j, c) in cols]
        base.update(status='passed' if have == want else 'wrong', reason=f'Communutation subcolumn conditions expected {sorted(want)}, observed {sorted(have)}; no search in row values.', literal_value_match=have == want, normalization='condition_list')
        return base
    common = ent.startswith('все ') or ent.startswith('обе модели')
    manufacturer = 'АРМАТЕХ' if 'АРМАТЕХ' in loc else 'ENSTO' if 'ENSTO' in loc else 'МЗВА' if 'МЗВА' in loc else None
    expected_count = int(re.search('\\d+', ent).group()) if ent.startswith('все ') else 2 if ent.startswith('обе модели') else None
    entitynames = ent.split(';') if ';' in ent else [ent]
    matches = []
    weak = []
    for (ti, t) in tables:
        for (j, c) in enumerate(t['columns']):
            if not header_matches(f, c) or not clean_header(c):
                continue
            if cid.endswith('060') and manufacturer and (manufacturer not in text(c) + ' ' + t['title']):
                continue
            for (ri, r) in enumerate(t['rows']):
                idcols = {col['id'] for col in t['columns'] if re.search(r'(Наименование|Обозначение|Тип|Марка|АРМАТЕХ|ENSTO|МЗВА)', text(col), re.I) and not header_matches(f, col)}
                vals = [str(x.get('value') or '') for x in r['cells'] if x['column_id'] in idcols]
                identity = common or any((any((norm(n) == norm(v) for v in vals)) for n in entitynames))
                cell = next((x for x in r['cells'] if x['column_id'] == c['id']))
                if cid.endswith('060'):
                    identity = False
                    for k in range(max(0, j - 2), j):
                        ic = t['columns'][k]
                        if manufacturer not in text(ic):
                            continue
                        icell = next((x for x in r['cells'] if x['column_id'] == ic['id']))
                        names = str(icell.get('value') or '').split('\n')
                        found = [a for (a, name) in enumerate(names) if any((norm(n).replace('С', 'C') == norm(name).replace('С', 'C') for n in entitynames))]
                        if not found:
                            continue
                        identity = True
                        lines = str(cell.get('value') or '').split('\n')
                        if len(names) > 1 and len(lines) == len(names) and (len(found) == 1):
                            cell = {**cell, 'original_composite_value': cell.get('value'), 'value': lines[found[0]], 'normalization_note': 'source-cell ordered line pairing, names/value counts equal', 'matched_identity_line': found[0]}
                        elif len(lines) > 1:
                            identity = False
                        break
                if common and (not any(('ОПН-П-' in v if cid.startswith('catalog-1') or cid.endswith('185') else 'ОЛСКИР-' in v for v in vals))):
                    identity = False
                if not identity:
                    continue
                matches.append((ti, t, ri, j, c, cell))
    if not matches:
        return base
    byrow = collections.Counter(((ti, ri) for (ti, t, ri, j, c, cell) in matches))
    if any((n > 1 for n in byrow.values())):
        base.update(status='ambiguous', reason='Multiple plausible physical parameter columns per matching model; not independently mapped.')
    else:
        problems = []
        modes = []
        literal = True
        warnings = []
        if expected_count and len(byrow) != expected_count:
            problems.append(f'Expected {expected_count} model rows, matched {len(byrow)}.')
        if ';' in ent and len(byrow) != len(entitynames):
            problems.append('Shared fact model range incomplete.')
        for (ti, t, ri, j, c, cell) in matches:
            (ok, mode) = valmatch(cell.get('value'), f['value'])
            literal = literal and globals()['literal'](cell.get('value')) == globals()['literal'](f['value']) and (not cell.get('original_composite_value'))
            modes.append(mode)
            if cell.get('normalization_note'):
                modes.append('source_ordered_line_pairing')
            if not ok:
                problems.append(f"Value row{ri}: expected{f['value']!r}, actual{cell.get('value')!r}.")
            if cell.get('state', 'value') != 'value':
                problems.append(f"Cell row{ri} state{cell.get('state')} cannot stand for printed literal{f['value']!r}.")
            (uok, note) = unit_matches(f, c)
            if not uok:
                problems.append(f"Physical unit{f.get('unit')!r} not explicit in column/unit/header/group.")
            if note:
                warnings.append(note)
            if 'не менее' in f['parameter'] and set(re.findall(r'не\s+(?:менее|более)', text(c), re.I)) != {'не менее'}:
                problems.append('Source minimum qualifier omitted.')
            if cid.endswith('060') and ('сечени' in alpha(text(c)) and 'диаметр' in alpha(text(c))) and (f.get('unit_policy') != 'faithful_original_combination'):
                problems.append('Composite section/diameter header does not disambiguate the field/unit.')
        base.update(status='wrong' if problems else 'passed', reason='; '.join(dict.fromkeys(problems)) if problems else 'Correct model/row, unambiguous parameter and condition, value/state and recoverable explicit unit.', literal_value_match=literal, normalization=sorted(set((x for x in modes if x))), schema_warnings=sorted(set(warnings)), raw_semantic_recoverability=dict(value_and_identity=not any((x.startswith('Value ') or 'model rows' in x or 'range incomplete' in x or ('state' in x) for x in problems)), unit_in_header=all((unit_matches(f, {**c, 'unit': None})[0] for (ti, t, ri, j, c, cell) in matches))))
    base['candidate_evidence'] = [dict(table_index=ti, table_id=t['id'], row_index=ri, column_index=j, column=c, cell=cell, row_identity_values=[x.get('value') for x in t['rows'][ri]['cells'] if isinstance(x.get('value'), str) and ('ОПН' in x['value'] or 'ОЛСКИР' in x['value'] or x['value'] in entitynames)]) for (ti, t, ri, j, c, cell) in matches]
    return base

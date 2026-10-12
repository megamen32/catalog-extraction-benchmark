"""Selected armature and insulator facts with explicit source-reviewed row scopes."""
import re
from .header_rules import clean_header
from decimal import Decimal, InvalidOperation
TRANS = str.maketrans("АВЕНКМОРСТХУ", "ABEHKMOPCTXY")
UNITS = ["мм", "мм²", "м", "кг", "кН", "кН·м", "кВ", "мкСм", "Гц", "кН/кВ"]

def norm(v):
    return re.sub('\\s+', '', str(v if v is not None else '')).replace('–', '-').replace('−', '-')

def glyph(v):
    return norm(v).translate(TRANS)

def fieldglyph(v):
    raw = glyph(v)
    converted = raw.translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789'))
    return converted if converted in {'d1', 'd2', 'd3', 'L1', 'L2', 'L3', 'B1', 'B2'} else raw

def equal(a, b):
    if glyph(a) == glyph(b):
        return True
    try:
        return Decimal(norm(a).replace(',', '.')) == Decimal(norm(b).replace(',', '.'))
    except InvalidOperation:
        return False

def field_matches(f, c):
    if not clean_header(c):
        return False
    label = c.get('label', '')
    group = c.get('group') or ''
    col = f['column']
    short = col.split(',')[0]
    leaf = label.split('/')[-1].split(',')[0].strip()
    if short in ['b', 'B', 'd', 'd1', 'd2', 'd3', 'D', 'H', 'L', 'L1', 'L2', 'L3', 'h*', 'B1']:
        return fieldglyph(leaf) == fieldglyph(short) or fieldglyph(group.split(',')[0].strip()) == fieldglyph(short)
    patterns = {'Масса': 'Масса', 'Масса, не более': 'Масса', 'Рис.': 'Рис', 'Марка троса': 'Марка.*троса', 'Исполнение': 'Исполнение', 'Разрушающая нагрузка, не менее': 'Разрушающая.*нагрузка', 'Номинальное напряжение': 'Номинальн.*напряжен', 'Нормированная разрушающая сила при изгибе': 'разрушающая.*сила.*изгиб', 'Нормированная разрушающая сила на изгиб': 'разрушающая.*сила.*изгиб', 'Полный грозовой импульс': '(полн.*грозов.*импульс|грозов.*импульс)', 'Удельная поверхностная проводимость слоя загрязнения': 'поверхностная.*(проводимость|загрязнения)', 'Допустимая степень загрязнения': 'степень.*загрязнения', 'Строительная высота H, не более': 'Строительная.*высота', 'Высота шпильки h': 'Высота.*шпильки', 'Изоляционная высота L, не менее': 'Изоляционная.*высота', 'Длина пути утечки, не менее': 'Длина.*пути.*утечки', 'Длина пути тока утечки': 'Длина.*пути.*утечки', '50Гц под дождем': '50.*Гц.*дождем', 'Фарфоровый аналог': 'Фарфоровый.*аналог'}
    text = ' '.join((label + ' ' + group).split())
    return bool(re.search(patterns.get(col, '^' + re.escape(col) + '$'), text, re.I))

def identity_cell(col):
    txt = ' '.join((str(col.get('label', '')) + ' ' + str(col.get('group') or '')).split())
    return bool(re.search('(Наименование|Обозначение|Наименования|Марка зажима|Тип зажима)', txt, re.I))

def resolve(cid, d, f, index):
    names, wire, part = f['scope']['products'], f['scope'].get('conductor'), f['scope'].get('part')
    out = []
    coverage = set()
    for (ti, t) in enumerate(d['tables']):
        cs = t['columns']
        idcols = [c['id'] for c in cs if identity_cell(c)]
        if not idcols:
            continue
        fields = [c for c in cs if field_matches(f, c)]
        for (ri, row) in enumerate(t['rows']):
            vals = {x['column_id']: x for x in row['cells']}
            rownames = [n for n in names if any((glyph(vals[x]['value']) == glyph(n) for x in idcols))]
            if not rownames:
                continue
            coverage.update(rownames)
            if wire:
                wirelist = wire if isinstance(wire, list) else [wire]
                wirecs = [c for c in cs if re.search('провода', c['label'], re.I)]
                if not any((any((glyph(vals[c['id']]['value']) == glyph(w) for w in wirelist)) for c in wirecs)):
                    continue
            if part:
                partcs = [c for c in cs if re.search('Деталь', c['label'], re.I)]
                if not any((norm(vals[c['id']]['value']) == norm(part) or (norm(part).startswith('корп') and norm(vals[c['id']]['value']).startswith('корп')) for c in partcs)):
                    continue
            for c in fields:
                cell = vals[c['id']]
                out.append({'table_index': ti, 'table_id': t['id'], 'row_index': ri, 'column_id': c['id'], 'column': c, 'cell': cell, 'product_names': rownames, 'path': f"tables[{ti}].rows[{ri}].cells[{next((j for (j, x) in enumerate(row['cells']) if x['column_id'] == c['id']))}]"})
    return (names, out, coverage)

def units(c, expected):
    if expected is None:
        return (None, 'source_unit_unspecified')
    if c.get('unit'):
        return (c['unit'] == expected, 'explicit_unit')
    literal = ' '.join([c.get('label') or '', c.get('group') or ''])
    found = set(re.findall(r'(?<![А-Яа-яA-Za-z])(?:' + '|'.join(re.escape(u) for u in sorted(UNITS,key=len,reverse=True)) + r')(?![А-Яа-яA-Za-z²/·])', literal))
    return (found == {expected}, 'literal_header_or_group' if found else 'missing_unit')

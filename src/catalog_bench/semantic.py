"""Engineering matches require a scoped identity, clean field, state, value and conditions."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import re
import unicodedata

from .profiles import arm_iz, opn_small
from .profiles.header_rules import clean_header, semantic_header_text


def normalized(value):
    if value is None:
        return None
    value = ''.join(c for c in unicodedata.normalize('NFC', str(value)) if unicodedata.category(c) != 'Cf')
    return ' '.join(value.split()).replace('–', '-').replace('−', '-')


def equivalent(actual, expected):
    a, b = normalized(actual), normalized(expected)
    if a == b:
        return True
    if a is None or b is None:
        return False
    try:
        return Decimal(a.replace(',', '.')) == Decimal(b.replace(',', '.'))
    except InvalidOperation:
        return False


def column_match(annotation, column):
    raw = normalized(' '.join(filter(None, [column.group, column.label])))
    folded = semantic_header_text(raw + ' ' + (normalized(column.qualifier) or ''))
    field = all(bool(re.search(r'(?<![\d.,])' + re.escape(token), folded)) if token[:1].isdigit() else token in folded for token in annotation.get('tokens', []))
    inline_group = None
    if annotation.get('symbol'):
        # Scoped aliases for dimension fields only; product names and grade СЗ stay literal.
        symbol = normalized(column.label).split('/')[-1].split(',')[0].strip()
        prefix = column.label.split('/')[:-1]
        wanted_group = annotation.get('group')
        if wanted_group:
            # One complete parent/leaf path may be represented in label instead of group.
            # An explicit conflicting group still takes precedence below.
            match = re.fullmatch(re.escape(wanted_group) + r'\s+([^/]+)', symbol)
            if match:
                symbol = match.group(1).strip()
                inline_group = wanted_group
            elif any(normalized(p) == wanted_group for p in prefix):
                inline_group = wanted_group
        field = arm_iz.fieldglyph(symbol) == arm_iz.fieldglyph(annotation['symbol'])
        if inline_group:
            leaf = normalized(column.label).split('/')[-1]
            suffix = leaf.partition(',')[2].strip()
            if suffix and suffix != annotation.get('unit'):
                field = False
        if any(not re.fullmatch(r'(?:основные\s+|присоединительные\s+)?размеры(?:,?\s*мм)?|(?:верхний|нижний)\s+фланец', p.strip(), re.I) for p in prefix):
            field = False
    if annotation.get('group'):
        field = field and (normalized(column.group) or inline_group) == annotation['group']
    # Several voltage conditions or leaf dimensions collapsed into a header are ambiguous.
    conditions = [r'полн.*грозов.*импульс', r'50.*гц.*сухом', r'50.*гц.*дождем', r'разрядн.*загрязн']
    if sum(bool(re.search(p, folded)) for p in conditions) > 1:
        field = False
    leaves = [arm_iz.fieldglyph(x.strip().split(',')[0]) for x in column.label.split('/')]
    dimension_names = {'b', 'B', 'D', 'd', 'd1', 'd2', 'd3', 'H', 'L', 'L1', 'L2', 'L3', 'B1', 'B2'}
    if sum(x in dimension_names for x in leaves) > 1:
        field = False
    physical_fields = [r'механич.*разруш.*сил', r'разруш.*крутящ.*момент',
                       r'строитель.*высот', r'диаметр.*ребер', r'изоляцион.*высот',
                       r'длина.*пути.*утечки', r'номиналь.*напряж', r'разрядн.*напряж',
                       r'выдержив.*напряж', r'поверхностн.*провод', r'степень.*загряз',
                       r'масса', r'классизолятора']
    if sum(bool(re.search(p, folded)) for p in physical_fields) > 1:
        field = False
    expected_unit = annotation.get('unit')
    explicit = normalized(column.unit) or None
    if explicit is not None:
        unit = explicit.replace('•', '·') == expected_unit
    elif expected_unit is None:
        unit = True
    else:
        pattern = r'(?<![\w])(?:кН/кВ|кН[·•]м|мкСм|мм²|мм|кВ|кН|кг|м)(?![\w/·•])'
        observed = {u.replace('•', '·') for u in re.findall(pattern, raw)}
        unit = observed == {expected_unit}
    with_qualifier = raw + ' ' + (normalized(column.qualifier) or '')
    bounds = set(re.findall(r'не\s+(?:менее|более)', with_qualifier, re.I))
    expected_bound = annotation.get('qualifier')
    bounds_ok = bounds == ({expected_bound} if expected_bound else set())
    expected_frequency = annotation.get('frequency_hz') or (50 if '50гц' in annotation.get('tokens', []) else None)
    frequencies = set(re.findall(r'(?<![\d.,])(\d+(?:[.,]\d+)?)\s*Г\s*ц\b', with_qualifier, re.I))
    frequency_ok = not expected_frequency or frequencies == {str(expected_frequency)}
    return {'field': field and clean_header(column), 'unit': unit, 'bounds': bounds_ok, 'frequency': frequency_ok}


def score_table_facts(case, content):
    checks = []
    for ti, (gold, annotations) in enumerate(zip(case.tables, case.semantic_columns)):
        table = content.tables[ti] if ti < len(content.tables) else None
        for ri, row in enumerate(gold.rows):
            candidates = []
            if table:
                identities = [c for c in table.columns if column_match(annotations[0], c)['field']]
                for index, observed_row in enumerate(table.rows):
                    cells = {c.column_id: c for c in observed_row.cells}
                    if any(cells[c.id].state == 'value' and normalized(cells[c.id].value) == normalized(row[0]) for c in identities):
                        candidates.append((index, cells))
            for ci, expected in enumerate(row):
                check = {'id': f't{ti}-r{ri}-c{ci}', 'identity': row[0], 'field': annotations[ci]['field'], 'expected': expected, 'status': 'missing'}
                if len(candidates) > 1:
                    check.update(status='ambiguous', reason='Duplicate product rows in the scoped table')
                elif candidates and table:
                    possible = [(c, column_match(annotations[ci], c)) for c in table.columns if column_match(annotations[ci], c)['field']]
                    if len(possible) > 1:
                        check.update(status='ambiguous', reason='Multiple matching engineering fields')
                    elif possible:
                        column, meaning = possible[0]
                        cell = candidates[0][1][column.id]
                        expected_state = 'blank' if expected is None else 'value'
                        value_ok = cell.state == expected_state and equivalent(cell.value, expected)
                        passed = value_ok and all(meaning.values())
                        check.update(status='passed' if passed else 'wrong', observed=cell.value,
                                     observed_state=cell.state, value_and_state=value_ok,
                                     literal_match=cell.state == expected_state and normalized(cell.value) == normalized(expected),
                                     conditions=meaning, column_id=column.id, row_index=candidates[0][0])
                checks.append(check)
    return checks


def score_arm_fact(case_id, fact, data, index):
    names, records, _ = arm_iz.resolve(case_id, data, fact, index)
    base = {'id': f'selected-{index+1:02}', 'expected': fact, 'status': 'missing', 'evidence': records}
    if not records:
        return base
    if set(names) - {n for r in records for n in r['product_names']}:
        return {**base, 'reason': 'Missing members of the source-reviewed product group'}
    by_row = Counter((r['table_index'], r['row_index']) for r in records)
    if any(n > 1 for n in by_row.values()) or len({(r['table_index'], r['column_id']) for r in records}) > 1:
        return {**base, 'status': 'ambiguous', 'reason': 'Multiple field or table interpretations'}
    problems = []
    for record in records:
        cell, column = record['cell'], record['column']
        label = column['label']
        leaves = [x.strip().split(',')[0] for x in label.split('/')]
        dimensions = {'b','B','D','d','d1','d2','d3','H','L','L1','L2','L3','B1','h*'}
        combined = ' '.join(str(column.get(k) or '') for k in ['label', 'group', 'qualifier'])
        if sum(x in dimensions for x in leaves) > 1 or sum(bool(re.search(p, combined, re.I)) for p in ['полного.*грозового.*импульса','50.*Гц.*сухом','50.*Гц.*дождем']) > 1:
            return {**base, 'status': 'ambiguous', 'reason': 'Composite header collapses independent fields'}
        state = 'blank' if fact['kind'] == 'blank' else 'value'
        if cell['state'] != state or not arm_iz.equal(cell['value'], fact['expected']):
            problems.append('value_or_state')
        if arm_iz.units(column, fact['unit'])[0] is False:
            problems.append('unit')
        if fact['column'] == 'Удельная поверхностная проводимость слоя загрязнения' and not re.search('проводимость', combined, re.I):
            problems.append('field_meaning')
        required_bound = 'не менее' if 'не менее' in fact['column'] else 'не более' if 'не более' in fact['column'] else None
        if required_bound and set(re.findall(r'не\s+(?:менее|более)', combined, re.I)) != {required_bound}:
            problems.append('source_bound')
    return {**base, 'status': 'wrong' if problems else 'passed', 'issues': sorted(set(problems))}


def score_facts(case, content):
    checks = score_table_facts(case, content)
    data = content.model_dump()
    for i, fact in enumerate(case.selected_facts):
        if case.selected_profile == 'opn-small':
            result = opn_small.check(case.id, fact, data)
            checks.append({'id': f'selected-{i+1:02}', **result})
        else:
            checks.append(score_arm_fact(case.id, fact, data, i))
    counts = dict(Counter(c['status'] for c in checks))
    return {'correct': counts.get('passed', 0), 'expected': len(checks),
            'percent': round(100*counts.get('passed', 0)/len(checks), 2) if checks else None,
            'statuses': counts, 'checks': checks, 'full_page_accuracy': False}

"""Recognize ambiguity in known engineering field vocabularies, without a model judge."""
import re

# Hierarchical groups may describe one leaf; unrelated leaves must not collapse.
FIELD_PATTERNS = [
    r'наиболь.*длительно.*напряж', r'номиналь.*напряж',
    r'механич.*разруш.*сил', r'разруш.*крутящ.*момент',
    r'строитель.*высот', r'диаметр.*ребер', r'изоляцион.*высот',
    r'длина.*пути.*утечки', r'разрядн.*напряж', r'выдержив.*напряж',
    r'поверхностн.*провод', r'(?:объемн.*провод|проводимостьобъемн)', r'степень.*загряз', r'масса', r'классизолятора',
    r'заряд.*пропуск', r'теплов.*заряд', r'теплов.*энерги',
    r'разруш.*нагруз', r'ток.*взрывобезопас', r'остающееся',
]

def semantic_header_text(raw):
    folded = re.sub(r'\s+', '', raw).casefold().replace('ё', 'е')
    # Equivalent noun/adjective order for this one unambiguous quantity.
    # This is matching-only; delivered labels, units and values stay literal.
    return folded.replace('удельнаяпроводимостьповерхностногослоязагрязнения',
                          'удельнаяповерхностнаяпроводимостьслоязагрязнения')


def clean_header(column):
    get = column.get if isinstance(column, dict) else lambda k, default=None: getattr(column, k, default)
    raw = ' '.join(str(get(k) or '') for k in ['label', 'group', 'qualifier'])
    folded = semantic_header_text(raw)
    if sum(bool(re.search(p, folded)) for p in FIELD_PATTERNS) > 1:
        return False
    voltage_conditions = [r'полн.*грозов.*импульс', r'50.*гц.*сухом', r'50.*гц.*дождем']
    if sum(bool(re.search(p, folded)) for p in voltage_conditions) > 1:
        return False
    segments = str(get('label') or '').split('/')
    dimensions = {'b','B','D','d','d1','d2','d3','H','L','L1','L2','L3','B1','B2','h*'}
    last = segments[-1].split(',')[0].strip().translate(str.maketrans('₁₂₃ВН','123BH'))
    if last in dimensions:
        allowed = r'(?:основные\s+|присоединительные\s+)?размеры(?:,?\s*мм)?|(?:верхний|нижний)\s+фланец'
        if any(not re.fullmatch(allowed, prefix.strip(), re.I) for prefix in segments[:-1]):
            return False
    return True

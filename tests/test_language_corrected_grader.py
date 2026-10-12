"""Fast unit: eliminate symbol/language bias while retaining source/scope guards.
Expected1s/max10s; no model calls, all frozen candidates and fixtures read-only.
"""
import copy,json
from pathlib import Path
from catalog_bench.dataset import fixture_path
from catalog_bench.language_corrected_grader import score_language_corrected,geometry_aliases,language_assertions
from catalog_bench.drawing import score_drawing_assertions

PUBLIC=Path('examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1')

def score(tmp_path,cid,data):
 p=tmp_path/'candidate.json';p.write_text(json.dumps(data,ensure_ascii=False));return score_language_corrected(fixture_path(cid,'engineering-catalogs-v2'),p)

def drawing(tmp_path,text,title='Вид Б',check='outer140',page=39):
 cid=f'catalog-1-page-{page:03d}';a=json.loads(fixture_path(cid,'engineering-catalogs-v2').read_text())['drawing_assertions'];a=next(x for x in language_assertions(a) if x['id']==check);return score_drawing_assertions([a],{'figures':[{'title':geometry_aliases(title),'description':geometry_aliases(text),'labels':[]}]})['checks'][0]['status']

def test_real_latin_amp_and_english_geometry_are_not_false_missing(tmp_path):
 p=PUBLIC/'catalog-1-page-039/catalogue-page.json';before=p.read_bytes();d=json.loads(before);r=score(tmp_path,'catalog-1-page-039',d)
 checks={x['id']:x for x in r['engineering_facts']['checks']};assert checks['selected-04']['status']=='passed';assert checks['selected-09']['status']=='passed'
 draw={x['id']:x['status'] for x in r['drawing_assertions']['checks']};assert draw['outer140']=='passed';assert draw['pitch116']=='passed';assert draw['ring500']=='wrong';assert p.read_bytes()==before

def test_false_pass_shields_for_scope_numbers_negation_and_owner(tmp_path):
 assert drawing(tmp_path,'flange diameter ⌀2140')=='missing'
 assert drawing(tmp_path,'flange diameter ⌀140',title='View A')=='missing'
 assert drawing(tmp_path,'⌀140 is not the outer contour.')=='missing'
 assert drawing(tmp_path,'⌀140 is an inner diameter.')=='wrong'
 assert drawing(tmp_path,'⌀116 outer circle.',check='pitch116')=='wrong'
 assert drawing(tmp_path,'⌀500 is not the cross-arm tube diameter.',check='ring500')=='missing'
 assert drawing(tmp_path,'View A: plate width ⌀50.',title='Вид А',check='dimension50-faces')=='missing'

def test_units_do_not_change_current_condition_or_product_identity(tmp_path):
 d=json.loads((PUBLIC/'catalog-1-page-039/catalogue-page.json').read_text());c=next(c for c in d['tables'][0]['columns'] if '250' in c['label']);c['label']=c['label'].replace('250','1250');r=score(tmp_path,'catalog-1-page-039',d);assert r['engineering_facts']['checks'][3]['status']!='passed'
 d=json.loads((PUBLIC/'catalog-1-page-039/catalogue-page.json').read_text());d['tables'][0]['rows'][0]['cells'][0]['value']='ОПН-П-150/110/10/1,6-IV УХЛ1';r=score(tmp_path,'catalog-1-page-039',d);assert r['engineering_facts']['checks'][3]['status']=='missing'

def test_metric_thread_script_alias_is_literal_only_and_composite_headers_fail(tmp_path):
 d=json.loads((PUBLIC/'catalog-4-page-078/catalogue-page.json').read_text());r=score(tmp_path,'catalog-4-page-078',d);checks={x['id']:x for x in r['engineering_facts']['checks']}
 assert checks['t1-r0-c4']['status']=='passed' and checks['t1-r0-c4']['literal_match'] is False
 assert checks['t0-r0-c13']['status']=='passed';assert checks['t0-r0-c8']['status']!='passed';assert checks['t0-r0-c9']['status']!='passed'
 assert any(x['classification']=='literal_script_only_physical_thread_equivalent' for x in r['literal_format_differences'])
 assert any(x['classification']=='contextual_header_abbreviation_typo' for x in r['literal_format_differences'])
 assert r['metrics']['cells_literal']['correct']<r['metrics']['cells_literal']['expected']

def test_thread_quantity_and_identity_aliases_are_not_global(tmp_path):
 d=json.loads((PUBLIC/'catalog-4-page-078/catalogue-page.json').read_text())
 for c in d['tables'][1]['rows'][0]['cells']:
  if c.get('value')=='4M16':c['value']='4M18'
 r=score(tmp_path,'catalog-4-page-078',d);check=next(x for x in r['engineering_facts']['checks'] if x['id']=='t1-r0-c4');assert check['status']=='wrong'
 d=json.loads((PUBLIC/'catalog-1-page-039/catalogue-page.json').read_text());c=next(c for c in d['tables'][0]['columns'] if '250' in c['label']);c['unit']='kA';r=score(tmp_path,'catalog-1-page-039',d);assert r['engineering_facts']['checks'][3]['status']=='wrong'

def test_english_endpoint_contradictions_and_charge_scopes(tmp_path):
 assert drawing(tmp_path,'50 plate width, 50 between centers of holes.',title='View A',check='dimension50-faces')=='wrong'
 assert drawing(tmp_path,'50 upper and lower plate faces.',title='View A',check='dimension50-faces')=='passed'
 assert drawing(tmp_path,'274 lower edge of ring ⌀500.',title='main drawing',check='dimension274-loweredge')=='passed'
 assert drawing(tmp_path,'⌀274 lower edge of ring ⌀500.',title='main drawing',check='dimension274-loweredge')=='missing'
 assertions=json.loads(fixture_path('catalog-1-page-027','engineering-catalogs-v2').read_text())['drawing_assertions'];a=next(x for x in language_assertions(assertions) if x['id']=='12-III-outer140')
 for title in ['11.2 Кл III View B','1.2 Кл IV View B']:
  data={'figures':[{'title':geometry_aliases(title),'description':geometry_aliases('flange diameter ⌀140'),'labels':[]}]};assert score_drawing_assertions([a],data)['correct']==0

def test_thread_rescue_requires_all_explicit_source_conditions(tmp_path,monkeypatch):
 import catalog_bench.language_corrected_grader as grader
 from catalog_bench.semantic import score_facts as original
 def no_conditions(case,content):
  result=original(case,content)
  for check in result['checks']:
   if check['id']=='t1-r0-c4':check.pop('conditions',None)
  return result
 monkeypatch.setattr(grader,'score_facts',no_conditions)
 d=json.loads((PUBLIC/'catalog-4-page-078/catalogue-page.json').read_text());r=score(tmp_path,'catalog-4-page-078',d);check=next(x for x in r['engineering_facts']['checks'] if x['id']=='t1-r0-c4');assert check['status']=='wrong'

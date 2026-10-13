"""Fast unit: fixed denominators and source receipt binding; max 10 seconds."""
import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('retained_compare',Path(__file__).parents[1]/'ops/compare-retained-agent-profiles-v033.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_missing_pages_keep_full_denominator():
 r=m.totals([{'engineering_correct':10,'drawing_correct':1,'candidate':'saved'}, {'engineering_correct':0,'drawing_correct':0,'candidate':None}])
 assert r['engineering_expected']==520 and r['drawing_expected']==21 and r['selected_pages']==17
 assert r['valid_pages']==1 and r['engineering_percent']==100*10/520

def test_source_mismatch_cannot_publish(tmp_path):
 p=tmp_path/'candidate.json';p.write_text('{}')
 origin={'status':'receipt_verified','source_bound_save':True,'source_sha256':'other','physical_page':27,'role':'extractor','artifact_sha256':m.sha(p)}
 with pytest.raises(AssertionError):m.verified({'source_sha256':'expected','physical_page':27},p,origin)

def test_artifact_mismatch_cannot_publish(tmp_path):
 p=tmp_path/'candidate.json';p.write_text('{}')
 origin={'status':'receipt_verified','source_bound_save':True,'source_sha256':'source','physical_page':27,'role':'extractor','artifact_sha256':'wrong'}
 with pytest.raises(AssertionError):m.verified({'source_sha256':'source','physical_page':27},p,origin)

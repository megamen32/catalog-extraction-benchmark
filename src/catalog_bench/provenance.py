"""Version and method evidence belongs to each execution, never an inferred current checkout."""
import math
from pathlib import Path
import hashlib


def elapsed(value):
    return float(value) if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0 else None


def tested_program(receipt=None, declared_version=None):
    receipt=receipt or {};state=receipt.get('project_state') or {}
    return {'git_revision':receipt.get('project_revision') or state.get('git_revision'),
            'package_version':receipt.get('package_version'),
            'declared_version':declared_version or state.get('declared_version'),
            'contract_sha256':receipt.get('contract_sha256'),
            'dirty':state.get('dirty'), 'tracked_diff_sha256':state.get('tracked_diff_sha256'),
            'version_evidence':'execution_receipt' if receipt else 'unavailable'}


def archive_artifact(candidate, destination):
    candidate=Path(candidate);destination=Path(destination)
    data=candidate.read_bytes();digest=hashlib.sha256(data).hexdigest()
    relative=Path('artifacts')/(digest+'.json');path=destination/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=data:raise ValueError('Archived artifact digest collision')
    if not path.exists():path.write_bytes(data)
    if candidate.read_bytes()!=data:raise ValueError('Candidate changed while being archived')
    return str(relative),digest

"""Reuse an existing protected credential bridge; never store its environment.

Only replace its final executable target with the pinned benchmark bootstrap.
The original bridge still loads credentials through its documented protected path.
"""
import os
from pathlib import Path
import runpy
import sys
bridge,bootstrap,plan=sys.argv[1:]
original_exec=os.execvpe

def execute_benchmark(file,argv,environment):
    if file!=sys.executable or argv[:3]!=[sys.executable,'-m','catalog_json.cli']:
        raise ValueError('Protected bridge executable contract changed')
    original_exec(file,[file,bootstrap,plan],environment)

os.execvpe=execute_benchmark
sys.argv=[bridge]
runpy.run_path(bridge,run_name='__main__')

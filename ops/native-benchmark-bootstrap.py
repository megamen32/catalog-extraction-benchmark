"""Import the frozen benchmark module without changing child PYTHONPATH."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from catalog_bench.mixed_runner import main
main()

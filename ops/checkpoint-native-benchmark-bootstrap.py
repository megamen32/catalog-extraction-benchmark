"""Separate checkpoint controller; child native imports remain unchanged."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from catalog_bench.checkpoint_mixed_runner import main
main()

"""Import the separately frozen corrected benchmark, leaving child imports native."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from catalog_bench.corrected_mixed_runner import main
main()

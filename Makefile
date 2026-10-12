.PHONY: check
check:
	timeout 180 sh -ec 'uv sync --locked; uv run pytest -q; uv run catalog-bench dataset; uv run python -c "import tempfile; from pathlib import Path; from catalog_bench.demo import run_demo; p=Path(\".tmp\"); p.mkdir(exist_ok=True); print(run_demo(Path(tempfile.mkdtemp(prefix=\"demo-\",dir=p))))"; uv build --out-dir .tmp/dist'

# Catalog Extraction Benchmark

Compare PDF catalogue parsers against independently reviewed engineering facts.

- **15 difficult pages** from five catalogues, including the rotated tables on page 78.
- **500 source-reviewed facts**: product identity, parameter, unit, condition and value.
- Compare canonical page JSON and externally supplied products/characteristics/families JSONL.
- Run explicit **project × model** matrices with bounded execution and reusable artifacts.
- Keep literal transcription, engineering correctness and annotation coverage separate.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/megamen32/catalog-extraction-benchmark@v0.2.0
```

## Try it

```bash
catalog-bench dataset
catalog-bench demo --output results/demo
catalog-bench score --case catalog-4-page-078 page-78.json --output results/score.json
```

The demo is synthetic and needs no model credentials. The reviewed dataset ships with the package; original PDFs and extraction outputs are supplied locally and are **not distributed**. A perfect selected-fact score does not establish full-page correctness.

## Compare your solutions

Export annotations with `catalog-bench dataset --export annotations`, then follow the [adapter guide](docs/ADAPTERS.md) to run an executable parser or import saved JSONL results. The benchmark does not require either competing parser to be installed for grading.

[Dataset and annotation coverage](docs/DATASET.md) · [Scoring rules](docs/SCORING.md) · [Source audit and errata](docs/ANNOTATIONS.md) · [Contributing](CONTRIBUTING.md)

[Ready-made solutions and measured parser results](docs/READY-SOLUTIONS.md)

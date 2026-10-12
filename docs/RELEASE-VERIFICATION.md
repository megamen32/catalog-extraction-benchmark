# v0.1.0 release verification

The public GitHub tag was installed through the advertised `uv tool install git+https://github.com/megamen32/catalog-extraction-benchmark@v0.1.0` command using a fresh isolated tool directory and cache.

- Installed CLI reports version 0.1.0.
- Packaged dataset validates all 15 cases, 500 assertions and frozen checksums.
- Installed synthetic demo completes four project/model arms, discriminates the incorrect unit and resumes without changing artifacts.
- Installed CLI grades actual saved page-78 artifacts from both compared formats using the same fixture and deterministic grader. Inputs and reports remain private.
- 37 fast unit/focused integration tests passed; ordinary check, synthetic consumer demo and wheel/source build completed within the 180-second check budget.
- Wheels contain all 15 fixtures and no supplied PDFs, screenshots, spreadsheets, JSONL dumps or private messages.

The repository is public with default branch main, and release assets include the wheel, source archive and SHA256SUMS. Automatic GitHub Actions is not enabled: the existing publishing credential lacks workflow scope. The ready CI template is `examples/ci-check.yml`; maintainers can use `make check` immediately.

Evaluation scope remains partial: source-reviewed table bodies on three pages and selected source assertions on the other twelve pages. These proofs validate the benchmark delivery, not perfect extraction of entire catalogues.

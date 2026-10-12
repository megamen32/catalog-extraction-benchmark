# Contribute a parser or source-reviewed case

Submit an argv adapter that receives source PDF, physical page, explicit model selection and fresh output directory, then writes canonical page JSON without benchmark answers in its prompt. A saved-result-only submission must keep model/runtime/cost unknown unless supported by an actual execution receipt.

For new cases, record source SHA-256, physical and printed page, exact field/unit/qualifier/value/state assertions, selected difficulty reasons and precise coverage. Review the original page independently of candidate outputs; have a second source reviewer check ambiguous rotated labels and merged groups. Preserve visible source typos. Never infer units, identities or missing candidate values from gold during import.

Changes to source annotations or grading rules need an erratum, dataset/grader version bump and regression proof. Do not silently compare old and new aggregate scores. Provide either licensed redistributable documents or user-supplied local inputs; do not upload private PDFs, chat, screenshots, credentials or candidate artifacts into this repository.

Development:

```bash
uv sync --locked
make check
```

Fast unit tests and focused subprocess/CLI integration share a 180-second ordinary check deadline. Slow live model runs are manual benchmark workloads, not release tests or automatic CI calls.

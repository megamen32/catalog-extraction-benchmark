# Compare extraction projects

## Grade an existing page

```bash
catalog-bench score --case catalog-4-page-078 candidate.json --output results/page78-score.json
```

Candidates use [PageContent](../src/catalog_bench/schema.py): ordered tables, explicit column labels/groups/units/qualifiers, rectangular rows with `value`, `blank` or `unknown` states, and figures with declared labels. A catalogue wrapper with `source.sha256` and `pages[].pdf_page/content` is also accepted and its source binding is verified. A plain page requires caller-selected source binding; the grader reports this limitation.

## Import the external JSONL format

Place the three saved exports outside version control:

```bash
catalog-bench import-jsonl \
  --products inputs/products.jsonl \
  --characteristics inputs/characteristics.jsonl \
  --families inputs/families.jsonl \
  --document-id src03 --page 78 --output results/external-page78
catalog-bench score --case catalog-4-page-078 \
  results/external-page78/candidate.json --output results/external-page78-score.json
```

The received baseline uses `src01` for armature, `src02` for insulators, `src03` for innovations, `src04` for the small catalogue and `src05` for OPN. These IDs are a property of that export; other exporters must supply their actual mapping.

The importer selects the exact document and physical page, preserves supplied raw fields/units and coordinates, obtains identities only from matching reported product observations, and retains unresolved conflicts as `unknown`. Missing evidence is never a source blank. It does not expand source merges, split composite fields into corrected fields, or infer drawing labels. `import.json` records byte hashes and original-to-candidate coordinate mapping. An imported result has **unknown model, latency, tokens and cost**, and is not a program execution.

## Compare saved results

Write a local manifest:

```json
{
  "artifacts": [
    {"project": "external-saved", "case_id": "catalog-4-page-078", "stage": "imported_result", "model": null, "candidate": "external-page78/candidate.json", "receipt": "external-page78/import.json"},
    {"project": "my-parser", "case_id": "catalog-4-page-078", "stage": "first_pass", "model": "your-exact-model-id", "candidate": "my-page78/candidate.json", "receipt": "my-page78/run.json"}
  ]
}
```

```bash
catalog-bench compare results/comparison-inputs.json --output results/comparison.json
```

Paths are relative to the manifest. A receipt is optional for an arbitrary saved page; without it model selection is merely declared. With a receipt, hashes and source/page/model binding must agree. Receipt verification does not independently re-execute the parser or authenticate its provider. Stages remain separate in the report. An imported baseline may not claim a verified model.

## Run a project × model matrix

1. Supply the original PDFs locally. Exact input hashes must match the chosen fixtures.
2. Export the frozen annotations: `catalog-bench dataset --export annotations`.
3. Adapt [suite.example.json](../examples/suite.example.json) to the parser's checkout, version and exact model IDs.
4. Run the manifest:

```bash
catalog-bench run suite.json --output results/matrix
catalog-bench run suite.json --output results/matrix --resume
catalog-bench report results/matrix/results.json --output results/summary.json
```

The example uses `catalog-to-json`'s first-pass CLI. Install and configure that parser separately. Both GLM and MiniMax can be selected using the exact model IDs resolved by the parser/provider; this benchmark performs no model discovery or fallback. Another solution needs only an executable adapter accepting `{source}`, `{page}`, `{model}` and `{run_dir}`, and writing canonical page JSON to its declared artifact path. Do not claim a fresh runtime comparison for a solution supplied only as JSONL.

Commands are argv arrays, not shell expressions. Every adapter must explicitly receive `{model}`. Gold is consumed by the parent grader and is not passed to the adapter. `model_receipt`, when configured, must include `status=completed`, `model`, `source_sha256`, `physical_page` and `candidate_sha256` matching the artifact. Put adapter outputs under `extraction/`; the benchmark reserves the run directory's `run.json` for its own receipt.

Runs are sequential with per-run and whole-suite deadlines. Only the runner's own process group is stopped on timeout. Failed and interrupted runs remain visible and are not replayed automatically. Resume regrades verified immutable outputs under the current fixture/grader digest; changed artifacts and dirty project state invalidate reuse. Every execution retains project revision or declared version, command inputs, source/artifact hashes and stage. Unknown runtime outcomes require manual reconciliation and a deliberately new run directory after that reconciliation.

The answer keys are public. Preventing access to them is an evaluation procedure: use a separate working directory, no fixture context in prompts, freeze raw first-pass artifacts before grading, and disclose any repair/judge stage. This runner is not a sandbox that conceals public gold from an untrusted adapter.

## Retained experiment record

Every matrix run records the executed Git revision/declared version, optional parser package/contract version, expanded argv, model, stage, timeout/deadline/repetition policy, immutable output path/hash, measured elapsed time and grader/fixture hashes. Reports include accuracy and per-case errors alongside the tested versions and method. Saved-result comparison copies exact candidate bytes to a content-addressed sibling `<report-name>-files/artifacts/` directory. It preserves executed version and elapsed time from a bound runtime receipt; missing external version/time remain null. Outputs and reports are retained locally outside Git by default. No chat transcripts are required by the benchmark.

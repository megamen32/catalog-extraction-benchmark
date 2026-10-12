# Catalog Extraction Benchmark

## What This Is

An independent public benchmark for engineering PDF catalog extraction. It evaluates competing extraction projects, including catalog-to-json and externally supplied JSONL results, against source-reviewed annotations on 15 difficult pages across five catalogues.

## Core Value

Compare both solutions with the same frozen source-grounded rules, without repairing candidates using the answer key.

## Requirements

### Validated

Public release v0.1.0 installs from its GitHub tag; the standalone dataset, demo and real saved-artifact grading work.

### Active

- [x] Publish an independent installable benchmark with versioned annotations.
- [x] Score canonical JSON and imported saved JSONL results consistently.
- [x] Run arbitrary project × model matrices with immutable receipts.
- [x] Preserve partial coverage and unknown runtime information explicitly.

### Out of Scope

- Publishing supplied PDF files, screenshots, private messages or historical model outputs.
- Implementing another extraction agent or selecting a model automatically.
- Claiming full-page correctness from selected table facts.

## Context

The benchmark was developed alongside catalog-to-json. The difficult anchor is physical page 78 of the 2021–2022 innovations catalogue. Source-only audits reviewed all 15 selected pages independently before comparison; source annotation errata are retained in this repository. External JSONL dumps are saved results with unavailable program source.

## Constraints

- **Public inputs**: annotations and hashes only; users supply matching PDFs locally.
- **Execution**: bounded sequential subprocesses, explicit model selection and no automatic replay of unknown runs.
- **Delivery**: public GitHub repository, reproducible installation, checks and versioned release.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Independent benchmark package | Neither competing parser owns grading | Verified |
| Publish source-reviewed facts, keep raw documents private | Reproducible grading without distributing user attachments | Verified |
| Separate literal, engineering and coverage metrics | Equal numbers can belong to different fields or conditions | Verified |

---
*Last updated: 2026-10-12 after initialization*

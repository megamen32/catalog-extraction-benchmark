# Requirements: Catalog Extraction Benchmark

**Defined:** 2026-10-12
**Core Value:** Compare extraction projects against independent frozen source annotations.

## v1 Requirements

### Dataset

- [x] **DATA-01**: User can inspect 15 source-bound cases with physical/printed page distinction and annotation coverage.
- [x] **DATA-02**: User can score the verified three table bodies and selected facts on the other 12 pages.

### Evaluation

- [x] **EVAL-01**: User can grade canonical page JSON and import external JSONL without source-driven repairs.
- [x] **EVAL-02**: User can run a project × model matrix with hashes, bounded processes and safe resume.
- [x] **EVAL-03**: Reports preserve missing/ambiguous/invalid results and separate literal from engineering matches.

### Release

- [x] **SHIP-01**: User can install a pinned public release and execute a complete synthetic demo without model credentials.
- [x] **SHIP-02**: Public files contain no supplied documents, screenshots, private chat or historical candidate outputs.

## v2 Requirements

- [ ] **NOM-01**: Score product selection for one source-bound ForEnergo tender against actual submitted products or independent engineer decisions; tender input text alone is not gold.
- [ ] **NOM-02**: Distinguish exact match, expert-review equivalent, insufficient data, no candidate, and false recommendation; false positives and safe abstentions are explicit.
- [ ] **NOM-03**: Retain tender/catalogue/standard source identities and row-level evidence without publishing customer files.
- [ ] **NOM-04**: Report precision, false-positive count, recall/coverage, abstention reasons, and Excel integrity separately; preserve prior 500/520 cohorts.
- [ ] **DOC-01**: A later independent benchmark consumes an approved selection workbook and grades submission forms against versioned templates and supporting evidence.

The owner assigned NOM-01..04 to the current task. DOC-01 is recorded for the next stage only.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full-page perfectness score | Prose and complete diagram semantics lack full independent annotations |
| Model billing inference | Saved outputs do not prove model, latency or cost |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| EVAL-01 | Phase 2 | Complete |
| EVAL-02 | Phase 2 | Complete |
| EVAL-03 | Phase 2 | Complete |
| SHIP-01 | Phase 3 | Complete |
| SHIP-02 | Phase 3 | Complete |
| NOM-01 | Phase 4 | Pending source-bound oracle and candidate output |
| NOM-02 | Phase 4 | Grader implemented; end-to-end run pending labels/output |
| NOM-03 | Phase 4 | Input hashes and row evidence in private intake; STО evidence missing |
| NOM-04 | Phase 4 | Metrics implemented; selection/Excel outcome pending |
| DOC-01 | Phase 5 | Roadmap only |

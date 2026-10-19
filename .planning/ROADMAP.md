# Roadmap: Catalog Extraction Benchmark

## Overview

Package the reviewed difficult-page dataset, deliver independent grading and adapters, then verify installation and publish a public release.

## Phases

- [x] **Phase 1: Frozen dataset** - Publish reviewed source facts and explicit coverage.
- [x] **Phase 2: Independent evaluator** - Deliver grading, saved-result import and project/model execution.
- [x] **Phase 3: Public release** - Verify real installation and publish versioned repository.
- [ ] **Phase 4: Forenergo nomenclature-selection benchmark** - Compare tender requirements with the ForEnergo product catalogue and score safe selection/abstention on one source-grounded procurement with a retained selection or engineer-labeled outcome.
- [ ] **Phase 5: Submission-document generation benchmark** - Independently grade filled application forms derived from an approved selection workbook.

## Phase Details

### Phase 1: Frozen dataset
**Goal**: Users can inspect the source-bound 15-case dataset and its source errata.
**Depends on**: Nothing
**Requirements**: [DATA-01, DATA-02]
**Success Criteria**:
  1. All 15 annotations validate and contain source hashes and physical page indices.
  2. Complete table-body coverage and selected-fact coverage are distinguished.
**Plans**: 1 plan

Plans:
- [x] 01-01: Sanitize and freeze independently reviewed annotations.

### Phase 2: Independent evaluator
**Goal**: Users can compare both extraction formats through one evaluator.
**Depends on**: Phase 1
**Requirements**: [EVAL-01, EVAL-02, EVAL-03]
**Success Criteria**:
  1. Both native JSON and saved JSONL can be graded without extraction dependencies.
  2. Source conditions, units, identity and value state affect engineering scores.
  3. A resumed matrix does not silently repeat external work.
**Plans**: 1 plan

Plans:
- [x] 02-01: Package graders, adapters, runner and focused checks.

### Phase 3: Public release
**Goal**: Users can install a pinned public version and run it.
**Depends on**: Phase 2
**Requirements**: [SHIP-01, SHIP-02]
**Success Criteria**:
  1. Clean installation and synthetic matrix demo succeed.
  2. Public GitHub repository and versioned release exist without private attachments.
**Plans**: 1 plan

Plans:
- [x] 03-01: Document, independently review, publish and verify installation.

### Phase 4: Forenergo nomenclature-selection benchmark
**Goal**: Determine whether the system can safely choose exact ForEnergo products for a real procurement and explain missing/uncertain matches.
**Depends on**: Phase 3; uses a separate tender-selection dataset and does not change extraction score cohorts.
**Requirements**: [NOM-01, NOM-02, NOM-03, NOM-04]
**Status**: Active / partial. A private source-derived intake workflow and strict grader are implemented. The current private case has been structurally read back, but its saved candidate lacks producer/version metadata and no independent outcome/engineer labels are present. Accuracy remains unscored. One cited source standard is absent and a filename disagrees with its internal title; exact evidence stays in the ignored private audit. Earlier crosswalk counts remain source-integrity results for a different input set, not selection accuracy.
**Success Criteria**:
  1. Every scored row has source evidence and an oracle from actual submitted goods or explicit independent engineer adjudication.
  2. Unsupported matches are counted as false positives; incomplete information yields a safe abstention and is reported separately.
  3. One retained candidate output is scored with product/version provenance; Excel row and formula integrity is verified.
  4. Original documents stay private; public benchmark artifacts contain only permitted, source-bound labels and compact results.

### Phase 5: Submission-document generation benchmark
**Goal**: Measure how accurately the system turns an approved selection workbook into versioned application documents.
**Depends on**: Phase 4 and a frozen approved workbook, current form templates, supporting documents, and independently checked completed examples.
**Requirements**: [DOC-01]
**Status**: Planned; not part of Phase 4 acceptance.
**Success Criteria**:
  1. Field-level form values trace to the approved workbook or evidence document.
  2. Missing values remain visible for human review; unsupported certifications, declarations, and commercial claims are never invented.
  3. Templates open correctly and preserve required structure/formulas; form accuracy is scored independently from product-selection accuracy.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Frozen dataset | 1/1 | Complete | 2026-10-12 |
| 2. Independent evaluator | 1/1 | Complete | 2026-10-12 |
| 3. Public release | 1/1 | Complete | 2026-10-12 |
| 4. Forenergo nomenclature selection | 0/1 | In progress | — |
| 5. Submission document generation | 0/1 | Planned | — |

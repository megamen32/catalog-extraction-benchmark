# Roadmap: Catalog Extraction Benchmark

## Overview

Package the reviewed difficult-page dataset, deliver independent grading and adapters, then verify installation and publish a public release.

## Phases

- [x] **Phase 1: Frozen dataset** - Publish reviewed source facts and explicit coverage.
- [x] **Phase 2: Independent evaluator** - Deliver grading, saved-result import and project/model execution.
- [x] **Phase 3: Public release** - Verify real installation and publish versioned repository.

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

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Frozen dataset | 1/1 | Complete | 2026-10-12 |
| 2. Independent evaluator | 1/1 | Complete | 2026-10-12 |
| 3. Public release | 1/1 | Complete | 2026-10-12 |

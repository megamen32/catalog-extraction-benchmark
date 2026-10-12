# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-12)

**Core value:** Compare extraction projects against independent frozen source annotations.
**Current focus:** Phase 3 — Public release

## Current Position

Phase: 3 of 3 (Public release)
Plan: 1 of 1 in current phase
Status: Complete
Last activity: 2026-10-12 — Fixed drawing token/view scoring in v0.2.1; frozen model executions remain unchanged.

Progress: [██████████] 100%

## Accumulated Context

### Decisions

Keep raw documents, private chat and historical model outputs outside the public repository. Provide JSONL import without claiming a fresh executable project run.

### Pending Todos

None for this release.

### Blockers/Concerns

No source code is available for the external saved-results baseline. This does not block grading its supplied artifacts.

## Session Continuity

Last session: 2026-10-12
Stopped at: Public release installed, dataset/demo and real artifact grading verified; requested delivery complete.
Resume file: None

## Release verification

v0.1.0 is public. Clean installation from the public tag, dataset verification, synthetic 4-arm execution/resume and grading of saved artifacts from both solutions succeeded. 37 tests passed. CI template is in examples because the publishing credential lacks workflow scope; local make check is available. Original documents and historical outputs remain excluded.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|---|---|---|---|
| 261012-9vv | Fix drawing token boundaries and reject swapped views | 2026-10-12 | 437b5ba | [261012-9vv](./quick/261012-9vv-fix-drawing-token-boundaries-without-cha/) |
| 261012-b7d | Recognize equivalent conductivity headers; reject composite fields | 2026-10-12 | pending | [261012-b7d](./quick/261012-b7d-recognize-equivalent-conductivity-header/) |

Owner permission on 2026-10-12 explicitly allows publication of public catalogue JSON examples and compact benchmark outputs with actual program versions. Raw logs, transcripts, credentials and model weights remain excluded. Historical releases and frozen grader cohorts are preserved.

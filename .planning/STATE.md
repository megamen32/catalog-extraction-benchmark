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
| 261012-b7d | Recognize equivalent conductivity headers; reject composite fields | 2026-10-12 | d2649e5 | [261012-b7d](./quick/261012-b7d-recognize-equivalent-conductivity-header/) |

Owner permission on 2026-10-12 explicitly allows publication of public catalogue JSON examples and compact benchmark outputs with actual program versions. Raw logs, transcripts, credentials and model weights remain excluded. Historical releases and frozen grader cohorts are preserved.

## Repeated frozen cohorts,2026-10-12

One fresh1.4.4 cohort saved14/15 pages and368/500 chosen facts; failed33 remains0/108. Its parent interruption17 recovered only a completed source-bound adapter artifact, with native duration explicitly separated. Outputs/metadata public; no transcripts. Added independently reviewed repeatability runner: mandatory frozen bindings, at least3 rounds, adaptive bounded concurrency and retained429/failure cases. Fresh rounds2/3 for1.4.2 and1.4.4 pending; single-trial results do not choose a winner.

## Grader 0.2.4, 2026-10-12

Confirmed false-negative: an unambiguous source parent dimension group moved into the same label was rejected despite all 140 literal cells matching. The grader now recognizes the complete parent/leaf path while rejecting conflicting parents, longer or composite symbols, conflicting units and added conditions. The frozen 500-fact dataset and model outputs are unchanged. Historical 0.2.3 scores remain retained; all 90 attempts will be regraded separately with released 0.2.4 after the running third round completes.

The 0.2.3 distribution had a stale 0.2.2 module/CLI version. Release 0.2.4 synchronizes package and module versions. Focused RED regressions and 52 passing tests, plus independent adversarial review, verified this source slice. Public release 0.2.4 was downloaded and independently installed: distribution, module and CLI all report 0.2.4; release wheel matches the published build.

## Three-round cohort complete, 2026-10-12

All 90 attempts finished; 84 exact final JSON outputs are retained. Round 1 is the explicitly retained historical cohort, rounds 2 and 3 are 60 fresh calls, with round 3 beginning only after all round-2 attempts finished. The bounded worker exited normally. No benchmark 429 was observed in retained fresh logs; SDK retries and concurrent catalogue work limit that interpretation.

Released grader 0.2.4 separately regraded every retained output with unchanged source annotations: 1.4.2 scores 483/463/466 out of 500 (mean 94.13%, range 4.0 percentage points, sample SD 2.16); 1.4.4 scores 368/341/345 (mean 70.27%, range 5.4 points, SD 2.91). Historical scores are preserved. Macro catalogue means are 86.96% and 85.23%, showing unequal weighting and non-universal strengths. The 1.4.4 round-3 page-78 result exposed a full-save → one-section edit → finalize data-loss defect; its final empty-table artifact remains scored 0/140, without substitution. Root owns the source-program repair. Source relation/whole-page coverage limits are stated. Publication audit and download/regrade acceptance of all public files are pending.

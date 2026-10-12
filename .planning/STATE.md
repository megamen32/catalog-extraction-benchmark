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

Released grader 0.2.4 separately regraded every retained output with unchanged source annotations: 1.4.2 scores 483/463/466 out of 500 (mean 94.13%, range 4.0 percentage points, sample SD 2.16); 1.4.4 scores 368/341/345 (mean 70.27%, range 5.4 points, SD 2.91). Historical scores are preserved. Macro catalogue means are 86.96% and 85.23%, showing unequal weighting and non-universal strengths. The 1.4.4 round-3 page-78 result exposed a full-save → one-section edit → finalize data-loss defect; its final empty-table artifact remains scored 0/140, without substitution. Root owns the source-program repair. Source relation/whole-page coverage limits are stated.

Independent publication audit passed exact 84 nested references, sizes, hashes and privacy checks. Published cohort revision 8d0ff191a037b5466105840cd7ae4a1207272766 was downloaded: all 84 files and 90 attempts regraded with public release 0.2.4 in 37.7 seconds; installed historical 0.2.3 separately reproduced all historical scores in 37.6 seconds. Candidate/fixture/algorithm hashes, distribution statistics and failed-case denominators passed. Public verification proof is retained beside the report. This repeatability delivery is complete; new source-program versions require fresh frozen rounds and receive no inherited score.

## Three fresh rounds of profile 1.4.6, 2026-10-12

Public A tag/release 89fbc374d2a8e216ea2a5a22ada30d8c87f7cf66 was downloaded and matched against 25 wheel source/skill entries and archive tag inputs. Its 139 main-runtime dependencies match the previous frozen 1.4.4 except catalog-to-json itself. The same parser plugin 0.2.2 and executors were frozen. Separately published runner source 1f3aa3b4f985286524b58252f90c7e43eb885d07 adds three-fresh-round mode, with focused RED/GREEN and 54 passing tests; scoring remains the immutable installed public 0.2.4.

All 45 new attempts finished in 3381.35 wall seconds: 450/469/471 of 500, mean 92.67%, minimum 90%, maximum 94.2%, range 4.2 points, sample SD 2.32. Catalogue macro mean 86.12%. Saved 13/13/15 pages (41 exact outputs), four timed-out attempts retained with zero. No benchmark 429 observed. In first-round failed149/126, no tool errors or save attempts occurred before the Vision-inspection timeout; this is not evidence of new save guards refusing output.

Historical profile 1.4.2/parser plugin 0.2.1 remains above profile 1.4.6/plugin 0.2.2 on observed means (94.13% weighted, 86.96% catalogue macro), without claiming causal core-only or statistically proven superiority from three samples. The previous 90 attempts are immutable. New delivery/hybrid profiles 1.4.7/1.4.8 did not execute in this cohort and inherit no scores. Root and full-catalogue owner received final metrics immediately; source-program deployment/980-page conversion remain their separate ownership. Independent publication audit passed all 41 exact nested output references, SHA, size, fixed denominators and limitations. Public download/regrade acceptance is pending.

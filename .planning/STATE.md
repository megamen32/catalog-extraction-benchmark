## Catalogue-meaning regressions,2026-10-14

Owner Root adds package0.4.0 registry1.0.0:8 retained high-priority failure examples, source hashes/page, exact outputs and native producer/version/time, pending ambiguity excluded. Meaning classification and engineering IDs have5 explicit automatic assertions; grammar/branding/efficiency remain diagnostics, not semantic accuracy gains. Legacy15/500 and17/520+21 datasets unchanged. New context metadata is accepted without changing their field assertions.37 focused checks pass0.24s; actual installed/public CLI proof pending. No model reruns for registration.

# Project State

## Forenergo selection benchmark — started 2026-10-20

The owner asked to build a first benchmark for tender-line-item to ForEnergo SKU
selection, and to record a second, later benchmark for application-document
generation from the approved selection workbook. Current path: Phase 4.

Input files copied read-only into ignored `.tmp/forenergo-benchmark-20261020/originals/`
and SHA-256 checked against their source copies: `Examplepositions.xlsx` (155
numbered, nonempty request rows), corrected
Appendix 3 workbook, ForEnergo catalogue versions 2, 3 and 4, and `message.txt`
meeting summary. Catalogue 4 contains 5,891 product rows and 49,022 characteristic
rows; catalogue 2 contains 6,571 product rows and 55,422 characteristic rows.
These are private inputs and are not going to Git.

Important blocker for scoring: buyer descriptions are not the actual goods
submitted by ForEnergo. No post-award submitted-product map or independent engineer
labels have yet been confirmed. Do not calculate benchmark accuracy from literal
name similarity or from the catalogue itself. The six SТО PDFs and separate tender
technical workbook were absent at this initial intake; see the later Mac M1 source
copy update below. A read-only UserIO helper was tasked with retrieving attachments.

The meeting summary sets a safety-first rule: an unsupported/incorrect product
recommendation is worse than a non-match. Stage 1 grades exact matches, possible
equivalents requiring an engineer, insufficient data, no candidate, and false
recommendations separately. It does not grade full submission-document generation.
DOC-01 and Phase 5 are recorded in ROADMAP; see
`.planning/quick/261020-forenergo-nomenclature-benchmark/PLAN.md`.

## Forenergo selection benchmark continuation — 2026-10-20

The earlier messaging intake lacked technical attachments: the UserIO Telegram media
adapter could not download them and the first Mac Downloads check did not find them.
The owner later supplied their exact folder paths; the present sources and file-title
verification are recorded in the newer section below. No account secrets were used.

An actual saved candidate workbook is now available, but producer/version and an
independently confirmed selected-SKU map are missing. The workbook is retained as an
unattributed artifact; do not score a guessed candidate.

Implemented `src/catalog_bench/forenergo_selection.py`: private intake workbook
generation with a strict typography-only crosswalk and a JSONL scorer. Workbook:
`.tmp/forenergo-benchmark-20261020/forenergo-selection-intake.xlsx`. Source audit:
155 request rows, 153 numbered Appendix 1 rows, 146 exact unique name links, 9
requests without an exact match, and 7 Appendix 1 items without a request match.
Intake accuracy is null and status is `pending_oracle`. The scorer requires source
evidence and explicit `system_id`/`system_version`; it distinguishes false
selection, exact miss, expert review and safe abstention. It reads both JSONL and
the separated gold/candidate columns in the Excel workbook,
and captures model, elapsed time and token usage when supplied. Focused tests: 8
passed. This is input-integrity/benchmark preparation, not a selection-quality score.

Readback verified 155 request rows, 146 exact links, 9 unmatched requests, 7
appendix-only rows and zero formulas. Intake SHA-256:
`b34ced317f007b255d103150fe80cd7b83d7a07167de5a2042cdfcc51c0a4c14`.
A short request for the missing system output, SKU oracle, technical brief and
matching standards now exists as an unsent UserIO draft requiring manual approval.
The package built and was installed into an isolated `.tmp` environment; its Excel
prepare/readback and score commands completed with 155 pending rows and null accuracy.

The full pre-existing test suite currently stops during collection in three tests:
`ownership_corrected_grader` expects frozen 0.3.2 language digest
`f091...`, while its imported current `language_grader_digest()` returns a different
hash. No files in that historical grader path were modified in this task; changing
its digest can affect frozen cohort identity and must be handled as a separate
regrade-safe repair. New scoped selection tests pass.

Next step: obtain producer/version attribution and an engineer-confirmed SKU map or
post-award outcome; then freeze and score the retained output.

## ForEnergo real tender intake — 2026-10-20

The owner pointed to the downloaded source set on Mac M1. All named files were copied
into ignored private `.tmp/` storage and SHA-256 checked against the originals.
`prepare-case` now builds and reads back a private selection intake, preserving row
identity and delivery lines. The saved candidate has no producer/version; all labels
remain pending and accuracy is null. One cited standard is missing and one filename
disagrees with its internal title; exact details stay in the ignored audit. Nothing
was sent or published. The API credential file was not used against an undocumented
endpoint.

## Project Reference

See: .planning/PROJECT.md (extraction release completed 2026-10-12; Phase 4 selection benchmark active 2026-10-20)

**Core value:** Compare extraction projects against independent frozen source annotations.
**Current focus:** Phase 4 — Forenergo nomenclature-selection benchmark

## Current Position

Phase: 4 of 5 (Forenergo nomenclature selection)
Plan: `.planning/quick/261020-forenergo-nomenclature-benchmark/PLAN.md`
Status: Partial; source-derived intake, structural audit and grader are ready; selection scoring awaits candidate provenance and oracle.
Last activity: 2026-10-20 — Private case intake readback passed; structural coverage is reported separately and semantic accuracy remains unscored.

Progress: Phase 3 remains complete; Phase 4 is in progress.

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

Historical profile 1.4.2/parser plugin 0.2.1 remains above profile 1.4.6/plugin 0.2.2 on observed means (94.13% weighted, 86.96% catalogue macro), without claiming causal core-only or statistically proven superiority from three samples. The previous 90 attempts are immutable. New delivery/hybrid profiles 1.4.7/1.4.8 did not execute in this cohort and inherit no scores. Root and full-catalogue owner received final metrics immediately; source-program deployment/980-page conversion remain their separate ownership. Independent publication audit passed all 41 exact nested output references, SHA, size, fixed denominators and limitations. Published cohort revision e3f70b869a34f1e594c60d754bcc607521ebf1cd was independently downloaded: all 41 exact JSON files and 45 attempts regraded by installed public release 0.2.4 in 17.94 seconds. Candidate/fixture/algorithm hashes, retained failures, totals 450/469/471 and distribution statistics passed. public-verification.json records the actual public consumer proof. Benchmark delivery is complete; new full-catalogue/hybrid source profiles remain separately owned and receive no inherited accuracy score.

## Mixed-pipeline evaluation in progress,12Oct2026

Dataset v2 contains17 pages,520 engineering facts and21 source-grounded drawing assertions. Original15fixtures unchanged. Three fresh sequential native142/parser0.2.1→148 GLM Coding Endpoint rounds use scheduler1.4.11 with no audit/gold context. Source fixture and grader independently reviewed. Ordinary checks66PASS7.90s/build. Official MiniMax subscription token quota is exhausted until18:00MSK; model calls wait before active budget starts. ALL980 catalogue queue is not stopped. New mixed accuracy is unknown until this cohort completes; source release alone is not task completion.

## Common leaderboard including catalog-to-json,2026-10-15

Direct owner request supersedes prior orchestrator exclusion. Added four first-pass profiles in a NEW common15/500 snapshot with pinned grader0.3.2:1.4.15 472/470(two rounds, incomplete series);1.4.2 483/463/466;1.4.6 450/469/471;1.4.4 368/341/345. Original24 rows unchanged except new ranks; old snapshot/candidates/gold/native receipts retained. Mean is observed selected-fact performance, not whole-page or final-reviewed accuracy. Current1.5.26 inherits no score. Full initial-extractor provenance excludes later repair substitution; no reviewer attribution.

Focused offline reproduction passed19.883s in1CPU/1GiB/300s; no models/parsers invoked.28 configurations map to18 products/install links. GitHub main readback and all310 snapshot blob hashes verified after source commit f048b6a. History now uses the new snapshot with old fallback. Plan and evidence: `.planning/quick/261015-hcv-include-catalog-to-json-versioned-saved-/`.

# Focused drawing repair trials — 1.4.26

These trials repair retained outputs for physical OPN pages 27 and 39. The original three-round driver encountered a callback failure and recovered completed native receipts without replay. An old round-two call had already completed when round one reopened, so strict sequentiality is not claimed. These are pilot repair trials using retained candidates and feedback. They are **not three fresh 17-page benchmark rounds**, and their selected scores do not establish whole-page correctness.

[Manifest](manifest.json) records exact native program, model, contract, source PDF, physical page, candidate SHA, native receipt hash and duration. Each saved candidate has independent offline 0.3.2 and 0.3.3 score sidecars. Source tables are compared with the retained seed. Tool counts include only events matching that producer's role, attempt, model, source, contract and native time window. Missing logs remain unknown.

Model review and independent source inspection are separate. A candidate rejected by a source-bound independent inspection remains rejected even if its model review passes. Other candidates remain pending until matching independent evidence is delivered; this collector never infers acceptance. Existing native files, the frozen 1.4.15 → 1.4.17 benchmark, its primary 0.3.2 scores and saved results are unchanged.

The read-only collector performs no model calls and publishes no transcripts. Native failures without completed receipts do not produce synthetic saved artifacts or zero token estimates. While trials run, `manifest.json` is an explicitly partial snapshot; completed candidate files remain byte-identical.

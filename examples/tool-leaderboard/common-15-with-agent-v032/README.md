# Common15 leaderboard including catalog-to-json

This is a new offline regrading snapshot on the identical 15 physical pages /500 engineering facts, pinned matching grader 0.3.2 and retained baseline 0.3.0. It adds four measured first-pass agent profiles to the 24 configurations in [the original snapshot](../common-15-v032/manifest.json). Original candidates, native attempts, annotations and that snapshot remain unchanged. No parser or model was called.

- catalog-to-json 1.4.2:483,463,466/500; three retained rounds, MiniMax-M3.1-Flash-Preview medium.
- catalog-to-json 1.4.4:368,341,345/500; three retained rounds, same named model, distinct program/tool contract.
- catalog-to-json 1.4.6:450,469,471/500; three fresh retained rounds, same named model, distinct program/tool contract.
- catalog-to-json 1.4.15:472,470/500; only two retained first-pass rounds, same named model. The planned third is absent, not scored zero. Only the common15 pages are included; the expanded 17-page results and drawings remain separate.

These are complete observed first-pass page sets with failures counted zero, not accepted reviewed deliveries. Later successful repairs do not replace failed initial answers. Reviewer 1.4.17 is not part of these first-pass scores. Current releases do not inherit them.

[manifest.json](manifest.json) retains exact versions, model/protocol, source and candidate hashes, timing coverage and references to both grader outputs. Existing parser/Catalog Vision Backend rows are reused exactly, apart from their ranks. The summary is an observed mean, not proof of statistical superiority or accuracy of whole pages/catalogues.

Legacy timings are sums of per-attempt parent durations. The 1.4.15 timings are completed native extractor durations; a missing duration stays unknown. Speed comparisons across those definitions are not controlled.

Reproduction requires the released 0.3.0 Python package plus the pinned source 0.3.2 matching module in this checkout. For example, unpack the public 0.3.0 wheel into a local directory and run:

```bash
python ops/add-catalog-agent-leaderboard.py --baseline-package .tmp/frozen030/package
```

The command checks both algorithm fingerprints, every newly graded candidate hash, fixture hashes, fixed page sets and unchanged inputs. Existing same-version output must match; it is never silently replaced. The 28-row snapshot is about 14 MB and contains scores/provenance, not transcripts or source PDFs.

[Published readable ranking](../../../docs/TOOL-LEADERBOARD-RU.md) · [Programs and installation](../../../docs/PRODUCTS-RU.md)

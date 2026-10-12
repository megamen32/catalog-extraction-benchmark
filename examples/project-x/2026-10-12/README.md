# Project X: three fresh PDF parsing rounds

Project X was tested on the 17-page catalogue benchmark with released grader 0.3.0. All 51 attempts completed. Only its deterministic PDF ingestion stage was executed; this is not a score for an untested model-assisted processing pipeline.

| Round | Engineering facts | Drawing assertions | Combined selected assertions | Subprocess wall time |
|---|---:|---:|---:|---:|
| 1 | 21/520 | 0/21 | 3.88% | 36.378 s |
| 2 | 21/520 | 0/21 | 3.88% | 37.509 s |
| 3 | 21/520 | 0/21 | 3.88% | 38.523 s |

Engineering accuracy is 4.04%; drawing coverage is 0%. The scores have zero observed spread across these three deterministic rounds. Mean subprocess duration is about 2.2 seconds per page. Timing includes interpreter/imports, parsing and export; it excludes installation and parent grading. There were zero model calls and zero model tokens; monetary cost was not measured.

On the unchanged original 15-page/500-fact subset, Project X scores 15/500 (3.00%) in every round. Our [historical 1.4.2 extractor profile](../../agent-routing/2026-10-12-repeated-runs/README.md) averaged 94.13% on those same selected facts. This compares a deterministic parser stage against a model-assisted extractor; it is not a causal comparison of parsers alone. The ongoing MiniMax→GLM mixed pipeline has no completed three-round result here yet.

Project X produces structured document blocks and canonical table grids. On page 27, its native grids contain only 10 columns and collapse some narrow/rotated fields. On page 39, the native grid has 16 columns and five rows: two source header rows and three product rows. Its header metadata identifies only one header row and misses some parent/leaf conditions and merged-cell ownership. Page 78 does not produce a canonical table. Native visual extraction did not produce assets for the vector drawing cases, so no Vision accuracy is claimed.

The normalization preserves native header labels/paths and native data-start metadata. It does not infer units, repair table values or substitute benchmark facts. All 51 native JSON outputs were captured inside their actual parsing calls, alongside 51 normalized outputs. Publication removes identifying metadata only; catalogue values remain unchanged. [Manifest and output hashes](manifest.json) and [per-case scores, timing and limitations](results.json) are available for independent regrading.

The participant is identified publicly only as **Project X**. Its source code, actual repository identity, adapter implementation and private snapshot correspondence are not published. The opaque tested snapshot is `ProjectX-snapshot-20261012`.

The [public consumer verification](public-verification.json) downloaded all 102 output files from the immutable public commit, checked their manifest hashes, and reproduced all 51 scores with the installed released grader in an isolated interpreter.

The separate [corrected offline grader 0.3.1 regrade](corrected-grader-v0.3.1.json) reproduces the same 21/520 engineering and 0/21 drawing scores in each round. It fixes a numeric scope boundary in drawing assertions; the original scores, outputs and tested grader remain retained.

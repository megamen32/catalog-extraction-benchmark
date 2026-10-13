# Supplemental drawing audit v1

This separate source audit covers twelve endpoint relationships on physical OPN page 27 and one condition absent from its lower table. It adds no facts to the frozen 17-page benchmark, changes no 0.3.2 or 0.3.3 scores, and produces no new overall percentage.

For each of four charge/execution variants (1.2/1.6 Cl × III/IV), view A prints: 45 between the first two hole centres; 67.5 between the second hole centre and body central axis; 135 between the left plate edge and body central axis. The last dimension is not the full plate length. The lower-table creepage-length column, cm has no minimum condition; the neighbouring thermal-energy column does.

Original PDF source SHA and all thirteen checks are in [the fixture](../fixtures/supplemental/opn27-drawing-v1.json). Root and an independent source auditor confirmed all four drawings; the scorer owner also inspected the original page and enlarged first view. The fixture is strictly offline ground truth and is never supplied to tested agents.

The scorer uses explicit charge/execution in each figure's own title, its own view-A description and individual numeric clauses. It cannot borrow a correct statement from another variant or view. Exact numeric boundaries, local negation and relation ownership prevent common false passes. The lower table is identified by its own 1.6 Cl product identifiers; only its matched creepage column's label, group, qualifier and unit are read. A minimum in the neighbouring energy column is not transferred.

Supported Russian endpoint phrases are deterministic proxies. Unknown, ambiguous or unsupported phrasing is `missing`, a supported contradictory endpoint claim is `wrong`, and a supported correct relationship is `passed`. These checks do not establish full drawing or page correctness. Existing raw outputs and scores are retained unchanged.

[Retained version-1.4.26 examples](../examples/supplemental-drawing-audit-v1/manifest.json) show why this supplement is necessary: candidate 1 lists numbers without their endpoints (twelve missing checks); candidate 2 names twelve incorrect endpoint relationships even though the earlier selected drawing checks improved. Both retain the correct leakage condition. Native source/model/program/contract receipts and all candidate hashes are recorded; regrading calls no model.

Run `python -m catalog_bench.supplemental_drawing_audit --fixture fixtures/supplemental/opn27-drawing-v1.json --output audit.json candidate.json` from this source checkout. The standalone module can also use the original released 0.3.0 wheel and the unchanged released 0.3.2 companion; the companion hash is checked before importing. Ordinary regressions are fast unit checks (expected <1s, maximum15s); public download/regrade is focused integration (maximum180s).

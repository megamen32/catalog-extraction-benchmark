---
phase: quick
plan: 1
status: complete
---

Grader 0.2.2 recognizes the equivalent noun/adjective order of the specific surface-conductivity header without modifying delivered labels, candidate bytes or gold annotations. Independent delta-review found and reproduced a composite surface/volume false positive; shared ambiguity recognition now rejects both composite orders, including the canonical phrase. Wrong units and invented bounds remain rejected.

Validation: 46 tests, dataset checksums (15 cases / 500 selected facts), demo execution/resume and wheel build passed within 180 seconds. Independent retained page33 regrade is 108/108; all15 fixtures,29 candidates and original results hashes unchanged. Provider/parser executions:0. Accuracy refers to selected engineering facts, not complete-page ground truth.

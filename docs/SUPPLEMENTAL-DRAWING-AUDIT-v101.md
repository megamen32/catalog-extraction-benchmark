# Supplemental audit1.0.1: unknown conditions remain missing

This is an offline erratum to the separate [13-check supplemental audit](SUPPLEMENTAL-DRAWING-AUDIT-v1.md), not a new primary benchmark. The frozen17 pages,520 engineering facts,21 drawing assertions, graders032/033 and model contexts are unchanged.

Audit1.0.0 could mark an own leakage-column qualifier such as `at least`, `не более` or `условие неизвестно` as proof that no condition was asserted. Six focused regressions reproduced false passes. Audit1.0.1 retains the released1.0.0 endpoint checks and corrects only that own-column check:

- Empty group/qualifier or a supported explicit statement that the condition is absent can pass.
- A supported unprinted bound is wrong. An unknown nonempty group/qualifier or an unsupported label extension is missing.
- A complete disclaimer does not erase another asserted condition in the same field; the adjacent energy column never contributes the leakage condition.

Supported label wording and absence statements are deliberately limited. This is not a universal semantic evaluator. The correction can reduce credit for unsupported paraphrases; missing means the selected statement was not verified, not that the complete page is factually wrong.

The two retained real candidates have empty leakage qualifiers. Their13-check counts remain1 passed/12 missing and1 passed/12 wrong respectively. The original JSON, audit1.0.0 and primary032/033 sidecars stay unchanged. [New sidecars and exact digests](../examples/supplemental-drawing-audit-v101/manifest.json) record the regrading with zero model calls. Forty-four focused fast-unit cases pass; ordinary verification has a180-second maximum. Public download and standalone regrading proof is delivered separately.

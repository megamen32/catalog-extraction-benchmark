# Offline drawing grader 0.3.3

The 0.3.2 matcher incorrectly treated “отверстие между Ø116 и внешним контуром” as a claim that Ø116 belongs to the outer contour. Those words describe two different objects. The independently checked source annotation remains unchanged: Ø116 is the circle through the four hole centers; Ø140 is the outer contour.

The separate 0.3.3 component excludes only ownership matches crossing the two objects of an explicit `между` / `between` relation, in either order. It applies to positive and contradictory Ø116/Ø140 ownership evidence. A comparison alone is missing ownership evidence, not a passing assertion. Actual “Ø116 — наружный контур,” including explicit ownership inside a comparison, remains wrong. Number, view/group, negation and material guards remain in force. This is a bounded deterministic text proxy, not universal semantic understanding.

Engineering facts, raw literal metrics, candidate bytes, source annotations and retained 0.3.2 scores stay unchanged. The active frozen three-round cohort still uses 0.3.2 as its primary grader. New 0.3.3 scores are separate offline sidecars and perform no model calls.

[Retained regrading outputs](../examples/corrected-results-v033/regrading.json) provide both scores, exact candidate/fixture/grader hashes and changes. The public regression reproducer is the retained source-bound page 39 candidate, rather than a private test dependency.

For an isolated consumer use the original benchmark 0.3.0 wheel and download both `catalog-ownership-grader-v0.3.3.py` and the unchanged `catalog-language-grader-v0.3.2.py` companion from release `corrected-grader-v0.3.3`. Run the ownership script with `--fixture <source-fixture.json> <candidate.json> --output <new-score.json>`. The companion and base algorithm are checked against exact hashes.

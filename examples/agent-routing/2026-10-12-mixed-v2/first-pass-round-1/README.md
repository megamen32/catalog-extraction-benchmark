# Fresh first-pass snapshot: round 1, 17 pages

The exact native MiniMax extractor 1.4.2/parser plugin0.2.1 produced 15/17 valid initial candidates. Missing/failed outputs score zero on the fixed 17-page denominator. First-pass selected engineering accuracy is 399/520; scoped drawing accuracy is 5/21; combined 404/541 (74.68%). Corrected offline grader0.3.1 gives 399/520 + 5/21. Both grader versions and exact candidate bytes are retained.

This measures the first extractor pass before normal GLM reviewer 1.4.8 review/repair, not accepted catalogue delivery. At this snapshot, 0/17 pages were accepted: delivery selected accuracy 0/541. The independent, sequential three-round run continues; no repaired candidate is substituted into these first-pass outputs. No gold or previous output was supplied to the agents. The full-catalogue conversion continues separately.

Selected assertions cover 520 engineering facts and 21 drawing checks, not every statement or whole-page correctness. Compare this stage only against another profile's initial valid candidates on the same 17-page dataset, counting failures zero; it is not the final two-agent result. Native durations and worker-cycle/admission waits are separate in summary.json. Raw transcripts remain private; observed token metrics are collected separately and failed SDK usage may be unknown.

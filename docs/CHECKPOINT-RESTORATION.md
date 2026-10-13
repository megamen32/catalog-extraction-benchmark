# Benchmark restart recovery

The corrected 17-page cohort was interrupted by a server reboot on 13 October. The separate checkpoint controller retains its exact extractor 1.4.15, reviewer 1.4.17, source pages, 148 frozen inputs, and graders 0.3.2/0.3.0. It does not rerun the 17 completed initial extractions.

Every completed producer is verified against its saved artifact, source, physical page, role, model, program and contract. A saved exact completed receipt is reconciled once. An invocation without a completed receipt remains an unknown failure; its external work is never replayed. Unindexed native call directories fail closed. Pages waiting for quota without a native invocation resume their next stage. Accepted and failed pages remain terminal.

The original per-round wall deadline includes downtime. Saved active work and quota hold totals are retained; downtime with no process is reported separately and excluded from active work. Provider rate-limit counts, backoff streaks and current limits survive restoration. Existing production cooldowns and quota holds remain read-only.

The interrupted first round has incomplete reviewed delivery. Initial, available-draft and accepted-delivery scores are reported separately. Unknown invocation duration is a checkpoint lower bound, not a measured final duration. The next two rounds are fresh sequential rounds; no prior candidate, gold or audit hints enter their model contexts.

[Restoration manifest](../examples/agent-routing/2026-10-12-corrected-v032/restart-controller.json) records the controller source digests and retained work. The original frozen runner and plan remain unchanged.

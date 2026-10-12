# Project X catalogue evaluation

Project X was evaluated through its deterministic PDF document route on the
public catalogue corpus. No upstream source, URL, author, package namespace,
private path, command, or provider credential is published here.

Three fresh sequential rounds covered 17 pages each. The adapter preserved native
header metadata and native data-start metadata; it did not infer units or replace
missing table structure with benchmark values. Native JSON and normalized public
JSON are retained in the evaluation evidence under an opaque snapshot mapping.

The deterministic route completed all 51 attempts without model/provider calls.
Its results are recorded in the [three-round report](../examples/project-x/2026-10-12/README.md).
Each round scores 21/520 engineering facts and 0/21 drawing assertions. On the
unchanged original 500-fact subset, each scores 15/500. Vector drawing pages
produced no native image assets, so no vision accuracy claim is made. Interpreter,
parsing and export wall time is retained per attempt; model calls and tokens are
zero, while monetary cost is not measured.


## Model-assisted route and scope

The [full repeated native Vision experiment](../examples/project-x/2026-10-12-native-vision-v1-full/README.md) uses17 pages,520 selected engineering checks and21 drawing assertions. Three complete rounds per model are required. Its own render fallback, catalogue metadata task and provider adapters are explicit modifications; they are not an untouched default deployment of Project X. Scores for that route must not be attributed to its provider-free parser alone or generalized to banking report QA, which this corpus does not test.

Project X has useful native architecture: source/package/document identity checks, typed visual analyses with selected-block provenance, confidence caps for approximate visual evidence, and bounded asset/text context. These are architectural strengths confirmed in the private source review, not independent benchmark scores for every feature.

The engineering-catalogue gaps are specific. Native PDF visual inventory depends on embedded image regions, so vector-only drawings need a render fallback. Canonical table extraction on the tested pages does not reconstruct every rotated or merged header. Native visual analysis is a separate artifact; it does not automatically repair canonical tables. These boundaries existed before the catalogue adapter.

The modified route additionally exposes provider/contract integration weaknesses: the MiniMax Anthropic adapter frequently returns incomplete native JSON; GLM can produce a native accepted sidecar whose nested catalogue metadata fails the stricter page contract. Those are measured integration failures, not proof that MiniMax cannot extract catalogues or that every native Project X operation fails. The small separate OpenAI compatibility probe is not included in the frozen experiment or its ranking.

## Changes worth trying

1. Trigger page rendering when a source has vector diagrams, no usable embedded image, or unresolved structural tables; use rotated detail crops where needed.
2. Validate a dedicated catalogue page/table contract before marking its output complete. Report syntax, native sidecar validation and catalogue contract validation separately; persist every failed attempt for debugging.
3. Extract large tables in bounded pieces with explicit row/column identities instead of relying on one deeply nested whole-page response. Repair model output through the same source-bound route; do not patch answers from benchmark gold.
4. Add a source-grounded second pass that checks dimension ownership, views, units, blanks and unsupported materials/purposes. The current21 drawing checks are limited coverage; high selected-check accuracy does not certify an entire drawing.
5. Add provider-specific admission/backoff and resumable receipts. Preserve failed rate-limited calls in a completed cohort; evaluate scheduling changes in a separately versioned cohort.

The user's public [catalog-to-json](https://github.com/megamen32/catalog-to-json) demonstrates page-bound tools, separate extraction/review roles and resumable source-linked artifacts. This [benchmark](https://github.com/megamen32/catalog-extraction-benchmark) retains source cases, version/settings, outputs, timing, usage and grader versions. These patterns can be reused without treating either project as universally best. Existing historical version results used the earlier500-check subset; they are not expanded520+21 scores and must not be ranked as if their denominators were identical.

# Catalog Vision Backend catalogue evaluation

> [Catalog Vision Backend](CATALOG-VISION-BACKEND.md) — наша закрытая адаптация; репозиторий приватный, доступ по запросу владельцу; планируем предоставлять бесплатно. Оценки ниже относятся к сохранённым конфигурациям испытаний, а не к новому запуску переименованного форка.

Catalog Vision Backend was evaluated through its deterministic PDF document route on the
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

The [full repeated native Vision experiment](../examples/project-x/2026-10-12-native-vision-v1-full/README.md) uses17 pages,520 selected engineering checks and21 drawing assertions. Three complete rounds per model are required. Its own render fallback, catalogue metadata task and provider adapters are explicit modifications; they are not an untouched default deployment of Catalog Vision Backend. Scores for that route must not be attributed to its provider-free parser alone or generalized to banking report QA, which this corpus does not test.

Catalog Vision Backend has useful native architecture: source/package/document identity checks, typed visual analyses with selected-block provenance, confidence caps for approximate visual evidence, and bounded asset/text context. These are architectural strengths confirmed in the private source review, not independent benchmark scores for every feature.

The engineering-catalogue gaps are specific. Native PDF visual inventory depends on embedded image regions, so vector-only drawings need a render fallback. Canonical table extraction on the tested pages does not reconstruct every rotated or merged header. Native visual analysis is a separate artifact; it does not automatically repair canonical tables. These boundaries existed before the catalogue adapter.

The modified route additionally exposes provider/contract integration weaknesses: the MiniMax Anthropic adapter frequently returns incomplete native JSON; GLM can produce a native accepted sidecar whose nested catalogue metadata fails the stricter page contract. Those are measured integration failures, not proof that MiniMax cannot extract catalogues or that every native Catalog Vision Backend operation fails. The small separate OpenAI compatibility probe is not included in the frozen experiment or its ranking.

## Changes worth trying

1. Trigger page rendering when a source has vector diagrams, no usable embedded image, or unresolved structural tables; use rotated detail crops where needed.
2. Validate a dedicated catalogue page/table contract before marking its output complete. Report syntax, native sidecar validation and catalogue contract validation separately; persist every failed attempt for debugging.
3. Extract large tables in bounded pieces with explicit row/column identities instead of relying on one deeply nested whole-page response. Repair model output through the same source-bound route; do not patch answers from benchmark gold.
4. Add a source-grounded second pass that checks dimension ownership, views, units, blanks and unsupported materials/purposes. The current21 drawing checks are limited coverage; high selected-check accuracy does not certify an entire drawing.
5. Add provider-specific admission/backoff and resumable receipts. Preserve failed rate-limited calls in a completed cohort; evaluate scheduling changes in a separately versioned cohort.

The user's public [catalog-to-json](https://github.com/megamen32/catalog-to-json) demonstrates page-bound tools, separate extraction/review roles and resumable source-linked artifacts. This [benchmark](https://github.com/megamen32/catalog-extraction-benchmark) retains source cases, version/settings, outputs, timing, usage and grader versions. These patterns can be reused without treating either project as universally best. Existing historical version results used the earlier500-check subset; they are not expanded520+21 scores and must not be ranked as if their denominators were identical.


## Concrete first-round cases

With GLM, [page27](../examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1/catalog-1-page-027/score-v0.3.1.json) turns source values38 and87,3 and a printed dash into empty cells in the IV execution row. A catalogue-specific merged-cell/row ownership pass should preserve the source distinction between an actual blank, a printed dash and a repeated shared value.

On [page39](../examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1/catalog-1-page-039/score-v0.3.1.json), original graders0.3.0/0.3.1 incorrectly mark the260,0 and284,0 associations missing: the published output has the correct250 A/30–60 condition but uses LatinA. Some English drawing descriptions also describe the source correctly while Russian-only matchers mark them missing. These are benchmark limitations, independently checked against the source, not missing Catalog Vision Backend data. A separate corrected offline0.3.2 regrade is published; original scores remain retained. The claim that⌀500 is a cross-arm tube diameter is a real geometry error: the source dimension spans the outer circular element, not the tube section.

Some [page78](../examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1/catalog-4-page-078/score-v0.3.1.json) penalties are strict literal-script differences:4M16 uses LatinM while the annotated source has CyrillicМ. These should be distinguished from a wrong engineering number. The benchmark retains its exact-literal scores; it does not silently normalize them or certify every drawing label. Real missing header conditions and unscoped geometry remain separate problems.

These are observed first-round examples. The three-round summary is required before claiming a stable mean or recommending a model configuration as the winner.


## Same expanded set: first-round comparison

| Tested initial stage | Valid catalogue JSON | Engineering checks | Drawing checks | Completed fresh rounds shown |
|---|---:|---:|---:|---:|
| Our native extractor1.4.2/plugin0.2.1 | 15/17 | 399/520 (76.73%) | 5/21 (23.81%) | 1 |
| Catalog Vision Backend + GLM5.3Flash, modified native Visionv1 | 14/17 | 380/520 (73.08%) | 4/21 (19.05%) | 1 |
| Catalog Vision Backend + MiniMaxM3.1FlashPreview, modified native Visionv1 | 4/17 | 210/520 (40.38%) | 3/21 (14.29%) | 1 |

The [our first-pass snapshot](../examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-1/README.md) precedes GLM reviewer1.4.8 and normal repairs. It is not an accepted two-role pipeline score: accepted pages at that snapshot are0/17. Catalog Vision Backend is a separate native visual stage with its explicit catalogue adapter and native syntax repair. These rows compare delivered initial-stage outputs on exactly the same17-page corpus and fixed denominators; they do not isolate the causal effect of one model or certify a final reviewed catalogue. The retained original scores reproduce the Catalog Vision Backend rows; corrected0.3.2 results are reported below.

The Catalog Vision Backend experiment has **three rounds for each of two model configurations**, six model-rounds total. Our already-running native extractor→reviewer experiment has its own three rounds. Publishing a first-round snapshot does not start another run. Current scheduler releases1.4.14/1.4.15 retain the same142→148 extraction/review roles; scheduler changes are not new extraction accuracy profiles. Historical144/146 version results on15 pages/500 checks remain historical; they have no expanded17/520+21 result here. No stable winner is declared from this table.


## Integration-format clarification

The frozen MiniMax Anthropic conversion sends the JSON-only task/schema in the prompt but **does not send a provider response_format parameter**. GLM sends itsjson_object parameter. The originally recorded response_format setting is a declared client policy, not evidence that both providers enforce the same JSON mode. Export metadata now distinguishes the declared policy from the actual parameter transmission. This is a comparison of recorded integrations; it does not isolate model capability under identical constrained decoding. Invalid output remains a real delivery failure, but its cause must not be attributed automatically to the unmodified private project or the model alone.


## Final corrected three-round results

All102 Catalog Vision Backend Vision attempts have finished. Primary offline0.3.2 scores are GLM411,456,313 of520 engineering and6,6,7 of21 drawing; MiniMax222,160,247 and3,0,2 respectively. GLM engineering mean75.64%, sample SD14.06 percentage points; MiniMax40.32%, SD8.61. Valid catalogue JSON is47/51 and13/51. The original-score table above is retained history, not the primary current comparison. In corrected first-round comparison our initial extractor scores399/520+5/21 versus Catalog Vision Backend GLM411/520+6/21, so a claim of our large advantage is unsupported. Our reviewed three-round pipeline is not finished.

The [Russian document with source crops](PROJECT-X-REVIEW-RU.md) explains page27 merged-cell loss, page39 dimension ownership, and page78 missing dry-withstand condition and H±2 tolerance. It also distinguishes real errors from English/unit-script grader bias. The [complete cohort](../examples/project-x/2026-10-12-native-vision-v1-full/README.md) retains outputs, failures, settings, timing and all three grader versions. The separate offline page78 format projection scores98/140 without changing table contents; its original failed delivery remains zero in the cohort.


## Historical accuracy and fresh-run regression

Our profile1.4.2's independently reproduced historical results remain483/463/466 of500, mean94.13%, first-round96.6%. Those results have not disappeared. The fresh initial-stage snapshots are399/520 then479/520, plus5/21 then6/21 drawing checks; their final reviewed three-round outcome remains pending. A separate zero-model-call regrade using the unchanged historical500-fact set and released0.2.4 gives381/500 and459/500, exactly matching the current grader on that subset. Thus the first-round drop is not caused simply by the added20 facts or drawing criteria.

On fresh round1 Innovations38, the native142 save/section/finalize sequence destroyed an already saved complete table (72/72 in a diagnostic) after a figure-only update. The original cohort retains its actual final0/72 output. [Same500 regrade](downloads/our-accuracy-history.json) and [source-bound save diagnostic](downloads/our-save-page38-diagnostic.json) document this without substituting intermediate results or starting another model call. The Russian PDF/Word have been corrected to show historical high accuracy, both fresh initial rounds and this real consumer defect prominently. The previous published document verification remains a historical immutable-commit proof.

# Catalog Vision Backend: three repeated Vision rounds per model

> [Catalog Vision Backend](../../../docs/CATALOG-VISION-BACKEND.md) — наша закрытая адаптация; репозиторий приватный, доступ по запросу владельцу; планируем предоставлять бесплатно. Оценки ниже относятся к сохранённым конфигурациям испытаний, а не к новому запуску переименованного форка.

**Complete: 102 fresh attempts, six model-rounds.** Each configuration ran three sequential rounds of the same expanded17-page benchmark:520 selected engineering checks and21 scoped drawing checks. No page78 preview or prior answer was reused. Invalid and failed outputs count zero against the fixed denominator.

Primary results use corrected offline grader0.3.2. Original0.3.0 and0.3.1 scores and byte-preserved candidate files remain available; no model answer was edited by the grader.

| Configuration | Engineering /520: rounds1,2,3 | Drawing /21: rounds1,2,3 | Valid JSON /17: rounds1,2,3 | Engineering mean; sample SD |
|---|---|---|---|---|
| GLM5.3Flash |411;456;313|6;6;7|14;17;16|75.64%;14.06 percentage points|
| MiniMaxM3.1FlashPreview |222;160;247|3;0;2|4;5;4|40.32%;8.61 percentage points|

GLM engineering range is60.19–87.69%; drawing mean30.16%. MiniMax engineering range30.77–47.50%; drawing mean7.94%. These measure delivery of the selected facts, not correctness of every word or dimension on a whole page. MiniMax has31 JSON syntax failures after the native repair,6 native-contract failures and1 catalogue-contract failure. GLM has1 rate limit,1 read timeout and2 catalogue-contract failures. Failure categories remain distinct from transcription errors.

The [manifest](manifest.json) records the opaque source snapshot, integration hash, cases and settings. The [summary](summary.json), per-attempt results, outputs, reported tokens and all grader scores are public. [Artifact hashes](artifact-manifest.json) support independent download and regrading. Raw transcripts and upstream source/identity remain private.

The modified native Vision integration uses a generic catalogue task, whole-page144DPI image and two overlapping216DPI crops. Canonical native tables remain unchanged; visual catalogue metadata is separately validated and exported. GLM uses low effort through its Coding Endpoint; MiniMax uses medium effort through its subscription Anthropic endpoint. Output ceiling32768, temperature1, native syntax repair at most1. One case per model ran concurrently, full rounds sequential within each model. Gold and previous answers were absent from model inputs.

**Format boundary:** GLM sends initial json_object; the frozen MiniMax Anthropic adapter sends JSON-only prompting without a provider response_format parameter. Per-attempt receipts distinguish declared client mode from actual API transmission. This compares integrations, not isolated model ability under identical decoding constraints.

Round subprocess time sums are1990.310;2874.598;2460.509s for GLM and1158.802;1482.897;1084.316s for MiniMax. Imports, preparation and admission waiting are included; provider timing is separate. Usage includes native repair and failed responses where counters were returned. Missing counters are unknown. Monetary cost was not measured.

Our comparable initial first round scores399/520+5/21; Catalog Vision Backend GLM's first round is411/520+6/21. Our three-round reviewed pipeline remains a separate experiment. This does not support a stable overall winner or a claim that our program is much better. Historical500-check scores are not ranked against these520+21 results.

GLM round3 page78 failed the catalogue contract because useful merged_cell_notes extensions were disallowed. Its original delivery remains zero. The separate [offline format diagnostic](format-diagnostic/README.md) retains those notes and evaluates unchanged cells/columns/figures, scoring98/140; it is not a cohort score or a new model run.

See the [Russian source-grounded review](../../../docs/PROJECT-X-REVIEW-RU.md) and [evaluation notes](../../../docs/PROJECT-X-EVALUATION.md).

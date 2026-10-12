# Project X: full repeated Vision benchmark

**Running, not complete: five of six full model-rounds are published.** Two model configurations each run three fresh, sequential rounds of the complete expanded benchmark: 17 pages, 520 selected engineering checks and 21 scoped drawing checks per round. This is 102 attempts, distinct from the earlier page78 integration probes; no probe output is reused.

The configurations are GLM 5.3 Flash at low reasoning effort through the Coding Endpoint and MiniMax M3.1 Flash Preview at medium effort through its subscription Anthropic endpoint. Model calls use the private native visual-analysis integration v1, with the same generic catalogue task, image preparation and output contract. Native canonical tables remain unchanged; extracted catalogue JSON comes from the separately validated visual analysis metadata.

Each model processes all17 cases before its next full round. One case per model may run concurrently. Original source PDFs are the only document inputs; fixtures and earlier results are available only to the parent grader. Completed outputs, failed attempts, actual returned model, elapsed time and reported token usage are retained. Raw provider histories and source code remain private. Invalid or failed attempts count zero delivered correct checks in the fixed full-round denominator.

The [frozen public experiment manifest](manifest.json) records the cases, snapshot, integration hash and settings. Results will retain all three rounds and their spread, with separate original0.3.0 and corrected0.3.1 scores. No finished aggregate accuracy or winner is claimed yet.

The independent [single-page integration probes](../2026-10-12-vision-preview/README.md) establish compatibility and expose remaining errors. They are not a substitute for this full experiment.

## First full round — preliminary

| Configuration | Valid catalogue JSON | Engineering checks (original0.3.0) | Drawing checks (corrected0.3.1) | Subprocess time, all17 attempts |
|---|---:|---:|---:|---:|
| Project X + GLM5.3Flash | 14/17 | 380/520 (73.08%) | 4/21 (19.05%) | 1990.310s |
| Project X + MiniMaxM3.1FlashPreview | 4/17 | 210/520 (40.38%) | 3/21 (14.29%) | 1158.802s |

These are one-round results, **not a final three-round mean or model ranking**. GLM has one rate-limit failure, one read timeout and one invalid catalogue contract. MiniMax has11 syntax failures after its native JSON repair and2 native contract failures. Failure checks count zero; this measures delivered selected-check accuracy under the recorded route, not accuracy conditional on obtaining a usable JSON file. Provider failures and transcription errors remain separate in each round's results.

The [summary](summary.json), both graders' full per-case scores and byte-preserved catalogue outputs are public. An invalid typed catalogue output is retained without manual repair. Raw provider responses and failed syntax output remain privately preserved, with publicly reported failure categories and usage receipts. [Artifact hashes](artifact-manifest.json) allow independent download and regrading. Usage includes native repair calls and failed responses when the provider returned counters; an unreported counter is unknown, not zero. Subprocess time includes imports, preparation and admission wait; provider time is recorded separately. Monetary cost is not measured.

For improvements and interpretation, see the [evaluation notes](../../../docs/PROJECT-X-EVALUATION.md).

## MiniMax: all three original-score rounds complete

Engineering selected-check counts are210,160,239 of520; mean39.04%, sample standard deviation7.69 percentage points, range30.77–45.96%. Drawing counts are3,0,2 of21. Valid catalogue JSON counts are4,5,4 of17 (13/51 combined). Full-round subprocess time is1158.802s,1482.897s,1084.316s. These are the retained original/0.3.1 results; corrected language/symbol evaluation is reported separately, not silently substituted.

GLM has two complete rounds (380/520+4/21 and452/520+6/21;14/17 and17/17 valid JSON). The third is still running, so no final three-round GLM mean is claimed.

**Known evaluation bias:** original0.3.0/0.3.1 miss some correct LatinA ampere labels and English geometry descriptions; strict literal CyrillicМ versus LatinM also differs from physical thread meaning. The separate offline0.3.2 correction retains originals and applies scoped matching-only aliases. First-round corrected results are our399/520+5/21, Project X GLM411/520+5/21, and Project X MiniMax222/520+3/21. Thus the old first-round comparison is not a sound basis for claiming our extraction is better. See the [source-grounded evaluation notes](../../../docs/PROJECT-X-EVALUATION.md).

**API format clarification:** MiniMax's frozen Anthropic adapter uses JSON-only prompting without a provider response_format parameter; GLM sends json_object for initial calls. Per-attempt export now distinguishes declared client format and the actual transmitted provider format. These are integration results, not an isolated comparison of model ability under identical decoding constraints.

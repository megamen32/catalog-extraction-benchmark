# Project X: full repeated Vision benchmark

**Running, not complete.** Two model configurations each run three fresh, sequential rounds of the complete expanded benchmark: 17 pages, 520 selected engineering checks and 21 scoped drawing checks per round. This is 102 attempts, distinct from the earlier page78 integration probes; no probe output is reused.

The configurations are GLM 5.3 Flash at low reasoning effort through the Coding Endpoint and MiniMax M3.1 Flash Preview at medium effort through its subscription Anthropic endpoint. Model calls use the private native visual-analysis integration v1, with the same generic catalogue task, image preparation and output contract. Native canonical tables remain unchanged; extracted catalogue JSON comes from the separately validated visual analysis metadata.

Each model processes all17 cases before its next full round. One case per model may run concurrently. Original source PDFs are the only document inputs; fixtures and earlier results are available only to the parent grader. Completed outputs, failed attempts, actual returned model, elapsed time and reported token usage are retained. Raw provider histories and source code remain private. Invalid or failed attempts count zero delivered correct checks in the fixed full-round denominator.

The [frozen public experiment manifest](manifest.json) records the cases, snapshot, integration hash and settings. Results will retain all three rounds and their spread, with separate original0.3.0 and corrected0.3.1 scores. No finished aggregate accuracy or winner is claimed yet.

The independent [single-page integration probes](../2026-10-12-vision-preview/README.md) establish compatibility and expose remaining errors. They are not a substitute for this full experiment.

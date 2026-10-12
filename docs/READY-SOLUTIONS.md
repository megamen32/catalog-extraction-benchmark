# Ready-made extraction solutions

[The researched list of 24 options](https://github.com/megamen32/catalog-to-json/blob/main/docs/READY-PARSERS.md) includes complete local pipelines, hosted document processors, and existing agent MCP/skill packages. The two independent researchers checked upstream sources on 2026-10-12. Catalogue engineering accuracy is established separately by this benchmark.

## Completed direct-parser experiment

Dataset engineering-catalogs-v1 1.0.0; benchmark implementation v0.2.0 (db192cd); all 15 cases and 500 selected engineering facts. These are joint product/parameter/unit/condition/value assertions, not full-page accuracy.

| Parser | Backend version | Correct facts | Elapsed total | Completed cases |
|---|---|---|---|---|
| Docling | 2.137.0 | 266/500 (53.2%) | 480.070 s | 15/15 |
| PyMuPDF4LLM | 1.28.2 | 13/500 (2.6%) | 419.758 s | 15/15 |

Method: one isolated process per original physical page, native text, OCR disabled, two CPU threads, source-preserving adapter, one repetition, no LLM, no gold-driven repair. Docling used table reconstruction. Docling models were downloaded before the matrix. Time includes process startup and serialization. Both arms attempted the identical case set; no timeout or omitted case was excluded from these totals.

Source adapter: catalog-parser-tools 0.1.0 prototype, in catalog-to-json Git parent 2eed0ad623df7c308f67f65f4bd2a418865aaa8d with dirty=true. The backend receipt records contract SHA-256 8e4837a35478a5ce08e78717cf1a7e1b26d6b2255b6b845070a23ce0d62d2ef6. This experiment is not attributed to the later clean v1.3.0 tag.

On physical page 78 alone, Docling scored 86/140 and PyMuPDF4LLM 0/140. The latter merged two separate tables; its joint-fact score does not mean that no text was extracted.

Every run retains source SHA, physical page, executed command and settings, backend and adapter versions, elapsed time, raw JSON, canonical candidate, artifact SHA and detailed score. Original PDFs and extraction outputs remain local; the public repository distributes annotations, software and aggregate measurements.

## Agent experiment is a separate stage

A first-pass MiniMax-M3.1-Flash-Preview experiment using Docling MCP evidence scored 140/140 engineering facts, 140/140 literal table checks, 11/11 figure-label checks and 3/3 negative label assertions on page 78. Elapsed time was 167.961 s including 103.865 s for a cold Docling call. It tested the modified catalog-to-json 1.3.0 prototype, with original program metadata and a source-hash sidecar retained. It had no reviewer and does not establish complete prose or diagram correctness.

Do not compare that single agent run to direct-parser totals, label it a reviewed conversion, or infer a speed advantage over older runs with different revisions/cache state.

## Next candidates

- LlamaParse/LiteParse: upstream already ships agent plugins, MCP and skills. Cloud LlamaParse requires authorization; LiteParse is local.
- PaddleOCR PP-StructureV3 and MinerU: complete local OCR/layout/table pipelines with upstream integration routes.
- img2table/gmft: independent table-focused components.
- Unstructured Transform MCP, Mistral OCR annotations, Azure Layout, Google Document AI Layout: hosted processors, requiring their own accounts.

Unmeasured tools have no engineering score in this report. Each new backend must be adapted without repairing against gold and evaluated under a separate versioned cohort.

## Published-version GLM first pass

GLM 5.3 Flash (zai.glm-5.3-flash?reasoning=low) with catalog-to-json 1.3.0, executed Git d3398f0668bbf5c5744a3237f53fca9d09087287, parser plugin 0.1.0: 128/140 engineering and literal table checks, 9/11 figure labels, 3/3 negative assertions; elapsed 107.150 s, timeout 900 s. Same original physical page 78, no reviewer or gold feedback. Missing shared-cell values remain failures. Original candidate, execution receipt and detailed score are retained. The MiniMax prototype trial used different source hashes, so these two first passes are not a matched model comparison.

## Expanded measured parser configurations (2026-10-12)

All arms attempted the same 15 physical pages and 500 selected engineering facts. Failed outputs remain in the denominator. These are direct parsers, not complete agent conversions. Different adapter contracts/prototypes are listed separately in the [machine-readable measurements](ready-parser-results-2026-10-12.json).

| Backend | Correct /500 | Completed /15 | Total execution seconds |
|---|---:|---:|---:|
| docling | 266 | 15 | 480.070 |
| mineru-advanced-metal | 201 | 14 | 1152.612 |
| gmft | 141 | 15 | 181.453 |
| img2table | 91 | 15 | 19.430 |
| marker-balanced-mac-metal | 88 | 15 | 428.770 |
| mineru-vulkan-gpu44 | 52 | 15 | 321.522 |
| mineru-standard-metal | 52 | 15 | 272.314 |
| camelot-lattice | 39 | 15 | 30.359 |
| tabula-lattice | 39 | 14 | 66.083 |
| mineru-basic | 22 | 14 | 306.909 |
| pymupdf4llm | 13 | 15 | 419.758 |
| unstructured-hi-res | 6 | 13 | 668.773 |
| pdfplumber | 5 | 15 | 26.867 |
| liteparse | 1 | 15 | 8.042 |
| pdf-mcp | 1 | 15 | 36.922 |
| pdf-capture-mcp-patched | 1 | 15 | 15.061 |
| tableshot | 1 | 15 | 17.335 |
| camelot-stream | 0 | 15 | 20.279 |
| paddle-cuda-gpu44 | 0 | 2 | 385.447 |
| tabula-stream | 0 | 15 | 62.178 |
| xberg | 0 | 15 | 3.280 |

The CPU expansion used clean catalog-to-json parent `470614c` and adapter contract `ee86c195…e5f7`. Mac runs used a retained prototype wheel SHA `881726c7…0256`, contract `dc453c18…f04`, not the later release. Both Metal modes use MinerU 4.0.12 with mineru-llama-cpp 0.1.3; no hidden CPU fallback. Advanced includes a 600-second loader timeout in its total and denominator. Its full native duration is unknown for that case; completed-case native time is 525.790 seconds, while total monitored execution is 1152.612 seconds.

Marker 2.0.0 / Surya 0.22.1 completed all 15 pages on the Mac using native Metal/MPS, OCR enabled and cloud LLM disabled. Its 88/500 score includes 20/140 on page 78; family-macro accuracy is 16.41%. Native inference took 402.443 seconds, the sum of per-case monitored durations 428.770 seconds, and the full supervisor loop 432.023 seconds. Input/output transfer took 173.806/25.452 seconds separately. Guided layout was explicitly disabled through the native Surya setting after the stock llama.cpp JSON-schema grammar rejected a digit regex; prior failed probes are retained. This is a measured configuration, not an unmodified default run. The observed peak RSS of the tracked Marker worker and VLM helper was 2793.297 MiB; a detached OCR-error helper was not included in that measurement. The idle task-owned helper was later identified and stopped by exact PID/create-time/command checks; its later RSS is not an earlier peak measurement. All 25 VLM layers were observed on Metal. Helper and adapter hashes are retained in the machine-readable measurements.

Paddle CUDA on the tested GPU had only two complete outputs; memory/reserve failures and malformed native HTML remain failures. Its 0/500 is a measured configuration under competing GPU load, not a claim about every Paddle deployment. The GPU standard MinerU arm completed 15/15 and scored 52/500. Paddle has only 13 known native durations totaling 307.902 seconds; the complete native total is unknown after two watchdog terminations. Its 385.447-second table entry is the sum of monitored case durations, not native inference time. The full supervisor took 385.599 seconds. GPU MinerU native inference took 292.804 seconds; its monitored cases sum to 321.522 seconds and full supervisor to 321.651 seconds.

Xberg and pdf-mcp are real installed plugin/MCP packages with successful initialize/tools-list. TableShot and PDF Capture also executed real MCP calls. PDF Capture scores refer to a separately retained private patch; upstream 0.12.0 swallowed invalid pdfplumber strategies and emitted no tables on page 78. Original and patched outputs are not conflated.

Useful complementary cases: gmft scored 62/108 and 58/72 on innovation pages 33/38, versus Docling 60/108 and 36/72. MinerU advanced Metal scored 72/108 on page 33. img2table scored 11/15 on small page 149 and 15/15 on armature page 111, versus Docling 2/15 and 8/15. These examples motivate source-property routing; selecting the best score after seeing gold is not an evaluated router.

The running controlled comparison fixes catalog-to-json 1.4.1 (`ecf9ced`), MiniMax model/settings, cases and grading, and changes only available tools: baseline Docling/PyMuPDF4LLM versus adding img2table/gmft. Agent accuracy improvement is pending; standalone parser scores do not prove it.

Availability and use are separate: each agent arm records the tools actually called and successful parser conversions. On the first page-78 pair the baseline called Docling and scored 140/140 selected engineering facts; the extended arm called no page parser and scored 120/140 despite 140/140 literal cell values. Its errors were column units and header conditions. This single first-pass pair does not establish a winner or a causal parser regression; the full 15-page comparison and reviewer stage remain separate.

The exact 297 canonical outputs from these 315 direct-parser attempts are available in [the retained output snapshot](../examples/parser-outputs/2026-10-12/README.md). Failed attempts have no fabricated output; the manifest records source/output hashes, actual options, timing boundaries and historical grader evidence.

Chandra OCR 0.2.0 / official chandra-ocr-2 was also attempted on Mac MPS with explicit bfloat16 and no CPU fallback. Two bounded page-78 attempts stopped at the admission/reserve guard before producing output; no accuracy score is available and this is not evidence of an inference-quality failure. The downloaded checkpoint and prior results are retained. The kernel memory-pressure percentage includes active memory and is not a count of unused RAM, so no unmeasured reserve reduction or foreign-process stop was used.

# Catalog Extraction Benchmark

Compare PDF catalogue parsers against independently reviewed engineering facts.

- **17 difficult pages** from five catalogues, including the rotated tables on page 78.
- **520 source-reviewed engineering facts +21 drawing checks** in dataset v2; the original15-page/500-fact dataset v1 is retained.
- Compare canonical page JSON and externally supplied products/characteristics/families JSONL.
- Run explicit **project × model** matrices with bounded execution and reusable artifacts.
- Keep literal transcription, engineering correctness and annotation coverage separate.
- [Important real failures and catalogue-meaning regressions](docs/REGRESSIONS-RU.md): retained evidence, pending glyph adjudication and purpose/scope checks, separate from historical fact totals.

**[Единая история всех испытаний: версии, три раунда, разброс, время и параллельные оценки](docs/EXPERIMENT-HISTORY-RU.md)** · [JSON-сводка](examples/experiment-history.json)

**[Общий рейтинг инструментов, включая Project X с GLM и MiniMax](docs/TOOL-LEADERBOARD-RU.md)** — одинаковые 15 страниц и один оценщик для всех; наш агент в этом рейтинге не участвует.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/megamen32/catalog-extraction-benchmark@v0.4.0
```

## Try it

```bash
catalog-bench dataset --dataset engineering-catalogs-v2
catalog-bench demo --output results/demo
catalog-bench score --case catalog-4-page-078 page-78.json --output results/score.json
```

The demo is synthetic and needs no model credentials. The reviewed dataset ships with the package; original PDFs are supplied locally. [Retained public catalogue parser outputs](examples/parser-outputs/2026-10-12/README.md) include JSON, versions, timing and historical scores for 21 configurations. A perfect selected-fact score does not establish full-page correctness.

## Compare your solutions

Export annotations with `catalog-bench dataset --export annotations`, then follow the [adapter guide](docs/ADAPTERS.md) to run an executable parser or import saved JSONL results. The benchmark does not require either competing parser to be installed for grading.

[Dataset and annotation coverage](docs/DATASET.md) · [Scoring rules](docs/SCORING.md) · [Source audit and errata](docs/ANNOTATIONS.md) · [Contributing](CONTRIBUTING.md)

[Ready-made solutions and measured parser results](docs/READY-SOLUTIONS.md)

[Как выбирать инструменты и проверить пользу для агента](docs/TOOL-ROUTING.md)

[Реальные 30 запусков FastAgent: инструменты, точность, время и выходные JSON](examples/agent-routing/2026-10-12-v1.4.1/README.md). [Переоценка 21 конфигурации парсеров оценщиком 0.2.2](examples/parser-outputs/2026-10-12/regrade-v0.2.2.json).

[Новая инструкция выбора/чтения:483/500 в полном15-страничном прогоне1.4.2](examples/agent-routing/2026-10-12-body-routing-v1.4.2/README.md). [Отдельный реальный15/15 canary1.4.3 на26](examples/agent-routing/2026-10-12-delivery-v1.4.3/README.md). Это отдельные версии и попытки.

[Повторные замороженные прогоны и разброс](docs/REPEATABILITY.md). [Сохранённая первая попытка1.4.4:368/500](examples/agent-routing/2026-10-12-byte-routing-v1.4.4/README.md); для выбора версии требуется минимум три полных раунда.

[Три полных раунда обеих версий: 90 попыток и 84 точных JSON](examples/agent-routing/2026-10-12-repeated-runs/README.md). После полной переоценки grader 0.2.4 среднее выбранных фактов: 94,13% у 1.4.2 и 70,27% у 1.4.4; разброс, неудачи и различия по каталогам сохранены отдельно.

[Три свежих раунда исправленной 1.4.6: 45 новых попыток](examples/agent-routing/2026-10-12-fresh-v1.4.6/README.md): 450/469/471 из 500, среднее 92,67%, диапазон 90–94,2%. Сравниваются полные профили с разными версиями parser plugin; новые смешанные профили не наследуют эти оценки.

[Source-grounded drawing checks for OPN27/39 and the mixed native pipeline](docs/DRAWING-ASSERTIONS.md). Dataset v2 is a new denominator; prior three-round percentages remain bound to immutable dataset v1.

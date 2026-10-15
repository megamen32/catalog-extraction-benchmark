# Общий рейтинг парсеров и агентов

> [Catalog Vision Backend](CATALOG-VISION-BACKEND.md) — наша закрытая адаптация; репозиторий приватный, доступ по запросу владельцу; планируем предоставлять бесплатно. Оценки ниже относятся к сохранённым конфигурациям испытаний, а не к новому запуску переименованного форка.

**Одинаковые 15 страниц, 500 инженерных фактов, один оценщик 0.3.2 для всех.** Это общая часть сохранённых испытаний. Catalog Vision Backend участвует как инструмент: без Vision, с GLM и с MiniMax. catalog-to-json включён отдельными версиями и моделями; агент и отдельные парсеры сравниваются как полные измеренные конфигурации.

Новых вызовов парсеров или моделей не было: переоценены сохранённые JSON. Рейтинг — по наблюдаемому среднему проценту инженерных фактов. У Catalog Vision Backend по три раунда; у catalog-to-json по два или три в зависимости от версии; у остальных инструментов пока по одному. Поэтому место в таблице не доказывает статистически устойчивого превосходства.

[Скачать и установить инструменты](PRODUCTS-RU.md). Название инструмента ведёт на продукт; последний столбец — на манифест результатов.

| Место | Инструмент / конфигурация | Режим / модель | Раундов | Раунд 1 | Раунд 2 | Раунд 3 | Среднее по 0.3.2 | SD, п.п. | Валидных страниц | Время раундов, с | Манифест |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [catalog-to-json 1.4.15](https://github.com/megamen32/catalog-to-json) | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 2 | 472/500 | 470/500 | не проводился | 94.20% | 0.28 | 15/15; 14/15 | 1665.9; не полностью измерено | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) |
| 2 | [catalog-to-json 1.4.2](https://github.com/megamen32/catalog-to-json) | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 3 | 483/500 | 463/500 | 466/500 | 94.13% | 2.16 | 14/15; 14/15; 13/15 | 2624.5; 2853.1; 3450.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) |
| 3 | [catalog-to-json 1.4.6](https://github.com/megamen32/catalog-to-json) | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 3 | 450/500 | 469/500 | 471/500 | 92.67% | 2.32 | 13/15; 13/15; 15/15 | 4180.3; 3949.9; 2029.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json) |
| 4 | [Catalog Vision Backend](https://github.com/megamen32/catalog-vision-backend) | Vision / glm-5.3-flash | 3 | 394/500 | 438/500 | 293/500 | 75.00% | 14.87 | 12/15; 15/15; 14/15 | 1784.1; 2208.6; 2276.7 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) |
| 5 | [catalog-to-json 1.4.4](https://github.com/megamen32/catalog-to-json) | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 3 | 368/500 | 341/500 | 345/500 | 70.27% | 2.91 | 14/15; 14/15; 15/15 | 3759.1; 3059.0; 2544.1 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) |
| 6 | [docling](https://github.com/docling-project/docling) | сохранённый режим парсера | 1 | 266/500 | не проводился | не проводился | 53.20% | не измерен | 15/15 | 480.1 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 7 | [mineru-advanced-metal](https://github.com/opendatalab/MinerU) | сохранённый режим парсера | 1 | 207/500 | не проводился | не проводился | 41.40% | не измерен | 14/15 | 1152.6 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 8 | [Catalog Vision Backend](https://github.com/megamen32/catalog-vision-backend) | Vision / MiniMax-M3.1-Flash-Preview | 3 | 212/500 | 160/500 | 244/500 | 41.07% | 8.48 | 3/15; 5/15; 3/15 | 1038.8; 1366.2; 989.8 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) |
| 9 | [gmft](https://github.com/conjuncts/gmft) | сохранённый режим парсера | 1 | 141/500 | не проводился | не проводился | 28.20% | не измерен | 15/15 | 181.5 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 10 | [img2table](https://github.com/xavctn/img2table) | сохранённый режим парсера | 1 | 91/500 | не проводился | не проводился | 18.20% | не измерен | 15/15 | 19.4 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 11 | [marker-balanced-mac-metal](https://github.com/datalab-to/marker) | сохранённый режим парсера | 1 | 88/500 | не проводился | не проводился | 17.60% | не измерен | 15/15 | 428.8 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 12 | [mineru-standard-metal](https://github.com/opendatalab/MinerU) | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен | 15/15 | 272.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 12 | [mineru-vulkan-gpu44](https://github.com/opendatalab/MinerU) | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен | 15/15 | 321.5 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 14 | [camelot-lattice](https://github.com/camelot-dev/camelot) | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен | 15/15 | 30.4 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 14 | [tabula-lattice](https://github.com/tabulapdf/tabula-java) | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен | 14/15 | 66.1 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 16 | [mineru-basic](https://github.com/opendatalab/MinerU) | сохранённый режим парсера | 1 | 22/500 | не проводился | не проводился | 4.40% | не измерен | 14/15 | 306.9 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 17 | [Catalog Vision Backend](https://github.com/megamen32/catalog-vision-backend) | PDF / без Vision | 3 | 15/500 | 15/500 | 15/500 | 3.00% | 0.00 | 15/15; 15/15; 15/15 | 31.6; 32.2; 33.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12/manifest.json) |
| 18 | [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) | сохранённый режим парсера | 1 | 13/500 | не проводился | не проводился | 2.60% | не измерен | 15/15 | 419.8 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 19 | [unstructured-hi-res](https://github.com/Unstructured-IO/unstructured) | сохранённый режим парсера | 1 | 6/500 | не проводился | не проводился | 1.20% | не измерен | 13/15 | 668.8 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 20 | [pdfplumber](https://github.com/jsvine/pdfplumber) | сохранённый режим парсера | 1 | 5/500 | не проводился | не проводился | 1.00% | не измерен | 15/15 | 26.9 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 21 | [liteparse](https://github.com/run-llama/liteparse) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 8.0 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 21 | [pdf-capture-mcp-patched](https://github.com/ChenHongYu2026/pdf-capture-mcp) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 15.1 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 21 | [pdf-mcp](https://github.com/jztan/pdf-mcp) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 36.9 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 21 | [tableshot](https://github.com/Bespoke34/tableshot) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 17.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 25 | [camelot-stream](https://github.com/camelot-dev/camelot) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 20.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 25 | [paddle-cuda-gpu44](https://github.com/PaddlePaddle/PaddleOCR) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 2/15 | 385.4 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 25 | [tabula-stream](https://github.com/tabulapdf/tabula-java) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 62.2 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 25 | [xberg](https://github.com/xberg-io/xberg) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 3.3 | [Результаты](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |

## Что именно сравнивается

- У всех строк одинаковые страницы, исходные PDF и неизменённые эталоны. 15 страниц буквально входят в текущий набор v2. Здесь исключены новые страницы 27 и 39, для которых у большинства старых парсеров нет сохранённого ответа.
- Полный основной бенчмарк остаётся на 17 страницах / 520 фактах +21 проверке чертежей. Эта таблица даёт сопоставимый общий рейтинг старых результатов и не заменяет расширенный бенчмарк.
- Варианты MinerU standard/advanced, backend и устройства сохраняют исходную конфигурацию. Catalog Vision Backend без Vision и с двумя Vision-моделями тоже отдельные конфигурации одного инструмента. Здесь не утверждается, что всем парсерам можно подключить одинаковые внешние модели.
- Catalog Vision Backend с Vision — протестированная адаптация native Vision v1 с рендером PDF и каталоговым JSON; это не измерение всех функций исходного банковского приложения. Исходный код остаётся в приватном репозитории.
- Неудачная или невалидная попытка остаётся нулём в знаменателе 500. Отсутствующий второй/третий раунд обозначен явно. Оценка выбранных фактов не означает полной точности страницы или всех каталогов.
- Время — сумма длительностей попыток для этих 15 страниц, включая сохранённые неудачи. Где поштучная разбивка неполна, сохранена исходная измеренная сумма и это явно отмечено в манифесте. Версии, режимы и условия также сохранены; кеши и нагрузка не контролировались как отдельный эксперимент скорости.

## Старый и новый оценщики живут параллельно

Один сохранённый JSON получает отдельные файлы оценок 0.3.0 и 0.3.2. Исходные оценки 0.2.0/0.2.2 у парсеров и 0.3.0/0.3.1/0.3.2 у Catalog Vision Backend также остаются на месте. Никакая переоценка не является новым модельным прогоном.

| Инструмент / конфигурация | Режим / модель | Среднее 0.3.0 | Среднее 0.3.2 |
|---|---|---|---|
| catalog-to-json 1.4.15 | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 94.20% | 94.20% |
| catalog-to-json 1.4.2 | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 94.13% | 94.13% |
| catalog-to-json 1.4.6 | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 92.67% | 92.67% |
| Catalog Vision Backend | Vision / glm-5.3-flash | 72.20% | 75.00% |
| catalog-to-json 1.4.4 | первый проход / anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 70.27% | 70.27% |
| docling | сохранённый режим парсера | 53.20% | 53.20% |
| mineru-advanced-metal | сохранённый режим парсера | 40.20% | 41.40% |
| Catalog Vision Backend | Vision / MiniMax-M3.1-Flash-Preview | 39.73% | 41.07% |
| gmft | сохранённый режим парсера | 28.20% | 28.20% |
| img2table | сохранённый режим парсера | 18.20% | 18.20% |
| marker-balanced-mac-metal | сохранённый режим парсера | 17.60% | 17.60% |
| mineru-standard-metal | сохранённый режим парсера | 10.40% | 10.40% |
| mineru-vulkan-gpu44 | сохранённый режим парсера | 10.40% | 10.40% |
| camelot-lattice | сохранённый режим парсера | 7.80% | 7.80% |
| tabula-lattice | сохранённый режим парсера | 7.80% | 7.80% |
| mineru-basic | сохранённый режим парсера | 4.40% | 4.40% |
| Catalog Vision Backend | PDF / без Vision | 3.00% | 3.00% |
| pymupdf4llm | сохранённый режим парсера | 2.60% | 2.60% |
| unstructured-hi-res | сохранённый режим парсера | 1.20% | 1.20% |
| pdfplumber | сохранённый режим парсера | 1.00% | 1.00% |
| liteparse | сохранённый режим парсера | 0.20% | 0.20% |
| pdf-capture-mcp-patched | сохранённый режим парсера | 0.20% | 0.20% |
| pdf-mcp | сохранённый режим парсера | 0.20% | 0.20% |
| tableshot | сохранённый режим парсера | 0.20% | 0.20% |
| camelot-stream | сохранённый режим парсера | 0.00% | 0.00% |
| paddle-cuda-gpu44 | сохранённый режим парсера | 0.00% | 0.00% |
| tabula-stream | сохранённый режим парсера | 0.00% | 0.00% |
| xberg | сохранённый режим парсера | 0.00% | 0.00% |

[Полные новые оценки, точные версии, контрольные суммы и выходные JSON](../examples/tool-leaderboard/common-15-v032/manifest.json) · [История всех испытаний и основной расширенный набор](EXPERIMENT-HISTORY-RU.md) · [Слабые места Catalog Vision Backend с примерами](PROJECT-X-SHORT-REVIEW-RU.md)

Для повторного пересчёта используйте отдельное окружение с опубликованным wheel 0.3.0 и этот checkout:

```bash
uv venv .tmp/regrade-v030
uv pip install --python .tmp/regrade-v030/bin/python https://github.com/megamen32/catalog-extraction-benchmark/releases/download/v0.3.0/catalog_extraction_benchmark-0.3.0-py3-none-any.whl
.tmp/regrade-v030/bin/python -I ops/add-catalog-agent-leaderboard.py
```

Скрипт проверяет отпечатки обоих алгоритмов и неизменность кандидатов. Он не запускает парсеры, не вызывает модели и не меняет исходные файлы оценки.

## catalog-to-json: версии и стадия

Все добавленные строки — первичное извлечение, без результата проверяющего. У версий 1.4.2, 1.4.4 и 1.4.6 по три сохранённых раунда; у 1.4.15 только два, поэтому серия явно неполная. Неудачные первые ответы дают ноль, поздние исправления их не заменяют.

Время 1.4.15 — сумма известных длительностей нативных вызовов извлекателя; неполная длительность не заполнена нулём. У остальных строк сохранено собственное определение времени. Эти суммы не доказывают преимущество по скорости.

Это оценки конкретных старых профилей. Они не являются измеренной точностью нынешнего выпуска 1.5.26 или принятых итоговых каталогов; проверяющий 1.4.17 не участвовал в этих первых ответах.

[Новый снимок с агентом](../examples/tool-leaderboard/common-15-with-agent-v032/manifest.json) · [Прежний снимок без агента](../examples/tool-leaderboard/common-15-v032/manifest.json). Оба сохраняются отдельно; новых вызовов моделей или парсеров не было.

# Общий рейтинг инструментов — Project X включён

**Одинаковые 15 страниц, 500 инженерных фактов, один оценщик 0.3.2 для всех.** Это общая часть сохранённых испытаний. Project X участвует как инструмент: без Vision, с GLM и с MiniMax. Наш агент, вызывающий инструменты, в этот рейтинг не включён.

Новых вызовов парсеров или моделей не было: переоценены сохранённые JSON. Рейтинг — по наблюдаемому среднему проценту инженерных фактов. У Project X три раунда каждой конфигурации; у остальных инструментов пока по одному. Поэтому место в таблице не доказывает статистически устойчивого превосходства.

| Место | Инструмент / конфигурация | Режим / модель | Раундов | Раунд 1 | Раунд 2 | Раунд 3 | Среднее по 0.3.2 | SD, п.п. | Валидных страниц | Время раундов, с |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Project X](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | Vision / glm-5.3-flash | 3 | 394/500 | 438/500 | 293/500 | 75.00% | 14.87 | 12/15; 15/15; 14/15 | 1784.1; 2208.6; 2276.7 |
| 2 | [docling](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 266/500 | не проводился | не проводился | 53.20% | не измерен | 15/15 | 480.1 |
| 3 | [mineru-advanced-metal](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 207/500 | не проводился | не проводился | 41.40% | не измерен | 14/15 | 1152.6 |
| 4 | [Project X](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | Vision / MiniMax-M3.1-Flash-Preview | 3 | 212/500 | 160/500 | 244/500 | 41.07% | 8.48 | 3/15; 5/15; 3/15 | 1038.8; 1366.2; 989.8 |
| 5 | [gmft](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 141/500 | не проводился | не проводился | 28.20% | не измерен | 15/15 | 181.5 |
| 6 | [img2table](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 91/500 | не проводился | не проводился | 18.20% | не измерен | 15/15 | 19.4 |
| 7 | [marker-balanced-mac-metal](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 88/500 | не проводился | не проводился | 17.60% | не измерен | 15/15 | 428.8 |
| 8 | [mineru-standard-metal](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен | 15/15 | 272.3 |
| 8 | [mineru-vulkan-gpu44](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен | 15/15 | 321.5 |
| 10 | [camelot-lattice](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен | 15/15 | 30.4 |
| 10 | [tabula-lattice](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен | 14/15 | 66.1 |
| 12 | [mineru-basic](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 22/500 | не проводился | не проводился | 4.40% | не измерен | 14/15 | 306.9 |
| 13 | [Project X](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12/manifest.json) | PDF / без Vision | 3 | 15/500 | 15/500 | 15/500 | 3.00% | 0.00 | 15/15; 15/15; 15/15 | 31.6; 32.2; 33.3 |
| 14 | [pymupdf4llm](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 13/500 | не проводился | не проводился | 2.60% | не измерен | 15/15 | 419.8 |
| 15 | [unstructured-hi-res](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 6/500 | не проводился | не проводился | 1.20% | не измерен | 13/15 | 668.8 |
| 16 | [pdfplumber](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 5/500 | не проводился | не проводился | 1.00% | не измерен | 15/15 | 26.9 |
| 17 | [liteparse](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 8.0 |
| 17 | [pdf-capture-mcp-patched](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 15.1 |
| 17 | [pdf-mcp](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 36.9 |
| 17 | [tableshot](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен | 15/15 | 17.3 |
| 21 | [camelot-stream](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 20.3 |
| 21 | [paddle-cuda-gpu44](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 2/15 | 385.4 |
| 21 | [tabula-stream](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 62.2 |
| 21 | [xberg](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен | 15/15 | 3.3 |

## Что именно сравнивается

- У всех строк одинаковые страницы, исходные PDF и неизменённые эталоны. 15 страниц буквально входят в текущий набор v2. Здесь исключены новые страницы 27 и 39, для которых у большинства старых парсеров нет сохранённого ответа.
- Полный основной бенчмарк остаётся на 17 страницах / 520 фактах +21 проверке чертежей. Эта таблица даёт сопоставимый общий рейтинг старых результатов и не заменяет расширенный бенчмарк.
- Варианты MinerU standard/advanced, backend и устройства сохраняют исходную конфигурацию. Project X без Vision и с двумя Vision-моделями тоже отдельные конфигурации одного инструмента. Здесь не утверждается, что всем парсерам можно подключить одинаковые внешние модели.
- Project X с Vision — протестированная адаптация native Vision v1 с рендером PDF и каталоговым JSON; это не измерение всех функций исходного банковского приложения. Исходный код и настоящее название не публикуются.
- Неудачная или невалидная попытка остаётся нулём в знаменателе 500. Отсутствующий второй/третий раунд обозначен явно. Оценка выбранных фактов не означает полной точности страницы или всех каталогов.
- Время — сумма длительностей попыток для этих 15 страниц, включая сохранённые неудачи. Где поштучная разбивка неполна, сохранена исходная измеренная сумма и это явно отмечено в манифесте. Версии, режимы и условия также сохранены; кеши и нагрузка не контролировались как отдельный эксперимент скорости.

## Старый и новый оценщики живут параллельно

Один сохранённый JSON получает отдельные файлы оценок 0.3.0 и 0.3.2. Исходные оценки 0.2.0/0.2.2 у парсеров и 0.3.0/0.3.1/0.3.2 у Project X также остаются на месте. Никакая переоценка не является новым модельным прогоном.

| Инструмент / конфигурация | Режим / модель | Среднее 0.3.0 | Среднее 0.3.2 |
|---|---|---|---|
| Project X | Vision / glm-5.3-flash | 72.20% | 75.00% |
| docling | сохранённый режим парсера | 53.20% | 53.20% |
| mineru-advanced-metal | сохранённый режим парсера | 40.20% | 41.40% |
| Project X | Vision / MiniMax-M3.1-Flash-Preview | 39.73% | 41.07% |
| gmft | сохранённый режим парсера | 28.20% | 28.20% |
| img2table | сохранённый режим парсера | 18.20% | 18.20% |
| marker-balanced-mac-metal | сохранённый режим парсера | 17.60% | 17.60% |
| mineru-standard-metal | сохранённый режим парсера | 10.40% | 10.40% |
| mineru-vulkan-gpu44 | сохранённый режим парсера | 10.40% | 10.40% |
| camelot-lattice | сохранённый режим парсера | 7.80% | 7.80% |
| tabula-lattice | сохранённый режим парсера | 7.80% | 7.80% |
| mineru-basic | сохранённый режим парсера | 4.40% | 4.40% |
| Project X | PDF / без Vision | 3.00% | 3.00% |
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

[Полные новые оценки, точные версии, контрольные суммы и выходные JSON](../examples/tool-leaderboard/common-15-v032/manifest.json) · [История всех испытаний и основной расширенный набор](EXPERIMENT-HISTORY-RU.md) · [Слабые места Project X с примерами](PROJECT-X-SHORT-REVIEW-RU.md)

Для повторного пересчёта используйте отдельное окружение с опубликованным wheel 0.3.0 и этот checkout:

```bash
uv venv .tmp/regrade-v030
uv pip install --python .tmp/regrade-v030/bin/python https://github.com/megamen32/catalog-extraction-benchmark/releases/download/v0.3.0/catalog_extraction_benchmark-0.3.0-py3-none-any.whl
.tmp/regrade-v030/bin/python -I ops/render-tool-leaderboard.py
```

Скрипт проверяет отпечатки обоих алгоритмов и неизменность кандидатов. Он не запускает парсеры, не вызывает модели и не меняет исходные файлы оценки.

# Единая история испытаний

**96,6% сохранились: это 483/500 в первом прогоне 1.4.2.** По трём сохранённым прогонам этой версии оценщик 0.2.4 даёт среднее 94,13%, а не 96,6%. Новая связка и расширенный набор проверяются отдельно; они не наследуют старый процент.

Эта страница собирается из опубликованных результатов. [Машиночитаемая сводка](../examples/experiment-history.json) содержит версии, методы, время, ссылки и контрольные суммы источников. Таблицы показывают точность выбранных проверяемых фактов; точность всей страницы и всех каталогов пока не установлена.

## Как читать историю

- Набор v1: 15 страниц, 500 инженерных фактов. Набор v2: 17 страниц, 520 фактов и отдельно 21 проверка чертежей. v1 сохранён; оба набора доступны одновременно.
- Первая выгрузка модели, исправляемый черновик и принятый проверяющим результат — разные стадии. Ниже первая выгрузка сравнивается с первой выгрузкой Project X. Готовность после проверки публикуется отдельно.
- Для законченного раунда неудачные/невалидные ответы остаются в фиксированном знаменателе с нулём. Ещё не начатый раунд и новая страница, которой не было в старом запуске, обозначаются как отсутствующие измерения.
- SD — выборочное стандартное отклонение по трём неокруглённым процентам, в процентных пунктах. Одного хорошего запуска недостаточно для выбора версии.
- Время сохраняется в секундах. Старые параллельные испытания и Project X дают суммы времени попыток; смешанная связка — длительность раунда на момент снимка с проверками и ожиданием лимитов. Сравнение скорости по этим разным определениям некорректно.

## Сохранённые испытания на v1 / 500 фактов

Модель всех агентских строк: MiniMax-M3.1-Flash-Preview, medium, без второго проверяющего. У 1.4.2 и 1.4.4 первый раунд сохранён из первоначального испытания, два следующих были свежими. У 1.4.6 все три свежие. Различались и программа, и версии плагина: это сравнение полных профилей.

| Программа / профиль | Оценщик | Раунд 1 | Раунд 2 | Раунд 3 | Среднее ± SD, п.п. | Валидных страниц | Время по раундам, с |
|---|---|---|---|---|---|---|---|
| [1.4.1 / baseline](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-v1.4.1/manifest.json) | 0.2.2 | 479/500 (95.80%) | не проводился | не проводился | нет трёх завершённых раундов | 14/15 | 2774.5 |
| [1.4.1 / extended](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-v1.4.1/manifest.json) | 0.2.2 | 467/500 (93.40%) | не проводился | не проводился | нет трёх завершённых раундов | 15/15 | 2023.0 |
| [1.4.2](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 0.2.4 | 483/500 (96.60%) | 463/500 (92.60%) | 466/500 (93.20%) | 94.13% ± 2.16 | 14/15; 14/15; 13/15 | 2624.5; 2853.1; 3450.3 |
| [1.4.4](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 0.2.4 | 368/500 (73.60%) | 341/500 (68.20%) | 345/500 (69.00%) | 70.27% ± 2.91 | 14/15; 14/15; 15/15 | 3759.1; 3059.0; 2544.1 |
| [1.4.6](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json) | 0.2.4 | 450/500 (90.00%) | 469/500 (93.80%) | 471/500 (94.20%) | 92.67% ± 2.32 | 13/15; 13/15; 15/15 | 4180.3; 3949.9; 2029.3 |

## Расширенный v2 / 520 инженерных фактов

Project X здесь означает адаптированную Vision-интеграцию v1, а не весь исходный банковский продукт. Для неё завершены три свежих последовательных раунда каждой модели. Старая смешанная связка остановлена после двух первоначальных раундов; у исправленной 1.4.15 → 1.4.17 три свежих раунда ещё выполняются. Итоговый победитель новой связки пока не установлен.

Номера у стрелки — фактические версии извлекающего и проверяющего агентов. Рабочая оцифровка всех 980 страниц сейчас использует отдельный управляющий выпуск 1.4.20 со связкой 1.4.15 → 1.4.8. Она не наследует точность экспериментального проверяющего 1.4.17; его нельзя продвигать по одному удачному результату.

| Программа / профиль | Оценщик | Раунд 1 | Раунд 2 | Раунд 3 | Среднее ± SD, п.п. | Валидных страниц | Время по раундам, с |
|---|---|---|---|---|---|---|---|
| [1.4.2 → 1.4.8 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/offline-regrading/2026-10-12-v032/summary.json) | 0.3.2 | 399/520 (76.73%) | 479/520 (92.12%) | не запускался | нет трёх завершённых раундов | 15/17; 16/17 | 5245.4; 3590.4 |
| [Project X / glm-5.3-flash](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 0.3.2 | 411/520 (79.04%) | 456/520 (87.69%) | 313/520 (60.19%) | 75.64% ± 14.06 | 14/17; 17/17; 16/17 | 1990.3; 2874.6; 2460.5 |
| [Project X / MiniMax-M3.1-Flash-Preview](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 0.3.2 | 222/520 (42.69%) | 160/520 (30.77%) | 247/520 (47.50%) | 40.32% ± 8.61 | 4/17; 5/17; 4/17 | 1158.8; 1482.9; 1084.3 |
| [Project X / PDF без Vision](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12/manifest.json) | 0.3.0 | 21/520 (4.04%) | 21/520 (4.04%) | 21/520 (4.04%) | 4.04% ± 0.00 | 17/17; 17/17; 17/17 | 36.4; 37.5; 38.5 |
| [1.4.15 → 1.4.17 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 0.3.2 | 492/520 (94.62%) | 490/520 (94.23%) | ожидается | нет трёх завершённых раундов | 17/17; 16/17 | 1987.2; 3515.8 |

## Черновик и принятый результат новой связки

Эти строки обновляются после завершения каждого полного цикла. Принятый результат требует отчёта проверяющего; отклонённые страницы не становятся принятыми от наличия JSON. Пока цикл не завершён, итоговая точность стадии не заявляется.

| Программа / профиль | Оценщик | Раунд 1 | Раунд 2 | Раунд 3 | Среднее ± SD, п.п. | Валидных страниц | Время по раундам, с |
|---|---|---|---|---|---|---|---|
| [1.4.15 → 1.4.17 / последний черновик](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 0.3.2 | 508/520 (97.69%) | 500/520 (96.15%) | ожидается | нет трёх завершённых раундов | 17/17; 16/17 | 16543.2; 17050.9 |
| [1.4.15 → 1.4.17 / принятый результат](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 0.3.2 | 15/520 (2.88%) | 78/520 (15.00%) | ожидается | нет трёх завершённых раундов | 1/17; 6/17 | 16543.2; 17050.9 |

## Чертежи / 21 отдельная проверка

Табличная точность не заменяет точность привязки размеров к элементам чертежа. Статистические графики — линейные, столбчатые, круговые — в этот набор пока не входят.

| Программа / профиль | Оценщик | Раунд 1 | Раунд 2 | Раунд 3 | Среднее ± SD, п.п. | Валидных страниц | Время по раундам, с |
|---|---|---|---|---|---|---|---|
| [1.4.2 → 1.4.8 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/offline-regrading/2026-10-12-v032/summary.json) | 0.3.2 | 5/21 (23.81%) | 6/21 (28.57%) | не запускался | нет трёх завершённых раундов | 15/17; 16/17 | 5245.4; 3590.4 |
| [Project X / glm-5.3-flash](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 0.3.2 | 6/21 (28.57%) | 6/21 (28.57%) | 7/21 (33.33%) | 30.16% ± 2.75 | 14/17; 17/17; 16/17 | 1990.3; 2874.6; 2460.5 |
| [Project X / MiniMax-M3.1-Flash-Preview](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 0.3.2 | 3/21 (14.29%) | 0/21 (0.00%) | 2/21 (9.52%) | 7.94% ± 7.27 | 4/17; 5/17; 4/17 | 1158.8; 1482.9; 1084.3 |
| [Project X / PDF без Vision](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12/manifest.json) | 0.3.0 | 0/21 (0.00%) | 0/21 (0.00%) | 0/21 (0.00%) | 0.00% ± 0.00 | 17/17; 17/17; 17/17 | 36.4; 37.5; 38.5 |
| [1.4.15 → 1.4.17 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 0.3.2 | 4/21 (19.05%) | 9/21 (42.86%) | ожидается | нет трёх завершённых раундов | 17/17; 16/17 | 1987.2; 3515.8 |

## Два оценщика одновременно, без повторного вызова моделей

В одном раунде может быть несколько оценок одного сохранённого ответа. Старые файлы оценки остаются на месте, новая версия записывает отдельный файл. В сводке первичный оценщик для v2 — 0.3.2; 0.3.0 и 0.3.1 видны рядом. Пересчёт не исправляет ответ программы и не является новым прогоном модели.

| Профиль | Раунд | Старый оценщик: факты / чертежи | Новый оценщик: факты / чертежи | Дополнительные вызовы моделей |
|---|---|---|---|---|
| [1.4.2](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 1 | 0.2.2: 483/500 (96.60%) / — | 0.2.4: 483/500 (96.60%) / — | 0 |
| [1.4.2](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 2 | 0.2.2: 463/500 (92.60%) / — | 0.2.4: 463/500 (92.60%) / — | 0 |
| [1.4.2](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 3 | 0.2.2: 406/500 (81.20%) / — | 0.2.4: 466/500 (93.20%) / — | 0 |
| [1.4.4](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 1 | 0.2.2: 368/500 (73.60%) / — | 0.2.4: 368/500 (73.60%) / — | 0 |
| [1.4.4](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 2 | 0.2.2: 341/500 (68.20%) / — | 0.2.4: 341/500 (68.20%) / — | 0 |
| [1.4.4](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) | 3 | 0.2.2: 345/500 (69.00%) / — | 0.2.4: 345/500 (69.00%) / — | 0 |
| [1.4.2 → 1.4.8 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/offline-regrading/2026-10-12-v032/summary.json) | 1 | 0.3.0: 399/520 (76.73%) / 5/21 (23.81%) | 0.3.2: 399/520 (76.73%) / 5/21 (23.81%) | 0 |
| [1.4.2 → 1.4.8 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/offline-regrading/2026-10-12-v032/summary.json) | 2 | 0.3.0: 479/520 (92.12%) / 6/21 (28.57%) | 0.3.2: 479/520 (92.12%) / 6/21 (28.57%) | 0 |
| [Project X / glm-5.3-flash](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 1 | 0.3.0: 380/520 (73.08%) / 4/21 (19.05%) | 0.3.2: 411/520 (79.04%) / 6/21 (28.57%) | 0 |
| [Project X / glm-5.3-flash](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 2 | 0.3.0: 452/520 (86.92%) / 6/21 (28.57%) | 0.3.2: 456/520 (87.69%) / 6/21 (28.57%) | 0 |
| [Project X / glm-5.3-flash](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 3 | 0.3.0: 304/520 (58.46%) / 4/21 (19.05%) | 0.3.2: 313/520 (60.19%) / 7/21 (33.33%) | 0 |
| [Project X / MiniMax-M3.1-Flash-Preview](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 1 | 0.3.0: 210/520 (40.38%) / 3/21 (14.29%) | 0.3.2: 222/520 (42.69%) / 3/21 (14.29%) | 0 |
| [Project X / MiniMax-M3.1-Flash-Preview](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 2 | 0.3.0: 160/520 (30.77%) / 0/21 (0.00%) | 0.3.2: 160/520 (30.77%) / 0/21 (0.00%) | 0 |
| [Project X / MiniMax-M3.1-Flash-Preview](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) | 3 | 0.3.0: 239/520 (45.96%) / 2/21 (9.52%) | 0.3.2: 247/520 (47.50%) / 2/21 (9.52%) | 0 |
| [1.4.15 → 1.4.17 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 1 | 0.3.0: 490/520 (94.23%) / 4/21 (19.05%) | 0.3.2: 492/520 (94.62%) / 4/21 (19.05%) | 0 |
| [1.4.15 → 1.4.17 / первая выгрузка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 2 | 0.3.0: 490/520 (94.23%) / 9/21 (42.86%) | 0.3.2: 490/520 (94.23%) / 9/21 (42.86%) | 0 |
| [1.4.15 → 1.4.17 / последний черновик](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 1 | 0.3.0: 508/520 (97.69%) / 6/21 (28.57%) | 0.3.2: 508/520 (97.69%) / 6/21 (28.57%) | 0 |
| [1.4.15 → 1.4.17 / последний черновик](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 2 | 0.3.0: 500/520 (96.15%) / 9/21 (42.86%) | 0.3.2: 500/520 (96.15%) / 9/21 (42.86%) | 0 |
| [1.4.15 → 1.4.17 / принятый результат](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 1 | 0.3.0: 15/520 (2.88%) / 0/21 (0.00%) | 0.3.2: 15/520 (2.88%) / 0/21 (0.00%) | 0 |
| [1.4.15 → 1.4.17 / принятый результат](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) | 2 | 0.3.0: 78/520 (15.00%) / 9/21 (42.86%) | 0.3.2: 78/520 (15.00%) / 9/21 (42.86%) | 0 |

У 1.4.2, раунд 3, сохранённый ответ получил 406/500 по старому алгоритму и 466/500 по 0.2.4: оценщик научился учитывать однозначную группу размеров верхнего фланца. JSON не менялся. В 0.3.2 добавлены ограниченные физические алиасы единиц и английских обозначений геометрии; неправильные числа, допуски и принадлежность размера по-прежнему считаются ошибками.

Новая страница может быть оценена задним числом только если её ответ действительно сохранён. У ранних 15-страничных испытаний нет результатов для новых страниц 27 и 39. Их нельзя превращать в якобы выполненный полный 17-страничный прогон.

## Что произошло между высокими и низкими результатами

1. 483/500 было верным результатом конкретного первого запуска. Три повтора выявили разброс; исправление оценщика изменило оценку одного сохранённого ответа, не работу модели.
2. В расширенных испытаниях были настоящие сбои сохранения: запись секции рисунков после полной страницы могла стереть таблицу. На странице 38 инновационных изделий это превратило ранее сохранённую таблицу 72/72 в итоговые 0/72. Промежуточный ответ не подставлялся вместо доставленного.
3. Изменился профиль: добавился второй агент, новая логика сохранения и новый набор. Низкий результат первой выгрузки старой связки не объясняется только добавлением 20 фактов: на прежних 500 фактах получено 381/500 и 459/500.
4. Исправленное сохранение проверено через настоящий MCP на выходе рабочей оцифровки: таблица, 64 ячейки и текст сохранились после обновления рисунков и финализации. Это проверка конкретного бага, а не подтверждение 96% для новой версии.

Сейчас исправленная связка проходит три раунда на замороженных v2/0.3.2. Оцифровка всех каталогов идёт отдельно. Следующий выбор программы будет опираться на эти новые три измерения; ошибки размеров, объединённых ячеек и слишком строгой буквальной проверки исправляются с отдельной версией и отдельным испытанием.

## Отдельные пробы, которые не заменяют полный раунд

Результаты отдельных попыток также сохранены в JSON-сводке; они не входят в среднее полного раунда и не заменяют неудачные ответы старой версии.

| Проба | Страница | Модель | Сохранённая оценка | Время, с |
|---|---|---|---|---|
| [1.4.3 / page26](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-delivery-v1.4.3/manifest.json) | 026 | anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium | 15/15 | 99.455 |
| [Project X / focused Vision probe](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-vision-preview/results.json) | 078 | MiniMax-M3.1-Flash-Preview | 108/140 | 50.755 |
| [Project X / focused Vision probe](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-vision-preview/results.json) | 078 | glm-5.3-flash | 136/140 | 106.563 |
| [Project X / focused Vision probe](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-vision-preview/results.json) | 027 | MiniMax-M3.1-Flash-Preview | нет валидного ответа | не записано |
| [Project X / focused Vision probe](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-vision-preview/results.json) | 039 | MiniMax-M3.1-Flash-Preview | нет валидного ответа | не записано |
| [1.4.25 / проверка рисунка](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-reviewer25-source-check/manifest.json) | 035 | zai.glm-5.3-flash?reasoning=low | Ложный PASS: неверная привязка Ø500 | 258.082 |
| [1.4.26 / рисунки, цикл1, попытка4](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-drawing-v126/manifest.json) | 027 | anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium → zai.glm-5.3-flash?reasoning=low | Модель: pass; Источник: отклонён; чертежи032 9/13 | 3375.515 |
| [1.4.26 / рисунки, цикл1, попытка3](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-drawing-v126/manifest.json) | 039 | anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium → zai.glm-5.3-flash?reasoning=low | Модель: pass; Источник: отклонён; чертежи032 5/8 | 1251.374 |
| [1.4.26 / рисунки, цикл2, попытка1](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-drawing-v126/manifest.json) | 027 | anthropic.MiniMax-M3.1-Flash-Preview?reasoning=medium → zai.glm-5.3-flash?reasoning=low | Модель: pass; Источник: ещё не принят; чертежи032 5/13 | 926.323 |

Пробы1.4.26 — отдельный пилот двух страниц с сохранённой обратной связью и восстановлением управляющего процесса. Они не являются тремя свежими последовательными раундами полного бенчмарка. PASS модели сохранён отдельно от отклонения по оригиналу; выбранные проверки чертежей не охватывают все реальные ошибки. Время этих строк — сумма завершённых native вызовов страницы на момент снимка.

[Дополнительный аудит13 связей и собственного условия столбца на странице27](SUPPLEMENTAL-DRAWING-AUDIT-v1.md) проверяет сохранённые ответы без новых вызовов модели. Он опубликован отдельной версией; результаты не добавляются к520+21 и не меняют прежние проценты.


Vision-пробы страницы 78 показывают старую строгую оценку: 108/140 и 136/140. Это отдельные ответы, а не первые раунды позднейшего полного испытания. Ранние 98,57% в переписке относились к 138/140 буквально прочитанным ячейкам одной страницы 78; это другой показатель, не точность всех каталогов.

## Общий рейтинг инструментов — включая Project X

[Таблица для отправки другу: Project X и остальные инструменты на одинаковых 15 страницах](TOOL-LEADERBOARD-RU.md). Все конфигурации ниже переоценены одним оценщиком 0.3.2, без новых запусков. Это общие 500 инженерных фактов сохранённых испытаний; основной расширенный набор 17/520+21 остаётся отдельным. Наш агент в рейтинге инструментов не участвует.

| Место | Инструмент / конфигурация | Режим / модель | Раундов | Раунд 1 | Раунд 2 | Раунд 3 | Среднее 0.3.2 | SD, п.п. |
|---|---|---|---|---|---|---|---|---|
| 1 | Project X | Vision / glm-5.3-flash | 3 | 394/500 | 438/500 | 293/500 | 75.00% | 14.87 |
| 2 | docling | сохранённый режим парсера | 1 | 266/500 | не проводился | не проводился | 53.20% | не измерен |
| 3 | mineru-advanced-metal | сохранённый режим парсера | 1 | 207/500 | не проводился | не проводился | 41.40% | не измерен |
| 4 | Project X | Vision / MiniMax-M3.1-Flash-Preview | 3 | 212/500 | 160/500 | 244/500 | 41.07% | 8.48 |
| 5 | gmft | сохранённый режим парсера | 1 | 141/500 | не проводился | не проводился | 28.20% | не измерен |
| 6 | img2table | сохранённый режим парсера | 1 | 91/500 | не проводился | не проводился | 18.20% | не измерен |
| 7 | marker-balanced-mac-metal | сохранённый режим парсера | 1 | 88/500 | не проводился | не проводился | 17.60% | не измерен |
| 8 | mineru-standard-metal | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен |
| 8 | mineru-vulkan-gpu44 | сохранённый режим парсера | 1 | 52/500 | не проводился | не проводился | 10.40% | не измерен |
| 10 | camelot-lattice | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен |
| 10 | tabula-lattice | сохранённый режим парсера | 1 | 39/500 | не проводился | не проводился | 7.80% | не измерен |
| 12 | mineru-basic | сохранённый режим парсера | 1 | 22/500 | не проводился | не проводился | 4.40% | не измерен |
| 13 | Project X | PDF / без Vision | 3 | 15/500 | 15/500 | 15/500 | 3.00% | 0.00 |
| 14 | pymupdf4llm | сохранённый режим парсера | 1 | 13/500 | не проводился | не проводился | 2.60% | не измерен |
| 15 | unstructured-hi-res | сохранённый режим парсера | 1 | 6/500 | не проводился | не проводился | 1.20% | не измерен |
| 16 | pdfplumber | сохранённый режим парсера | 1 | 5/500 | не проводился | не проводился | 1.00% | не измерен |
| 17 | liteparse | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен |
| 17 | pdf-capture-mcp-patched | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен |
| 17 | pdf-mcp | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен |
| 17 | tableshot | сохранённый режим парсера | 1 | 1/500 | не проводился | не проводился | 0.20% | не измерен |
| 21 | camelot-stream | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен |
| 21 | paddle-cuda-gpu44 | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен |
| 21 | tabula-stream | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен |
| 21 | xberg | сохранённый режим парсера | 1 | 0/500 | не проводился | не проводился | 0.00% | не измерен |

У Project X три прогона каждого режима, у остальных пока по одному. Место отражает наблюдаемое среднее; статистически устойчивый победитель не доказан. Исходные ответы и прежние оценки сохранены отдельно.

## Сохранённая историческая оценка 21 парсера

315 попыток, 297 сохранённых выходных файлов; без дополнительных вызовов агентских моделей при переоценке. Некоторые парсеры используют собственные OCR/VLM-компоненты. Это первая обработка без агентского проверяющего, на прежнем наборе. Полные версии и определения времени находятся в сводке и [оригинальном манифесте](../examples/parser-outputs/2026-10-12/manifest.json).

| Конфигурация | Оценщик 0.2.0 | Оценщик 0.2.2 | Валидных страниц | Время, с |
|---|---|---|---|---|
| docling | 266/500 (53.20%) | 266/500 (53.20%) | 15/15 | 480.070 |
| pymupdf4llm | 13/500 (2.60%) | 13/500 (2.60%) | 15/15 | 419.758 |
| camelot-lattice | 39/500 (7.80%) | 39/500 (7.80%) | 15/15 | 30.359 |
| camelot-stream | 0/500 (0.00%) | 0/500 (0.00%) | 15/15 | 20.279 |
| gmft | 141/500 (28.20%) | 141/500 (28.20%) | 15/15 | 181.453 |
| img2table | 91/500 (18.20%) | 91/500 (18.20%) | 15/15 | 19.430 |
| liteparse | 1/500 (0.20%) | 1/500 (0.20%) | 15/15 | 8.042 |
| mineru-basic | 22/500 (4.40%) | 22/500 (4.40%) | 14/15 | 306.909 |
| paddle-cuda-gpu44 | 0/500 (0.00%) | 0/500 (0.00%) | 2/15 | 385.447 |
| mineru-vulkan-gpu44 | 52/500 (10.40%) | 52/500 (10.40%) | 15/15 | 321.522 |
| mineru-standard-metal | 52/500 (10.40%) | 52/500 (10.40%) | 15/15 | 272.314 |
| mineru-advanced-metal | 201/500 (40.20%) | 201/500 (40.20%) | 14/15 | 1152.612 |
| pdfplumber | 5/500 (1.00%) | 5/500 (1.00%) | 15/15 | 26.867 |
| tabula-lattice | 39/500 (7.80%) | 39/500 (7.80%) | 14/15 | 66.083 |
| tabula-stream | 0/500 (0.00%) | 0/500 (0.00%) | 15/15 | 62.178 |
| xberg | 0/500 (0.00%) | 0/500 (0.00%) | 15/15 | 3.280 |
| pdf-mcp | 1/500 (0.20%) | 1/500 (0.20%) | 15/15 | 36.922 |
| pdf-capture-mcp-patched | 1/500 (0.20%) | 1/500 (0.20%) | 15/15 | 15.061 |
| tableshot | 1/500 (0.20%) | 1/500 (0.20%) | 15/15 | 17.335 |
| unstructured-hi-res | 6/500 (1.20%) | 6/500 (1.20%) | 13/15 | 668.773 |
| marker-balanced-mac-metal | 88/500 (17.60%) | 88/500 (17.60%) | 15/15 | 428.770 |

## Хронология опубликованных доказательств

Ниже время последнего Git-коммита каждого исходного манифеста, UTC. Оно показывает публикацию/обновление доказательства, а не обязательно начало обработки. Фактическое время обработки, когда оно записано, остаётся в самом манифесте.

| Последняя публикация, UTC | Доказательство |
|---|---|
| ещё не закоммичен | [examples/agent-routing/2026-10-12-corrected-v032/round-2/round.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/round-2/round.json) |
| 2026-10-12T07:19:05+03:00 | [examples/parser-outputs/2026-10-12/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/manifest.json) |
| 2026-10-12T08:25:09+03:00 | [examples/parser-outputs/2026-10-12/regrade-v0.2.2.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/parser-outputs/2026-10-12/regrade-v0.2.2.json) |
| 2026-10-12T08:28:57+03:00 | [examples/agent-routing/2026-10-12-v1.4.1/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-v1.4.1/manifest.json) |
| 2026-10-12T09:13:00+03:00 | [examples/agent-routing/2026-10-12-delivery-v1.4.3/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-delivery-v1.4.3/manifest.json) |
| 2026-10-12T13:43:51+03:00 | [examples/agent-routing/2026-10-12-repeated-runs/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/manifest.json) |
| 2026-10-12T13:43:51+03:00 | [examples/agent-routing/2026-10-12-repeated-runs/regrade-v0.2.4.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-repeated-runs/regrade-v0.2.4.json) |
| 2026-10-12T15:36:21+03:00 | [examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-fresh-v1.4.6/manifest.json) |
| 2026-10-12T17:46:17+03:00 | [examples/project-x/2026-10-12/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12/manifest.json) |
| 2026-10-12T18:42:02+03:00 | [examples/project-x/2026-10-12-vision-preview/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-vision-preview/results.json) |
| 2026-10-12T19:28:20+03:00 | [examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-1/summary.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-1/summary.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/manifest.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/summary.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/summary.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-1/results.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-2/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-2/results.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-3/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/glm-5.3-flash/round-3/results.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-1/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-1/results.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-2/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-2/results.json) |
| 2026-10-12T21:00:29+03:00 | [examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-3/results.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/project-x/2026-10-12-native-vision-v1-full/MiniMax-M3.1-Flash-Preview/round-3/results.json) |
| 2026-10-12T21:09:17+03:00 | [examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-2/summary.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-mixed-v2/first-pass-round-2/summary.json) |
| 2026-10-12T21:11:57+03:00 | [examples/offline-regrading/2026-10-12-v032/summary.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/offline-regrading/2026-10-12-v032/summary.json) |
| 2026-10-13T00:00:19+03:00 | [examples/agent-routing/2026-10-12-corrected-v032/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/manifest.json) |
| 2026-10-13T00:34:22+03:00 | [examples/agent-routing/2026-10-12-corrected-v032/first-pass-round-1/round.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/first-pass-round-1/round.json) |
| 2026-10-13T00:43:28+03:00 | [examples/tool-leaderboard/common-15-v032/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/tool-leaderboard/common-15-v032/manifest.json) |
| 2026-10-13T03:47:30+03:00 | [examples/agent-routing/2026-10-13-reviewer25-source-check/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-reviewer25-source-check/manifest.json) |
| 2026-10-13T04:40:33+03:00 | [examples/agent-routing/2026-10-12-corrected-v032/round-1/round.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/round-1/round.json) |
| 2026-10-13T05:30:31+03:00 | [examples/agent-routing/2026-10-12-corrected-v032/first-pass-round-2/round.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-12-corrected-v032/first-pass-round-2/round.json) |
| 2026-10-13T05:52:52+03:00 | [examples/supplemental-drawing-audit-v1/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/supplemental-drawing-audit-v1/manifest.json) |
| 2026-10-13T06:06:02+03:00 | [examples/agent-routing/2026-10-13-drawing-v126/manifest.json](https://github.com/megamen32/catalog-extraction-benchmark/blob/main/examples/agent-routing/2026-10-13-drawing-v126/manifest.json) |

Воспроизвести индекс: `python3 ops/render-experiment-history.py`. Команда только читает опубликованные результаты и создаёт эту страницу и JSON-сводку; парсеры и модели не запускаются.

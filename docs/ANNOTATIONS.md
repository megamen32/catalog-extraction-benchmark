# Source audit and corrections

The initial selection scanned 980 physical pages across five supplied catalogues. Structural features suggested difficult candidates; visual curation selected 15 pages with rotated multi-level headings, narrow columns, merged groups, mixed dimensions, manufacturer cross-reference layouts and engineering drawings. Difficulty features are selection evidence, not extraction quality or an independent difficulty ranking.

Each selected original page was inspected repeatedly by the coordinator and by independent visual reviewers. Full source table bodies were audited on innovation pages 33, 38 and 78. The other twelve pages have fifteen selected source facts each. Source facts were recorded before looking at competing outputs; disagreements were checked again against original PDF crops. The public annotations publish factual assertions, source-byte hashes and coverage. The supplied PDFs, screenshots, chat messages, intermediate candidate dumps and runtime secrets remain outside this repository.

Corrected source annotations included in `engineering-catalogs-v1`:

| Case | Correction retained in frozen data |
|------|------------------------------------|
| `catalog-3-page-111` | Execution 1 covers НМЗ-45-1 through НМЗ-160-3, 24 models. Execution 2 begins НМЗ-180-1; the earlier inferred 200-3 endpoint was wrong. |
| `catalog-5-page-030` | Physical page 30 is printed page 29. |
| `catalog-5-page-035` | Physical page 35 is printed page 34. |
| `catalog-2-page-060` | Mixed section/diameter source columns retain `мм²/мм`; do not force an inferred single unit. |
| Selected OPN/small drawings | Selected dimension/value associations are scored, while physical units without an explicit source legend are unscored. |
| `catalog-4-page-078` | Preserve source `B2` unit м, Cyrillic `СЗ`, actual view А/Б and height tolerance H±2. Breaking torque has no minimum qualifier; polluted/wet discharge voltage specifies 50 Гц. |

This is a deliberately small challenge set. It does not support claims about all catalogue pages or all manufacturers. Difficulty coverage and ground truth should grow through additional independently source-reviewed cases, rather than selecting pages merely because one submitted solution performs badly.

Annotations are frozen by `checksums.json` and included in wheels. Corrections change the dataset version, retain a written erratum, and require regrading all compared immutable artifacts with the same grader. Release tags fix the code, annotations and rules used in an evaluation.

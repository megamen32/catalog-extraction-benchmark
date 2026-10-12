# Dataset: engineering-catalogs-v1

Version 1.0.0 · 15 selected pages · 500 engineering assertions. Original PDFs are not included; supply byte-identical files locally. `catalog-bench dataset --list` lists hashes; `catalog-bench dataset --export annotations` exports fixtures.

| Case | PDF | Physical / printed page | Facts | Annotation coverage |
|------|-----|-------------------------|-------|---------------------|
| `catalog-1-page-017` | opn.pdf | 17 / 17 | 15 | Selected facts only |
| `catalog-1-page-022` | opn.pdf | 22 / 22 | 15 | Selected facts only |
| `catalog-1-page-026` | opn.pdf | 26 / 26 | 15 | Selected facts only |
| `catalog-2-page-060` | Malyj-katalog.pdf | 60 / unlabelled | 15 | Selected facts only |
| `catalog-2-page-149` | Malyj-katalog.pdf | 149 / 148 | 15 | Selected facts only |
| `catalog-2-page-185` | Malyj-katalog.pdf | 185 / 184 | 15 | Selected facts only |
| `catalog-3-page-103` | Katalog-ARMATURA.pdf | 103 / 102 | 15 | Selected facts only |
| `catalog-3-page-108` | Katalog-ARMATURA.pdf | 108 / 107 | 15 | Selected facts only |
| `catalog-3-page-111` | Katalog-ARMATURA.pdf | 111 / 110 | 15 | Selected facts only |
| `catalog-4-page-033` | Katalog-Innovacionnye-izdelija-2021-2022.pdf | 33 / 33 | 108 | Full table body; page remains partial |
| `catalog-4-page-038` | Katalog-Innovacionnye-izdelija-2021-2022.pdf | 38 / 38 | 72 | Full table body; page remains partial |
| `catalog-4-page-078` | Katalog-Innovacionnye-izdelija-2021-2022.pdf | 78 / 78 | 140 | Full table body; page remains partial |
| `catalog-5-page-030` | Katalog-IZOLJaTORY.pdf | 30 / 29 | 15 | Selected facts only |
| `catalog-5-page-035` | Katalog-IZOLJaTORY.pdf | 35 / 34 | 15 | Selected facts only |
| `catalog-5-page-126` | Katalog-IZOLJaTORY.pdf | 126 / 125 | 15 | Selected facts only |

Every source is bound by SHA-256, physical PDF page (one-based), and source page count. Printed page numbers are descriptive and may differ. Case selection reasons and measured structural features are in the [packaged manifest](../src/catalog_bench/data/engineering-catalogs-v1/dataset.json).

To scan your own local catalogue for candidate pages:

```bash
catalog-bench scan inputs/catalog.pdf --output results/difficulty
```

The scanner checkpoints exact source bytes and detector version. Its structural score suggests pages for manual visual selection; it does not validate annotation accuracy or claim performance.

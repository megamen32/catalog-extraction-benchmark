# Catalogue benchmark ownership

Use this canonical checkout and main; preserve other owners' work. Existing
checkpoint/model-runner work is independent of regression registration.

The objective is a usable engineering catalogue with meaning and provenance.
Distinguish catalogue offers, project specifications, software demonstrations,
illustrative screenshots and supporting material. Literal OCR coverage alone
does not establish correct product data or correct drawing ownership.

When a new failure is discovered, capture it immediately as a source-bound
regression: original source SHA and physical page, exact saved JSON, actual
producer/model/version, failure and expected behavior. Use
`catalog-bench regressions --register CASE.json --registry REGISTRY` to retain
the evidence in a pending inbox. Preserve exact artifacts and prior cases;
do not rerun models merely to register or rescore an existing result.

New registrations start pending. Promote source-reviewed, unambiguous oracles
to a versioned corpus. Ambiguous glyphs remain pending and never enter accuracy
totals. Efficiency/format/delivery diagnostics are separate from product-fact
accuracy. Contextual plausibility is not evidence for changing a printed ID.

Keep engineering-catalogs-v1/v2 and historical grader outputs immutable and
available in parallel. The catalogue-regressions-v1 corpus is separate; its
classification assertions do not silently change the500/520-fact denominators.
Original PDFs, screenshots, credentials and raw transcripts stay outside Git.
The owner authorizes public catalogue JSON examples and compact metrics.

Verification: fast unit, focused integration, slow nightly. For regression
registration use the smallest focused unit and actual CLI checks (expected30s,
emergency300s); no automatic model runs. Root publishes scoped owned paths.

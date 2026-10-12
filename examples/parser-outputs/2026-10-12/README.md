# Retained parser outputs, 12 October 2026

These are the exact canonical JSON outputs graded in 21 direct-parser configurations: 315 attempts, 297 outputs, about 40 MB total. Each file is under 10 MiB. Failed attempts remain in the manifest and denominator; there is no fabricated output for a failed case.

The [manifest](manifest.json) records physical source page and PDF checksum, output checksum, timing, parser/adapter versions and historical v0.2.0 scoring evidence. Separate source/adapter cohorts are preserved. Missing receipt/version evidence stays missing; a declared version is not proof of execution. No values were edited for publication. Originals, model weights, native logs, transcripts and embedded images are excluded. These public catalogues and output examples were explicitly approved by their owner for publication.

Regrade an output locally with the installed benchmark, for example:

```bash
catalog-bench score --case catalog-4-page-078 examples/parser-outputs/2026-10-12/docling/catalog-4-page-078.json --output results/docling-78-v021.json
```

Label a new score with its grader version. v0.2.1 corrects drawing-token boundaries and view association; it does not rewrite the historical scores in this snapshot. Selected engineering facts are not a whole-page accuracy measure, and standalone parser results do not establish agent routing improvement.

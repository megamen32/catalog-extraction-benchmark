# Observed cost of calls that did not save a valid deliverable

Partial collector 0.1.0 reads the frozen mixed runner's failed call windows and canonical FastAgent histories. It complements usage collector 1.0.0: successful receipt-bound usage stays separate from weaker failed-window observations. It performs no model requests, changes no runtime or histories, and never converts a failed catalogue extraction into a valid output.

A failed record must have a unique role/attempt window, exact source/page match against the frozen plan, matching model and timestamp. Replayed/ambiguous windows stay unknown. Records already inside a completed native receipt are excluded; repeated provider snapshots are deduplicated. Program/contract/reasoning identities on failed records are declared frozen-runtime provenance, not a successful producer receipt. Coverage always remains partial because failed SDK requests may omit usage. Missing costs are null, not zero.

Download both standalone components into a private working directory:

```bash
curl -fL https://github.com/megamen32/catalog-extraction-benchmark/releases/download/usage-collector-v1.0.0/catalog-usage-collector-v1.0.0.py -o usage_collector.py
curl -fL https://github.com/megamen32/catalog-extraction-benchmark/releases/download/partial-usage-collector-v0.1.0/partial-usage-collector-v0.1.0.py -o partial_usage_collector.py
python partial_usage_collector.py round-1 --plan frozen-plan.json --output failed-usage.json
```

The output contains numeric source/page/model/runtime observations, no chat or private paths. Input-accounted values may be lower bounds; reasoning is an output subset, and cache is already within reported prompt totals. Native response timing is separate from the worker cycle, which can include admission waits. This is not a billing reconciliation.

The fresh first-pass round 1 report keeps failed-window costs separately: ARM103 stopped at MAX_TOKENS without JSON; IZ126 hit the native 900-second generation timeout without JSON. Retained history confirms 14 and 105 observable provider responses respectively. The benchmark counts both missing outputs as zero accuracy even though they consumed observable tokens. Raw histories remain private.

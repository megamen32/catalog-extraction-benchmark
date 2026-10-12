# Offline tokens, timing and private debug history

The independently versioned `usage_collector.py` uses existing FastAgent canonical histories and native execution receipts. It makes no provider requests, changes no native files/instructions, and does not alter the frozen mixed benchmark. Collector version1.0.0 is separate from benchmark grader0.3.0.

```bash
python usage_collector.py page-workdir --output private/page-usage.json --private-debug private/debug
python usage_collector.py catalogue-queue --tree --expected-pages 980 --output private/all-usage.json
```

Canonical `history_extractor.json`/`history_reviewer.json` are read; `_previous` backups are excluded from usage accounting. Provider snapshots are deduplicated by native role/attempt and provider/model/response timestamp. Usage is bound only when its timestamp falls within the matching source/page/model native producer receipt. All repairs are retained. Whole final numeric-attempt usage (including repeated review epochs) is separate from the exact latest accepted candidate/review producer windows. Coverage is tracked per native receipt window, and source/program/model/contract identities are kept separate. Unbound responses and failed calls make coverage partial rather than zero cost.

Input totals, uncached/cache-read/cache-write, output, reasoning, API response count, tool calls and inference duration are separate. Cached input is already part of a provider-reported prompt total, and reasoning is a subset of output. Neither is added twice. MiniMax may report a null prompt total/cache-write; summing its known uncached/cache-read components is explicitly a lower bound, not a fabricated exact total. Missing numeric fields remain null with per-field coverage counts.

Producer start/finish gives native call wall time; provider response duration gives reported inference time. Neither includes all job admission waits, and failed SDK retries may omit usage. This is observed usage, not provider billing reconciliation. Whole-queue reports include all known attempts and unknown coverage; pages not started do not become zero-token successes.

Debug collection snapshots exact original history bytes by content hash, preserving native files. Compact JSON keeps message text/tool calls/results/usage and replaces image data with decoded image hashes, byte counts and references into the preserved raw history. Raw histories and compact transcripts remain private. Only numeric/source-identity aggregates may be published using `--public-metrics`; transcript paths and contents are omitted.

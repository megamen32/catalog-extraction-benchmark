# Include catalog-to-json in the tool leaderboard

Direct user instruction: include our public catalog-to-json in the product list and ranking, since LLM-backed tools already participate. This supersedes the earlier exclusion. Side-session task only; no parent merge continuation or subagents.

1. Retain original common15 snapshot and all native candidates, annotations and grader versions unchanged. Reuse old parser/Project X rows, grade only saved agent candidates with frozen baseline0.3.0 + matching0.3.2 on the identical common15 /500.
2. Add separate first-pass rows for1.4.2/1.4.4/1.4.6 (three recorded rounds) and1.4.15 (two only), exact model/protocol/hash/time/failure evidence. No accepted-stage inheritance, reviewer-score attribution or new accuracy for1.5.26.
3. Publish a new snapshot, product mapping, dual grader output and navigation. Verify recomputation, old row equality except ranks, failed=0, source/fixture hashes, corrected page-set selection and public readback. Focused offline integration expected30s, emergency300s,1 CPU/1GiB, no swap increase, one job; temp<100MiB. No model or parser calls.
4. Scoped main commits/push only owned files, preserve foreign WIP and past snapshots; refresh history against the new published manifest.

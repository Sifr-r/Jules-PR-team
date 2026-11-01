# Candidate and evidence freshness

**Intent:** Establish exactly which content each conclusion and validation result supports.

**Questions, top down:** What was captured at C0, what team changes produced C1/C2, and are pre-existing user edits still intact? Have every writer and replacement stopped? Do the handoffs account for every assigned path/domain and terminal task state? Which source, tests, fixtures or generated files changed after each check? Does a missing second independent pass or unfinished exhaustive question leave required coverage absent?

**Evidence:** Inspect `git status --porcelain --untracked-files=all`, combined tracked diffs, deletions/renames and full relevant untracked contents when Git exists; otherwise inspect equivalent baseline/current file records. Candidate IDs are labels, not proof of unchanged content. Match commands/cwd/exit status and runtime assumptions to the exact final files. Distinguish source traces, unit/mocked execution, integration checks and unavailable environments. A worker's completion message alone is not validation.

**Bounded action and proof:** Remain read-only. Identify affected stale checks and request the narrow relevant rerun from the coordinator after writers stop. Inspect check-generated changes before accepting the result. Compare actual assigned coverage with returned artifacts, including failures/cancellations and ownership conflicts; do not infer coverage from agent count.

**Stop/handoff:** Stop when the final relevant candidate and evidence match or list exact missing proof and owners. Local/fresh work needs no imaginary PR snapshot. For an existing PR, require the separate pinned merge-base comparison and remote head/base/open-state freshness; hand remote or operational status questions to operational-readiness.

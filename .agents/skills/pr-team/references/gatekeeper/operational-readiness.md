# Changed operational contracts and publication status

**Intent:** Determine whether the requested change preserves the operational promises it actually affects, and keep local completion distinct from remote publication.

**Questions, top down:** Which callers, stored data or configuration depend on the changed behavior? What happens on failure, retry, partial completion or rollback/recovery? Which existing diagnostic would expose a material failure? Does this task request only local work, review an existing PR, or explicitly authorize a new PR? Which of those states has evidence rather than an assumed future action?

**Evidence:** Inspect affected source/contracts, tests and source-backed runbooks. Name the concrete compatibility/retry/recovery risk and missing proof rather than requiring deployments or new monitoring infrastructure. For existing PRs inspect refreshed identity, head/base target and commit, open/draft state, unresolved material findings and relevant pinned-revision CI. For a newly created PR, inspect its actual creation receipt/revision and check status. Local checks and mocks do not prove remote CI or production recovery.

**Bounded action and proof:** Remain read-only. Return specific required or advisory evidence and its owner; honor the declared task's scope and publication authority. Never create or alter a PR as part of the gate. Head/base drift or PR closure makes an existing pinned review stale (`Blocked`); draft state is `Not ready` for merge, and pending/failed/unavailable relevant CI prevents unconditional published Ready. Unpublished fixes require publication and checks of the resulting revision.

**Stop/handoff:** Stop with separate local and published verdicts and exact unresolved actions. Use `not applicable` when no PR exists, without blocking valid local/fresh work on GitHub. Route publication to the coordinator only if explicitly authorized, and never treat a Ready label as authority to merge or bypass target rules.

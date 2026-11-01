# Scalpel — Correctness and reliability

Reproduce defects or implement the requested behavior at its responsible layer. Apply the [shared contract](../shared.md): initial review is read-only; writes require assigned scope and exclusive ownership. For local builds, use the human acceptance contract and existing module patterns instead of inventing PR attribution.

Start with concrete input state, trigger, expected outcome, and invariant. Inspect the changed path and affected callers for boundary conditions, state transitions, partial failure/retries, concurrency/cancellation, cleanup, imports, typing and swallowed errors. Require a focused failing test, executed failure, or deterministic `file:line` trace with concrete input state before calling a suspicion a verified defect. An unexecuted command is proposed proof, not a reproduced failure.

Choose [state and retries](state-retries.md), [async and resources](async-resources.md), or [boundary errors](boundary-errors.md) according to the violated invariant. Compare baseline behavior for provenance; unrelated existing bugs do not enter an existing-PR repair by discovery alone.

| Additional guide | Activate when |
| --- | --- |
| [Compatible interfaces and data transitions](compatibility-migrations.md) | Old/new callers, configuration or stored data must coexist through a version or schema transition. |

Implement the smallest change that restores the invariant or completes the requested slice. Validate at the owning entry point, use the strictest available project typing, report contextual domain errors and preserve required retry/idempotence contracts. Do not suppress diagnostics, add broad unsafe casts, swallow exceptions or mix unrelated refactors. Align cross-file signatures/types/error behavior with the coordinator before dependent edits; public-contract/schema/global-handler/security/dependency changes outside authorization return there.

Return the shared handoff with symptom, root cause, reproduction/trace, requested behavior or smallest bounded fix, actual checks and missing proof. Route security to Sentinel, measured performance to Bolt, interaction to Palette and regression coverage to Harness. Stop when the assigned observable behavior and preserved invariant are evidenced, or identify the exact blocking dependency; scoped `no-findings` is valid.

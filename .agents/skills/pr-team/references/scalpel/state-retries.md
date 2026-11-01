# State transitions and retries

**Intent:** Define the state before the action, its successful result, and what must remain true after interruption or repetition.

**Questions, top down:** What triggers the transition and owns the write? Which intermediate steps are externally visible? Where can failure occur after only part of the change? If the caller retries or repeats the same action, should the operation deduplicate, resume, reject or repeat? Can stale state or competing writers violate the invariant?

**Evidence:** Describe concrete initial state and operation sequence, including failure/duplicate placement. Trace the state store, transaction/version/idempotency primitive and affected callers at `file:line`, or use isolated deterministic fixtures. Distinguish a promised idempotent operation from one whose intended behavior legitimately repeats effects; do not impose a new contract.

**Bounded action and proof:** Within owned paths, restore the transition using existing transaction/state primitives and contextual failure. Verify ordinary success plus the demonstrated partial-failure or duplicate path, checking both final state and side-effect count. Hand schema/public API changes to the coordinator when outside authority.

**Stop/handoff:** Stop after the assigned transition and its specified recovery/retry behavior are proven. Route scheduling/cancellation causes to async-resources and missing test protection to Harness. Unknown retry semantics are an intent question, not permission for a new persistence layer.

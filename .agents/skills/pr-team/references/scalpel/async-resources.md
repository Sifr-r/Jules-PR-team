# Async ordering and resource ownership

**Intent:** Find which task owns completion and cleanup for the requested operation.

**Questions, top down:** Which work may overlap, and which result is allowed to win? What happens when the user navigates away, a timeout fires, or cancellation races completion? Who closes/releases listeners, streams, handles, locks or temporary state on success, failure and cancellation? Can an old completion update new state or prevent another task from progressing?

**Evidence:** Provide a concrete schedule or lifecycle trace with the initial state and order of events at `file:line`. Use controlled completion/cancellation hooks or existing fake clocks rather than arbitrary sleeps. Show the observable stale update, leak, deadlock or lost work; a background task alone is not a defect.

**Bounded action and proof:** Under writer authority, fix ordering/ownership at the narrowest layer using existing cancellation and cleanup primitives. Preserve error visibility and the intended concurrency level. Prove the demonstrated ordering plus the normal completion path, and ensure cleanup occurs at the correct owner without double release.

**Stop/handoff:** Stop after the assigned lifecycle and race are accounted for. Route measured resource cost to Bolt, duplicate state transitions to state-retries, and deterministic scheduling tests to Harness. Do not redesign the task system for an unproven race.

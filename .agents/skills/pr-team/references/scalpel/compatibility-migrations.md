# Compatible interfaces and data transitions

**Intent:** Preserve the callers and stored data that must coexist while the requested interface, configuration or schema changes. Use this guide when a change crosses versions or requires data conversion, not for every internal refactor.

**Questions, top down:** Which old clients, readers, writers or deployments remain active? What must they continue to accept and observe? Does compatibility involve source code, wire representation, semantics, defaults or persisted values? Can the new representation be added before old use is removed? How is existing data backfilled, how are concurrent writes handled, and what proves cutover is complete? At which step does rollback stop being lossless?

**Evidence:** Record the relevant old/new caller-and-data combinations and concrete invariants. Inspect migration operations, field handling, type conversions and affected callers. Distinguish a proposed deployment sequence from an executed fixture migration. Absence of production access is not permission to run a live transition or claim it succeeded.

**Bounded action and proof:** Within authorized paths, prefer an additive transition when coexistence requires it: introduce support, convert/check data, move callers, and remove obsolete support only after its exit condition is evidenced. Validate conversion inputs, preserve strict types and contextual errors, and make retry/backfill behavior safe for its contract. Use local synthetic fixtures for old/new compatibility, partial failure, repeated execution and recovery where applicable. Do not invent a reversible rollback for destructive data loss.

**Stop/handoff:** Stop at the requested transition with compatibility proof and an explicit recovery limit. Schema/public-contract changes already authorized can proceed; material new decisions go to the coordinator. Hand acceptance checks to Harness and operational sequencing to Gatekeeper/Scribe.

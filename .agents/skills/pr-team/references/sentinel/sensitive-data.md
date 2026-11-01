# Sensitive data lifecycle

**Intent:** Identify the data owner, permitted audience, and lifetime before deciding whether output or retention is excessive.

**Questions, top down:** What secret/personal value enters this feature, and why is it needed? Where is it stored or copied? Which responses, errors, logs, telemetry, caches, files or worker handoffs expose it? Can an unauthorized actor read that destination, and does retry/cleanup behavior extend retention beyond the contract?

**Evidence:** Trace source to storage/output at `file:line`, name the affected audience and concrete consequence, and use marked synthetic values. Inspect redaction before formatting/serialization, not just the normal success response. Do not retrieve real credentials to prove reachability; record an inspected trace when execution is unavailable.

**Bounded action and proof:** Under writer authority, remove the unnecessary copy, narrow the output, or reuse the project's redaction/lifetime primitive at the owning boundary. Preserve enough context to diagnose the failure without including the value. Verify relevant success/error paths with synthetic markers and route storage/public-contract changes through the coordinator when outside authorization.

**Stop/handoff:** Stop after the assigned data path and intended audience/lifetime are checked. Hand authorization questions to the corresponding niche and cleanup/retry failures to Scalpel. A missing retention or audience contract goes to the coordinator rather than being invented.

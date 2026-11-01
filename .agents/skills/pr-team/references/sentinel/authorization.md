# Authorization boundaries

**Intent:** Identify who may do what to which resource, then test that exact policy rather than adding a new policy.

**Questions, top down:** Which actor/tenant owns the action? How is identity established? Which object or field is selected from untrusted input, and where must permission be checked? Can an alternate caller, bulk operation, ownership transition, or stale identity reach the action without the same restriction? Does a denial prevent the side effect, including after a retry?

**Evidence:** Trace the public entry point to the policy primitive and resource lookup at `file:line`. State the attacker's starting capability and concrete unauthorized result. Use synthetic users/tenants and isolated fixtures for allowed/denied cases; distinguish missing authentication from insufficient resource authorization. A policy not stated by the product is an intent gap, not proof of a vulnerability.

**Bounded action and proof:** Under writer authority, correct the owning authorization boundary with existing primitives and preserve legitimate callers. Verify a denied action has no protected side effect and the intended allowed action still succeeds. Coordinate any changed auth policy or public contract before editing it; hand shared correctness/test work to Scalpel/Harness.

**Stop/handoff:** Stop once the dispatched resource/action path and its denial behavior are evidenced. If policy intent or safe identity fixtures are unavailable, report that precise uncertainty to the coordinator. Do not widen into a repository-wide identity audit.

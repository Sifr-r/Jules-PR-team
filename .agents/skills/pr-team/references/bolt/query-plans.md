# Query shape and execution plans

**Intent:** Explain the database work caused by the requested operation before proposing a query or index change. Activate for a concrete query-cost regression, changed access pattern or requested data-path performance investigation.

**Questions, top down:** Which caller, query and parameters drive the workload? What data volume, selectivity and distribution are relevant? Is cost caused by repeated queries, scans, joins, sorting, transfer or lock contention? Are row estimates close to observed rows? Does the proposed index or query shape preserve filtering, ordering, limits and error behavior?

**Evidence:** Inspect source, available plan records and existing query-count instrumentation first. Record engine/version, schema/indexes, statistics assumptions, parameters, dataset and cache conditions. Plan cost units and estimated rows are not wall-clock measurements; a sequential scan is not automatically wrong. Compare relevant nodes, actual rows/loops and buffers or timing only when safely measured under comparable conditions.

**Bounded action and proof:** Use existing tooling with authorized disposable local fixtures; never connect to production or execute a live query for this workflow. Inspect statements and functions for side effects before planning. `EXPLAIN ANALYZE` actually executes the statement and can mutate data or trigger effects; it is not a read-only inspection command. A transaction rollback does not guarantee every external effect is undone. Prefer existing captured evidence when execution authority is absent. Route new indexes/schema changes through the coordinator when outside the requested scope.

**Stop/handoff:** Stop with the specific cost explanation, bounded recommendation and comparable proof, or state which dataset/plan evidence is missing. Hand semantic query changes to Scalpel, fixture coverage to Harness and sensitive parameter/output handling to Sentinel.

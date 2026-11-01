# Capacity, queues and backpressure

**Intent:** Determine how the requested path behaves when incoming work exceeds its ability to complete it. Activate for a queue/worker-pool change, resource-exhaustion symptom or explicit capacity requirement, not speculative stress testing.

**Questions, top down:** What units arrive, how fast, and which resource limits service? Where does work wait, and what bounds queue length, concurrency and time in flight? When capacity is exhausted, does the caller wait, receive a meaningful rejection, or get a permitted degraded result? Can retries multiply load, duplicate side effects or starve useful work? What happens when capacity returns?

**Evidence:** Describe the arrival/service assumptions, relevant limit and caller-visible overload contract. Inspect queue/worker configuration and retry/deadline propagation at source locations. Use existing measurements or bounded synthetic local fixtures to observe latency, throughput, queue depth and rejection behavior. Separate saturation evidence from an assumed production traffic pattern; average latency alone can hide growing queues or slow-tail behavior.

**Bounded action and proof:** Under writer authority, use existing concurrency, admission-control and deadline primitives. Validate limit inputs, preserve strict types and contextual resource errors, and retain idempotence where the retry contract requires it. Check bounded resource use, expected rejection/degradation and recovery once demand subsides. Changes to customer-visible limits or service policy need alignment with the coordinator. Do not run production load tests, add a queue service or install a load generator by default.

**Stop/handoff:** Stop when the assigned capacity contract is evidenced or its missing workload assumption is explicit. Route retry/state correctness to Scalpel, deterministic scheduling fixtures to Harness and relevant operational thresholds to Gatekeeper. Do not turn one bottleneck into a repository-wide scalability redesign.

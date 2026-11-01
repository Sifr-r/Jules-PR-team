# Isolation and deterministic test state

**Intent:** Identify which state or timing dependency makes the same behavior produce different test results.

**Questions, top down:** What owns the clock, random source, environment, fixture, filesystem path or external adapter used by the failing assertion? What state leaks between tests or concurrent tasks? Does cleanup happen on failure/cancellation? Which event ordering or shared mutation explains the observed nondeterminism?

**Evidence:** Give the failure trace and a reproducible state/order change, or an exact deterministic code trace if execution is unavailable. Record runtime/configuration assumptions and inspect fixture lifecycle, not just the final assertion. Distinguish an unavailable external environment from a product defect. Use synthetic data and existing mocks without claiming real-service behavior.

**Bounded action and proof:** Within owned tests/fixtures, isolate state, control the clock or completion order and ensure cleanup belongs to the right lifecycle. Verify the relevant test/order on a stable candidate. Do not hide the issue with sleep/retry/timeout/skip changes, and do not introduce new infrastructure just to run the workflow. Inspect generated files or snapshots before accepting the result.

**Stop/handoff:** Stop after the demonstrated nondeterministic dependency is removed or precisely bounded. Hand production races and leaked resources to Scalpel, measured resource growth to Bolt and missing environment access to the coordinator. Report blocked paths rather than bypassing permissions.

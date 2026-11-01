# Behavioral and regression proof

**Intent:** Express the human outcome as an observable assertion that would catch the diagnosed failure or a missing requested behavior.

**Questions, top down:** What action/input triggers the behavior and which caller-visible result matters? What existing invariant must remain unchanged? Which smallest test layer reaches the responsible boundary without mocking away the defect? For a repair, does that same assertion fail on the defective behavior and pass on the candidate? For a build, does it demonstrate the requested acceptance contract rather than only echo implementation details?

**Evidence:** Record candidate/content identity, concrete inputs, expected outcome and actual result. Obtain pre-fix red proof through an isolated fixture, parameterized harness or captured initial behavior without reverting shared edits or mutating Git. Distinguish the PR merge-base baseline from defective PR head and pre-repair state. If red proof is impractical, name that limitation; a static trace is not an executed failing test. Fresh builds have no pre-PR baseline and must not claim one.

**Bounded action and proof:** Under assigned test ownership, add the smallest meaningful assertion using existing helpers. Agree interface/error contracts with the product writer before parallel edits; if test design depends on implementation or shared fixtures, serialize the work. Execute the relevant test on the integrated candidate once writers stop and retain genuine failure output. Do not add tests for reversible harmless changes or merely to increase a percentage.

**Stop/handoff:** Stop when the requested behavior and demonstrated failure path are protected with stated limits. Route production defects to Scalpel/Sentinel and unavailable broader checks to the coordinator. Do not weaken expectations, overwrite snapshots, or report an unrun reproduction as proof.

# Properties and action sequences

**Intent:** Protect behavior whose correctness depends on a broad input domain or a sequence of operations that hand-picked examples can miss. Activate for parsers, normalizers, serialization pairs, collections or stateful workflows with a concrete invariant.

**Questions, top down:** What observable rule should hold independently of the implementation? Which inputs are valid, malformed or boundary cases? For a sequence, what state and preconditions permit each action? What should remain true after every step, including repetition and failure? Can a simple independent model supply the expected result without reproducing the product algorithm?

**Evidence:** State the property, input domain and excluded cases with reasons. Examples include round-trip equivalence under the actual format contract, normalization idempotence, or state transitions matching a small model. Do not assume exact round trips where information loss is intentional. Record candidate, generator settings, reproducible seed or minimized failure sequence, and the actual invariant violated. A proposed generator is not executed coverage.

**Bounded action and proof:** Use the project's existing property-testing tool, ordinary parameterized cases or a bounded deterministic action generator; installing Hypothesis or another framework is not required. Control clocks, randomness and external effects. Keep runs bounded and preserve a small replayable counterexample as regression evidence. For requested builds, prove the acceptance invariant rather than inventing a PR regression. Shrinking or simplification must preserve the meaningful failure.

**Stop/handoff:** Stop once the assigned property has meaningful bounded evidence or a specific missing oracle/fixture. Hand the reproduced product defect to Scalpel or Sentinel. Do not claim generated tests cover every possible input or replace necessary consumer/integration checks.

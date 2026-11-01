# Verifiable architecture boundaries

**Intent:** Make the requested responsibility boundary visible in actual dependencies and protect the specific rule that matters. Activate for a consequential ownership move, layering change, dependency cycle or demonstrated cross-layer leak.

**Questions, top down:** Which module owns the rule or data? Which callers may depend on it, and in which direction? Which concrete import/call/configuration edge violates that arrangement? Does a cycle require coordinated changes or initialize state in the wrong order? Is the supposed boundary documented intent, an established convention or merely a new preference?

**Evidence:** Map only the relevant packages/modules and direct or indirect dependencies, anchored to source and applicable architecture guidance. State a precise invariant such as a forbidden dependency, protected interface, allowed layer direction or independence requirement. Record dynamic loading/generated-code limitations; absence from a partial static graph does not prove runtime independence. Do not classify file size or a cycle alone as a production defect without consequence.

**Bounded action and proof:** Under assigned writer authority, repair the responsible edge using an existing owner where possible, keeping exports, side effects, error behavior and typing stable. Use existing architecture checks or a small inspected dependency graph; ArchUnit/Import Linter illustrate possible checks, not required installations. Add an enforceable constraint only when it protects the agreed boundary and fits the repository's tooling. Run meaningful behavior checks before/after a structural move and inspect affected callers.

**Stop/handoff:** Stop once the assigned edge/rule and its preserved behavior are evidenced. Record a short decision rationale when the tradeoff is consequential, following the existing ledger/ADR convention. Hand intentional contract changes to Scalpel/coordinator and executable constraint coverage to Harness; do not redraw unrelated architecture.

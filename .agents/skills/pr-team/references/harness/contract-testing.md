# Consumer and provider contracts

**Intent:** Verify the assumptions a real caller makes about another module, service, command or event producer. Activate when one side of an interface changes or mocked success could conceal incompatibility.

**Questions, top down:** Which consumer/version needs which request, response, event, exit status or error behavior? What provider state makes the interaction meaningful? Which fields/defaults are required by the consumer, and which variations should remain allowed? Does the provider actually satisfy those assumptions? Are timing, ordering or delivery semantics part of a separate behavior contract?

**Evidence:** Derive interactions from actual consumer usage and validate them against provider behavior at the relevant revision or a safe local implementation. A schema-valid example or consumer test against a hand-written mock proves only that example/mock; it does not establish provider compatibility. Pair the consumer expectation with provider verification and record both identities, state fixtures, matching rules and outcomes. Keep semantic workflow proof separate where request/response matching is insufficient.

**Bounded action and proof:** Prefer existing contract tooling or focused tests across the public seam; a Pact installation, broker or remote environment is not mandatory. Match strictly on meaningful obligations while allowing irrelevant extra data where the real caller does. Use synthetic isolated states and exercise the changed success/error interaction. Do not weaken expectations to fit the new implementation or call live services merely to obtain green output.

**Stop/handoff:** Stop when both sides of the assigned interaction have current proof, or label unavailable provider verification precisely. Send compatibility changes to Scalpel and documented contract drift to Scribe. An unavailable remote provider does not erase valid local evidence or justify claiming whole-system compatibility.

# Threat model and workflow abuse

**Intent:** Understand the requested feature's assets and legitimate outcome before exploring how an adversary could obtain a different outcome. Use this guide for a new trust boundary, consequential workflow, or a requested security-design assessment.

**Questions, top down:** Who owns the valuable data or action? Which actors, processes and stores exchange it, and where does trust change? What can an attacker already control? Could valid operations performed repeatedly, concurrently, out of order, or against another resource defeat the business rule? Which existing control stops that specific path, and what assumption does it require?

**Evidence:** Sketch only the relevant data flows, stores and trust boundaries, tied to source locations or a clearly proposed design. Describe a concrete abuse sequence, capability and consequence. Separate a modeled threat from a verified reachable vulnerability; STRIDE or an attack tree can prompt investigation but does not itself prove impact. Record unanswered policy questions instead of inventing restrictions.

**Bounded action and proof:** In a read-only assessment, recommend the smallest control at the responsible boundary. Under writer authority, reuse established validation/authorization primitives and check permitted and denied behavior with synthetic fixtures. Test the abuse sequence and preserved legitimate outcome without probing live accounts. Coordinate material policy changes outside existing authorization.

**Stop/handoff:** End when the assigned flow has a traceable threat/control/test relationship or explicit residual-risk owner. Send implementation invariants to Scalpel and negative-path coverage to Harness; do not expand into unrelated system modeling.

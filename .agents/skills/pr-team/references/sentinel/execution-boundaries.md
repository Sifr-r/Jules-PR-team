# Input reaching execution

**Intent:** Follow the requested input to the operation that interprets it; determine whether the input retains its intended data meaning.

**Questions, top down:** Who controls the value? Which shell, SQL/template engine, URL client, file resolver, deserializer, or downstream model consumes it? Where is interpretation introduced? Can quoting, redirects, traversal, a changed base path, or instruction-like data cross the intended boundary? Which validation or argument separation actually protects that sink?

**Evidence:** Give concrete synthetic input, the transformations applied, reachable sink at `file:line`, attacker capability and resulting impact. Inspect subprocess argument arrays and shell selection, parameterized operations, normalized path confinement, and applicable URL/redirect rules only where that path reaches them. For model input, distinguish untrusted task content from authority-bearing instructions; mere inclusion in a prompt is not proof of unsafe execution.

**Bounded action and proof:** With assigned writer ownership, validate at the responsible boundary, preserve argument/data separation and contextual failure, and reuse established escaping/parameterization rather than stacking arbitrary sanitizers. Check the attack-shaped input is safely rejected or remains data and legitimate input still works. Never execute a destructive payload or target a live service to demonstrate impact.

**Stop/handoff:** End at the assigned sink and its affected callers. Route policy questions to authorization, leakage to sensitive-data, and deterministic negative tests to Harness. Missing sink access or preconditions remain explicit uncertainty.

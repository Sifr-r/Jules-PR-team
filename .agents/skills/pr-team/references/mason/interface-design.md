# Small interfaces containing domain complexity

**Intent:** Give callers a clear way to obtain the requested capability while keeping its coordination and domain rules with their responsible owner. Activate for a requested module/API design or a demonstrated spread of complexity across callers.

**Questions, top down:** What does the caller need to accomplish, and which facts must it know to use the capability safely? Are validation, sequencing, state, retries or error interpretation repeated at call sites? Which knowledge can the owning module encapsulate without hiding an important contract? Does a proposed public method/parameter earn its complexity through real use? Is a new boundary necessary, or can an existing owner provide the behavior?

**Evidence:** Trace representative callers and the rules/configuration/order/error behavior they currently manage. Describe a proposed interface through concrete call examples, accepted inputs, results, failures and lifecycle constraints. Assess complexity moved out of callers, not implementation line count or a prescribed vocabulary. A thin pass-through is not automatically wrong when it serves an actual integration boundary.

**Bounded action and proof:** With assigned authority, design the smallest sufficient public surface, validate at its owning boundary and use strict types with contextual errors. Keep internal decomposition private where callers need not coordinate it. Prove the intended behavior through representative caller-level tests, preserving side effects and retry semantics. New feature behavior follows its acceptance contract; a structural refactor needs before/after preservation evidence. Do not introduce hypothetical adapters or replace the project's testing style merely to fit a design pattern.

**Stop/handoff:** Stop when real callers can express the requested task with a clear contract and meaningful proof. Hand intentional behavior changes to Scalpel, regression design to Harness and documented public-contract changes to Scribe/coordinator.

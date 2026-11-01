# Entry boundaries and error contracts

**Intent:** Determine which caller can provide invalid or unexpected input and what failure that caller is promised.

**Questions, top down:** What type/shape/range/path does the entry point accept? Which conversion makes malformed data meaningful? Is validation owned here or already guaranteed upstream? Which caller observes a domain error, return value or diagnostic? Can missing imports, unsafe narrowing, a swallowed exception or partial output disguise failure as success?

**Evidence:** Trace concrete valid and invalid values from entry to affected caller at `file:line`. Identify the exact violated contract and distinguish a deterministic code trace from executed proof. Check defaults, empty/missing values, conversion failures and relevant external adapter responses where they occur in this path; avoid unrelated input fuzzing.

**Bounded action and proof:** With assigned ownership, validate once at the responsible boundary, use strict project types and contextual domain errors, and preserve documented caller behavior. Check the demonstrated invalid input/error path and a legitimate input. Do not catch everything, replace useful diagnostics with generic success, or change public error contracts without alignment.

**Stop/handoff:** Stop after input ownership and caller-visible failure are clear and protected. Hand hostile-input interpretation to Sentinel, public documentation drift to Scribe and regression gaps to Harness. If expected error behavior is unknown, report that contract gap before choosing a breaking result.

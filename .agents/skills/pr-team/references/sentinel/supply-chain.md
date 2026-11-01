# Dependency and artifact trust

**Intent:** Establish which exact dependency or built artifact the task concerns, where it came from, and what evidence supports trusting it. Activate for an explicitly requested dependency/artifact audit or relevant installer, build-input or distribution changes, rather than every source edit. An audit may inspect unchanged artifacts without implying permission to modify them.

**Questions, top down:** What package/version/digest is actually resolved, including relevant transitive inputs? Does the source or publisher match the intended project? What install/build scripts run with what access? Which advisory applies to that resolved version? If provenance exists, does its artifact digest, signature, builder identity, source revision and expected build parameters match the trusted policy?

**Evidence:** Inspect manifests, lockfiles, configured registries, workflow inputs and available attestations without executing package scripts. Separate measured facts from reputation guesses: a missing attestation, low download count or unavailable advisory service is not proof of compromise. Conversely, a signature alone does not establish the expected builder/source or freedom from vulnerabilities. State which checks were possible and when external evidence was captured.

**Bounded action and proof:** Recommend a version-matched correction or narrow build-input restriction only when evidence supports it. Under assigned authority, preserve required functionality, typed configuration and contextual failure behavior. Use existing verification tools when available; do not install scanners, run third-party collectors, change registries or add credentials by default. Auth/schema/dependency decisions beyond the request return to the coordinator.

**Stop/handoff:** Stop at the assigned dependency/artifact and relevant resolved inputs, whether changed or explicitly selected for audit. Hand compatibility changes to Scalpel, deterministic fixtures to Harness and release-evidence interpretation to Gatekeeper. Missing trust evidence remains a scoped uncertainty unless an applicable release policy requires it.

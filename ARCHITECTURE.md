# Architecture ledger

## Harness portability blueprint and completion

Make the skill and the launcher usable from any agent harness, not only Codex. Keep the existing directory structure, eight specialist roles, three scope modes, launcher contract, and read-only GitHub boundary. The change is additive: the original launcher and package modules stay byte-identical, and portability is delivered by new files plus targeted edits to the skill and documentation.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| .agents/skills/pr-team/SKILL.md | Replace the Codex-only activation line with harness-neutral invocation, and add a capability-detection contract for GitHub access, delegation, and sandboxing. Preserve scope modes, role definitions, repair-round limit, and the readiness verdict. |
| .agents/skills/pr-team/HARNESSES.md | Record per-harness skill locations, invocation forms, the agent CLI registry, and the override format. Documentation only. |
| prteam/harness.py | Own the agent CLI registry, PATH detection, argv rendering, and user override loading. One responsibility: describing how to start a harness. |
| pr_team_any.py | Own the portable launcher entry point. Reuse the upstream preflight and prompt builder unchanged, then hand the prompt to the selected agent CLI. |
| tests/test_harness.py | Offline coverage for registry defaults, override parsing, selection order, and launch-argument rendering. |
| harnesses.example.json | Documented template for the operator override file. |
| README.md | Integration owner: document the portable launcher, the global install command, and the harness-neutral invocation forms. |
| AGENTS.md | Integration owner: name the new module ownership and drop the Codex-only framing. |
| ARCHITECTURE.md | Integration owner: record this blueprint, final responsibilities, and observed verification. |

Completed: the skill no longer assumes a vendor. It activates through `/pr-team`, `$pr-team`, or a plain request, and it detects the host at runtime — native GitHub tools or MCP before the `gh` CLI, the host's subagent mechanism for parallel delegation, and the host's own sandbox. When a host has no subagent mechanism the roles run sequentially, the report states that role independence was reduced, and the final verdict is Blocked with that prerequisite rather than a simulated sign-off. `pr_team_any.py` reuses the upstream preflight, scope policy, and prompt builder unchanged and adds only the choice of agent CLI; `pr_team.py` is untouched and still Codex-specific. The registry keeps the prompt on stdin so PR content never reaches the process table, and every template other than `codex` is marked unverified and overridable. All eight role references were already vendor-neutral and are unchanged.

Verification: all 66 offline unittest tests pass, 47 inherited and 19 new, run from the repository root as a git checkout. The 19 new tests cover registry defaults, the verified/unverified distinction, stdin prompt delivery, `{repo}` substitution, override precedence, malformed configuration rejection, auto-selection order, and the no-CLI error path. The original launcher, package modules, and three original test modules are byte-identical to the previous release, confirmed by SHA-256 comparison. The skill frontmatter still validates, all eight reference links resolve, and prompt construction still inlines the full skill and every role in all three modes. The agent CLI templates other than `codex` are unverified: no agent CLI was installed on the validation machine, so only the registry's detection, rendering, and override behaviour are proven. These checks do not prove live PR repair or model execution by any harness.

## GitHub publication blueprint

Publish the reviewed workspace as a proposed update to `Sifr-r/Jules-PR-team` on `codex/pr-team-workflow`, based on remote `main` at `9f9bcd563141923c77d6deec7f2cc5f3e5805bd0`. The user's publication request authorizes this release step; the launched PR-review workflow retains its read-only GitHub contract. Local Git history and configuration remain untouched.

| Path or artifact | Responsibility and acceptance |
| --- | --- |
| README.md | Use portable public setup examples without a maintainer-specific workstation path. |
| AGENTS.md | Classify preserved root governance and prompt files as legacy reference material so the Codex workflow has one active contributor contract. |
| Existing skill, launcher, tests and provenance files | Publish the complete reviewed toolkit needed to run the skill, excluding Git internals, caches and unrelated files. |
| upstream/agents/{Bolt,Palette,Sentinel}.txt | Restore the original end-of-file bytes (no final newline) so the three archived prompts' blob hashes exactly match the pinned source. |
| GitHub tree and proposed branch | Build on the pinned remote tree so existing root prompts, governance and repository history are preserved. Verify the published file contents against the local manifest. |
| ARCHITECTURE.md | Record publication scope, responsibilities and observed packaging checks. |

Independent read-only content review and offline validation precede publication. Use the connected GitHub API for a single content commit and a pull request; do not run local Git mutation commands. Live PR repair and model availability remain unverified.

Packaging completed: the public README example uses a generic installation path, contributor guidance marks retained root Jules files as legacy references, and the three archived prompt endings now match the original source. The release manifest contains 35 local files. All eleven archived files and the retained license match the pinned source blobs; remote root governance and agent prompts remain inherited from the base tree. Independent validation passed all 47 offline tests, skill frontmatter validation, and complete role bundling in all three modes. Publication verifies every resulting tree entry against this manifest before exposing the branch; the pull request and chat provide the publication receipt.

## Skill review improvement blueprint

Keep the current directory structure, eight specialist roles, launcher contract, and three scope modes. This pass changes instructions and documentation only; no new runtime files, dependencies, permissions, or GitHub actions are planned.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| .agents/skills/pr-team/SKILL.md | Coordinator owner: clarify PR-relative evidence, complete candidate inspection including new files, validation after writers stop, worker safety handoffs, and scoped versus published verdicts. Preserve scope filters, read-only GitHub access, and the two-round limit. |
| .agents/skills/pr-team/references/{sentinel,scalpel,harness,gatekeeper}.md | Correctness and evidence owner: sharpen domain proof, safe reproductions, reproducible validation and independent verdict criteria without adding universal audits or approvals. |
| .agents/skills/pr-team/references/{bolt,palette,mason,scribe}.md | Specialist owner: improve domain-specific evidence and bounded repair guidance; distinguish measured, inspected and unverified claims. |
| README.md | Integration owner: explain changed workflow guarantees and remaining limits. |
| ARCHITECTURE.md | Integration owner: record this blueprint, final responsibilities and observed verification. |

The three instruction owners may edit only their assigned paths in parallel. The integration owner reviews combined artifacts and documentation, then runs the offline unittest suite, skill frontmatter validation, bundled-reference checks, and independent scenario-based instruction review. Evaluation uses synthetic evidence only and cannot start paid Codex sessions, alter a real checkout, or mutate GitHub. Existing user-owned untracked files are preserved.

Completed: all nine instruction files were reviewed and improved within their assigned boundaries. The coordinator now requires PR merge-base evidence and accurate baseline provenance, explicitly passes worker safety rules, inspects new-file contents, waits for writers before integrated validation, defines repair-round accounting, and separates scoped local readiness from published PR status. Each specialist now states domain-specific proof and verification limits; explicit surgical targets can predate the PR. README documents the resulting guarantees. No new files or runtime changes were needed.

Verification: all 47 offline unittest tests passed; the skill frontmatter validator passed; all eight reference links resolve within the skill; UI metadata remains consistent; and prompt construction includes the full revised skill and every role in all three modes while preserving the untrusted JSON snapshot. Independent instruction simulations exercised five synthetic cases: unfinished surgical repairs with stale checks, a clean high-priority review with deferred and pre-existing issues, exhaustive coverage gaps with base drift and a failed worker, repair-round accounting after failure, and a pre-existing surgical documentation target. The review exposed round-boundary and baseline-provenance wording ambiguities, which were corrected. These are instruction and offline packaging checks, not proof of live PR repair or model execution by the launcher.

## Production-team update blueprint and completion
Keep the existing directory structure and eight specialist roles. No launcher, dependency, permission, or GitHub mutation changes are planned.

| File | Planned responsibility and acceptance |
| --- | --- |
| .agents/skills/pr-team/SKILL.md | Define a reviewable team blueprint, bounded worker lifecycle, exclusive write ownership, and evidence handoffs while preserving all three scope modes. |
| .agents/skills/pr-team/references/harness.md | Define reproducible validation handoffs and distinguish observed test results from unavailable production evidence. |
| .agents/skills/pr-team/references/gatekeeper.md | Independently assess relevant operational contracts, evidence gaps, and local versus published readiness without requiring unrelated work. |
| README.md | Explain the production-team workflow and its actual guarantees. |
| ARCHITECTURE.md | Record final responsibilities and actual verification. |

Dispatch skill and reference edits to separate owners; integrate documentation centrally. Verify with the offline unittest suite, skill validator, and an independent instruction review. No live PR or paid model execution is part of this update.

Completed: the skill now defines a reviewable blueprint, slot-aware task roster, dependency scheduling, stopped-worker ownership transfer, artifact inspection, and candidate-specific evidence freshness. Harness owns reproducible validation handoffs; Gatekeeper independently checks relevant operational contracts and unresolved team evidence. README documents the behavior. No new files or runtime changes were needed; existing prompt bundling includes the revised resources.

Verification: all 47 offline unittest tests passed after integration, and the skill frontmatter validator passed. An independent read-only instruction review found no actionable contradictions in surgical worker failure, exhaustive overlapping edits/stale checks, and documentation-only scenarios. These checks do not prove live PR repair, deployment safety, or execution by a launched Codex team.

## Baseline and source
The initial workspace contained only .git and no source or architecture ledger.
Upstream: https://github.com/Sifr-r/Jules-PR-team at 9f9bcd563141923c77d6deec7f2cc5f3e5805bd0 (MIT).
Upstream is a prompt library, not an executable multi-agent system. Preserve original material under upstream/ for provenance; runtime instructions are adapted for an existing PR.

## Acceptance
Scope expansion implemented from the pre-dispatch blueprint: prteam/scope.py owns typed mode policies and validation; cli.py parses and injects the selected scope. README.md and SKILL.md specify matching terminal/chat commands. The test suites cover scope boundaries and propagation. Existing GitHub and checkout boundaries remain in force.
One command, python pr_team.py <github-pr-url> --repo <local-checkout>, validates a clean checkout at the PR head, reads GitHub PR context, and starts Codex with multi-agent enabled. The same command shape is available through pr_team_any.py, which selects a different agent CLI without changing the preflight, the scope policy, or the prompt.
The orchestrator delegates independent reviews, scopes evidence-backed local repairs, validates, and issues a read-only Gatekeeper verdict. No GitHub writes, commits, push, checkout, reset, rebase, or merge.
A repo-local $pr-team skill supplies the same orchestration inside Codex.
Validation must cover input validation, subprocess safety, wrong/dirty checkout refusal, launch arguments, command failures, and dry-run behavior without paid model calls.

## Implemented files and single responsibilities
| Path | Responsibility |
| --- | --- |
| pr_team.py | Thin executable entry point. |
| prteam/__init__.py | Python package marker. |
| prteam/cli.py | Argument parsing, preflight, prompt construction, Codex invocation, contextual failures. |
| prteam/scope.py | Immutable validated scope selections and deterministic mode policies. |
| prteam/github.py | Strict PR URL parsing and read-only gh/Git subprocess adapters, validating remote identity and checkout head. |
| prteam/harness.py | Agent CLI registry, PATH detection, argv rendering, and operator override loading for harness-neutral launching. |
| pr_team_any.py | Portable launcher entry point. Reuses the upstream preflight and prompt builder, then hands the prompt to the selected agent CLI. |
| .agents/skills/pr-team/SKILL.md | Coordinator workflow, team blueprint and task lifecycle, exclusive ownership, bounded repair loop and final evidence contract. |
| .agents/skills/pr-team/references/bolt.md | Measured performance review and repair. |
| .agents/skills/pr-team/references/palette.md | Accessibility and interaction review and repair. |
| .agents/skills/pr-team/references/sentinel.md | Concrete security review and repair. |
| .agents/skills/pr-team/references/scalpel.md | Correctness and reliability review and repair. |
| .agents/skills/pr-team/references/harness.md | Focused regression coverage, test reliability and reproducible candidate-specific validation handoffs. |
| .agents/skills/pr-team/references/mason.md | Test-backed, behavior-preserving maintenance. |
| .agents/skills/pr-team/references/scribe.md | Source-backed documentation and handover. |
| .agents/skills/pr-team/references/gatekeeper.md | Independent read-only readiness verdict, relevant operational contracts and final-candidate evidence gaps. |
| .agents/skills/pr-team/agents/openai.yaml | Skill discovery metadata. |
| .agents/skills/pr-team/HARNESSES.md | Per-harness install locations, invocation forms, agent CLI registry, and override format. |
| harnesses.example.json | Documented template for overriding the agent CLI registry. |
| tests/test_cli.py | Offline launcher boundary and end-to-end subprocess-contract tests. |
| tests/test_scope.py | Offline mode, focus, immutability and policy-selection verification. |
| tests/test_github.py | Offline URL, metadata and checkout safety tests. |
| tests/test_harness.py | Offline agent CLI registry, override, selection, and launch-argument tests. |
| README.md | Installation prerequisites, exact activation commands and limitations. |
| AGENTS.md | Contributor safety, ownership, and actual validation commands. |
| .gitignore | Exclude Python caches only. |
| LICENSE | Original MIT license. |
| UPSTREAM.md | Pinned source attribution and adaptation summary. |
| ARCHITECTURE.md | Record architecture, responsibilities and verification. |
| upstream/README.md | Preserve original usage documentation. |
| upstream/AGENTS.md | Preserve original harness configuration as reference. |
| upstream/GOVERNANCE.md | Preserve original governance as reference. |
| upstream/agents/Bolt.txt | Preserve original performance prompt. |
| upstream/agents/Palette.txt | Preserve original accessibility prompt. |
| upstream/agents/Sentinel.txt | Preserve original security prompt. |
| upstream/agents/scalpel.md | Preserve original correctness prompt. |
| upstream/agents/harness.md | Preserve original testing prompt. |
| upstream/agents/mason.md | Preserve original maintainability prompt. |
| upstream/agents/scribe.md | Preserve original documentation prompt. |
| upstream/agents/gatekeeper.md | Preserve original readiness prompt. |

## Runtime boundaries
Python 3.10+ standard library only. Existing agent CLI and gh authentication; no added SDK, service, dependency or global configuration.
CLI passes argument arrays with shell=False, supplies the prompt through stdin, and runs codex exec --enable multi_agent --sandbox workspace-write -C <repo> -. The portable launcher substitutes one agent CLI for another through prteam/harness.py; the prompt stays on stdin and no shell is involved.
Preflight uses only git status and git log. GitHub reads use gh pr view and gh api GET; no shell-built commands or external mutations.
All specialist writing is coordinated with explicit file ownership. Gatekeeper is instructed read-only; shared native subagents inherit the session sandbox, so this is a workflow constraint, not OS isolation.

## Final integration and tradeoffs
Preflight requires a checkout-root .git marker, base-repository identity, a clean tree and the exact PR head. Inherited GH_REPO is removed from gh subprocess environments so it cannot override checkout identity. Fork-only clones may need a suitable base-repository checkout.
The launcher inlines the workflow, all eight fixed role references and an explicitly untrusted JSON metadata snapshot; no toolkit files are copied into the target checkout.
The coordinator gathers complete merge-base diff, review and CI evidence, dispatches parallel read-only reviews, deduplicates findings and assigns exclusive file ownership for repairs. At most two repair rounds precede a final Gatekeeper verdict and remote head/base freshness check.
All changes remain local. A successful Codex process exit is not a machine-checked readiness verdict; read the final report. Local-candidate readiness is distinct from published PR and CI status.
Direct $pr-team invocation requires the skill available without introducing dirty checkout files. The terminal launcher is the primary path for another existing project. Re-running after local repairs intentionally stops until the user handles those changes.

## Verification
66 offline unittest tests pass, including a complete launcher path with mocked external processes, URL and metadata validation, checkout gates, GH_REPO isolation, mode/focus validation, scope propagation, current-directory defaults, dry-run and exit handling, plus 19 agent CLI registry tests covering defaults, overrides, selection order, and launch-argument rendering. Tests use Python 3.10-compatible APIs.
The skill frontmatter validator passed. Installed Codex CLI help and feature output confirm the required exec flags and multi_agent capability.
No paid model session or live PR repair was executed: no target PR was supplied, and local gh authentication was invalid during verification.

## Scope modes and command review
--mode high-priority is the default: review for verified P0/P1 findings and repair only those; record lower-priority findings as deferred. Severity follows actual impact, not a failed CI status alone.
--mode surgical requires exactly one nonblank --focus target of at most 2,000 characters without Unicode Cc/Cf/Cs characters. It narrows detailed investigation and repair to that target, with a relevant owner, useful regression coverage and independent Gatekeeper. Urgent incidental findings are reported without silently expanding repairs. The scoped verdict cannot certify the whole PR.
--mode exhaustive prioritizes thoroughness across the complete PR and affected code paths, records changed-file/domain coverage, uses all relevant specialists and obtains a second independent read-only review pass. It does not enforce a numeric token budget or guarantee discovery of every defect. All modes retain two repair rounds, evidence gates and account/context limits.
Invalid mode/focus combinations fail as usage errors before prerequisite checks or remote reads. Focus is encoded as JSON task data in the stdin prompt rather than a subprocess argument. No extra permissions, dependencies, model selections or global configuration are introduced.
--repo now defaults to the current working directory, which must still be the matching clean PR checkout root. Existing explicit --repo commands continue to work. --help examples use the launcher's absolute path so they work from another checkout. --dry-run includes the selected scope while preserving the launch-argv JSON output.

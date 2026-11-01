# Architecture ledger

## Production-team exhaustive audit, verification, and hardening blueprint and completion (30 October 2026)

Assess the repository through its own eight-role production-team workflow (`exhaustive` scope, local repair authority, no publication), verify multi-agent orchestration across all seven domain specialists and an independent read-only Gatekeeper, and resolve verified boundary, subprocess-isolation, CLI-contract, test-isolation, and documentation findings.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| prteam/harness.py; pr_team_any.py | Infer `prompt_delivery="arg"` when `--harness-cmd` includes `{prompt}`; reject placeholders in `Harness.command`; validate `Harness.render()` inputs; fail closed on missing/unreadable explicit `--config <path>` and non-file default configs; reject empty, whitespace, control-character, and non-string harness names in `select()`/`resolve()`; avoid duplicate config reads in `select("auto")`; resolve the selected harness CLI before `gh`/`git` preflight in `pr_team_any.py`; support `codex.exe` / path stems for `--skip-git-repo-check`; report actionable command-line limit guidance when `arg` delivery fails with `OSError`. |
| prteam/github.py; prteam/workspace.py; prteam/cli.py; prteam/scope.py; prteam/__init__.py | Scrub inherited `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and `GIT_COMMON_DIR` overrides in Git subprocesses; set `GIT_OPTIONAL_LOCKS="0"` on `git` calls in `prteam/github.py`; tailor `git` vs `gh` error remediation; validate `pr` and `repo` types in `build_prompt`, `read_pr`, and `validate_checkout`; distinguish mandatory `surgical` vs optional `focused` `--focus` errors; update `prteam/__init__.py` docstring. |
| .agents/skills/pr-team/SKILL.md; HARNESSES.md; references/shared.md; references/routing.md; references/gatekeeper/ROLE.md; README.md; UPSTREAM.md | Document all nine canonical `--task` job strings and `build` initial role routing (`mason, scalpel, harness, gatekeeper`); define `P2` vs `P3`; specify early-stopped batch candidate numbering (`C1`/`C2`) and `Not ready` vs `Blocked` Gatekeeper verdict precedence; align harness tables/lists with `AUTO_PRIORITY`; document `--task` validation bounds, explicit `--config` validation, `--harness-cmd` `{prompt}` delivery, and workspace-first upstream adaptation. |
| tests/test_harness.py; tests/test_cli.py; tests/test_github.py; tests/test_workspace.py; tests/test_scope.py | Replace all eight `tempfile.TemporaryDirectory()` fixtures in `tests/test_harness.py` with in-memory `Path` mocks so the entire suite runs without OS temp-directory permissions; isolate default config paths; add unit and end-to-end offline contract tests (`PortableEndToEndContractTests`) for `F-01` through `F-06`. |
| ARCHITECTURE.md | Integration owner records the production-team blueprint, dependency direction, current file inventory, and verified offline results. |

Dependency direction (strict DAG, zero circular imports): `prteam/github.py` (stdlib) -> `prteam/{workspace,scope,routing,harness}.py` -> `prteam/prompts.py` -> `prteam/cli.py` -> `pr_team.py` and `pr_team_any.py`.

Active file inventory and single responsibilities:

| Path | Responsibility |
| --- | --- |
| pr_team.py | Thin executable entry point for Codex launches. |
| pr_team_any.py | Portable launcher entry point across registered or custom agent CLIs. |
| prteam/__init__.py | Python package marker. |
| prteam/cli.py | Argument parsing, preflight orchestration, prompt construction, Codex invocation, contextual failures. |
| prteam/scope.py | Immutable validated scope selections (`focused`, `surgical`, `exhaustive`, `high-priority`) and deterministic mode policies. |
| prteam/routing.py | Immutable validated task intent, publication authority flag, and canonical role-resource plans. |
| prteam/prompts.py | Confined, deterministic packaging of shared contracts and role/niche prompt resources. |
| prteam/workspace.py | Read-only local and fresh workspace snapshots with Git environment isolation. |
| prteam/github.py | Strict PR URL parsing and read-only `gh`/Git subprocess adapters, validating remote identity and checkout head. |
| prteam/harness.py | Agent CLI registry, `PATH` detection, single-pass argv rendering, and operator override loading. |
| harnesses.example.json | Documented template for overriding the agent CLI registry. |
| .agents/skills/pr-team/SKILL.md | Coordinator workflow, team blueprint and task lifecycle, exclusive ownership, bounded repair loop, and final evidence contract. |
| .agents/skills/pr-team/HARNESSES.md | Per-harness install locations, invocation forms, agent CLI registry, `AUTO_PRIORITY`, and override format. |
| .agents/skills/pr-team/SOURCES.md | Contributor-facing capability research provenance and deliberate integration boundaries (outside runtime packaging). |
| .agents/skills/pr-team/agents/openai.yaml | Skill discovery metadata. |
| .agents/skills/pr-team/references/shared.md | Shared worker authority, candidate tracking (`C0`/`C1`/`C2`), provenance, validation, and handoff contracts. |
| .agents/skills/pr-team/references/routing.md | Top-down intent discovery and role/niche routing catalog. |
| .agents/skills/pr-team/references/{bolt,palette,sentinel,scalpel,harness,mason,scribe,gatekeeper}/ROLE.md | Eight specialist parent role contracts and niche activation tables. |
| .agents/skills/pr-team/references/{bolt,palette,sentinel,scalpel,harness,mason,scribe,gatekeeper}/*.md | Thirty-eight focused niche guides across the eight specialist directories. |
| tests/test_{cli,scope,routing,prompts,workspace,github,harness}.py | Offline unit and end-to-end contract tests (100% in-memory, zero temp-directory or external process execution). |
| README.md; AGENTS.md; UPSTREAM.md; ARCHITECTURE.md; LICENSE; .gitignore | Operator usage, contributor safety, upstream provenance, architecture ledger, MIT license, and ignore rules. |
| upstream/** | Archived original Jules prompts and governance retained for provenance. |

Completed: Wave 1 dispatched four parallel read-only specialist audit subagents covering all seven domain roles (`Sentinel`, `Scalpel`, `Mason`, `Bolt`, `Harness`, `Palette`, `Scribe`) on candidate `C0`. Findings were deduplicated into `F-01` through `F-07`. Batch 1 (`C0 -> C1`) dispatched four parallel scoped writer subagents with strictly disjoint file ownership. All eight previously blocked temp-directory test fixtures now run completely in-memory.

Validation: all 137 discovered offline tests ran and passed (`Ran 137 tests in 0.296s OK`), with zero skipped or permission-blocked cases. All Python modules pass `py_compile`, `git diff --check` passes cleanly, all 48 skill resources and local Markdown links resolve, and an independent second review pass plus independent read-only Gatekeeper verified candidate `C1`. No paid external CLI session or Git/GitHub mutation was performed.

## Researched capability expansion blueprint and completion (30 October 2026)

Expand the existing eight roles with seventeen focused guides, emphasizing Palette's missing visual-design workflow. Preserve task/scope/authority boundaries, the standard-library launcher, offline packaging, complete coordinator availability, and narrow worker dispatch. Inspect primary skill/standard sources; write original guidance rather than importing external scripts, styles, binaries, or global skills. Keep source history outside runtime prompt resources.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| references/palette/visual-direction.md | Establish audience/surface/brand constraints and a deliberate, brief-specific visual direction. |
| references/palette/visual-system.md | Preserve or define a coherent typography, color, spacing, density, and component vocabulary. |
| references/palette/motion.md | Explain state changes with interruptible, reduced-motion-aware transitions. |
| references/palette/imagery-content.md | Select truthful product content and assets with evidence of provenance and usage rights. |
| references/palette/visual-review.md | Critique rendered states, prioritize evidence-backed design improvements, and verify the final candidate. |
| references/sentinel/threat-model.md | Identify assets, trust boundaries, and reachable workflow/business-abuse paths. |
| references/sentinel/supply-chain.md | Assess dependency and artifact identity/provenance without claiming trust from missing or superficial signals. |
| references/scalpel/compatibility-migrations.md | Preserve old/new caller and data contracts through reversible compatibility transitions. |
| references/harness/stateful-testing.md | Prove invariants over reproducible input/action sequences with existing test tools. |
| references/harness/contract-testing.md | Verify actual consumer/provider assumptions without treating mocked success as compatibility proof. |
| references/bolt/web-performance.md | Diagnose user-facing loading, interaction, and layout stability with comparable browser evidence. |
| references/bolt/query-plans.md | Inspect query plans, workload/cardinality, and actual execution costs safely. |
| references/bolt/capacity-backpressure.md | Establish bounded queue/concurrency behavior under overload and retry amplification. |
| references/mason/interface-design.md | Design a small public seam that contains domain complexity and supports meaningful tests. |
| references/mason/architecture-boundaries.md | Identify and verify concrete dependency-direction, layering, and cycle constraints. |
| references/scribe/documentation-structure.md | Match reader intent to tutorial, task guidance, reference, or explanation without unnecessary document churn. |
| references/gatekeeper/reliability-evidence.md | Assess relevant user-facing indicators, release criteria, attribution, and recovery ownership without deploying. |
| references/<role>/ROLE.md | Domain owners add discoverable triggers and distinguish requested improvements from verified defects. |
| prteam/routing.py; tests/test_prompts.py | Register every guide and verify reverse inventory, unique ownership, parent indexes, and offline packaging. |
| .agents/skills/pr-team/SOURCES.md | Contributor-facing research provenance: primary URLs, checked date, usage terms for reviewed skills, adopted/omitted ideas, and guide mapping; not runtime-bundled. |
| references/routing.md; SKILL.md; README.md; ARCHITECTURE.md | Integration owner documents optional capability selection, source trust, actual verification, and prompt-size tradeoff. |

All reference paths above are under `.agents/skills/pr-team/`. Parallel owners: Palette content; other-role content; runtime catalog/integrity. The integration owner maintains routing, source research, and the ledger. Baseline: 31 runtime resources, 65,307 resource characters, and an 81,420-character focused-UI coordinator prompt. The previous runnable offline suite passed 112/120 tests; eight known sandbox temporary-directory fixture failures are not retried. Stop when all new guides are discoverable and packaged exactly once, source provenance is recorded, requested visual design and read-only critique route correctly, and bounded offline checks/independent scenarios pass. No paid sessions or Git/GitHub mutations are authorized for implementation/testing.

Completed: seventeen independently written niche guides and eight updated role parents provide 38 niches across the existing team. Palette now owns deliberate visual creation and critique in addition to flow/accessibility. Parent/shared contracts distinguish verified behavioral defects, explicitly requested visual acceptance, and optional aesthetic observations; none grants redesign or publication authority. Routing resolves prerequisite decisions from available evidence before asking material human questions. Contributor research records Taste, Impeccable, Anthropic, Vercel, Matt Pocock, Trail of Bits, Superpowers, and the relevant primary technical sources, checked on 30 October 2026, with adopted/omitted ideas and reviewed skill usage terms. No external suite, script, binary, asset, or dependency was installed or vendored. Existing launcher, scope, permission, and publication behavior remains unchanged.

Validation: 125 tests discovered; all 117 runnable offline tests passed. Eight known permission-blocked temporary-directory fixture cases remain unrun, so this is not a full-suite pass. All 48 runtime resources are registered, nonempty, uniquely owned, discoverable through parent/routing indexes, and packaged exactly once. New tests compare the actual reference tree against the manifest and resolve local Markdown links across the complete skill. The skill validator and `git diff --check` passed. A subsequent instruction-only independent pass exercised incumbent-brand UI polish, a source-only exhaustive UI audit, query/overload work without production access, old-client compatibility with unavailable provider proof, and prototype supply-chain/release assessment. It found one narrow ambiguity around auditing unchanged artifacts, which was corrected in the guide and both activation indexes; all twelve affected catalog/resource tests passed afterward. No rendered UI, performance gain, live compatibility, model execution, or publication success is claimed from these checks.

Context tradeoff: registered resource text grew from 65,307 to 110,357 characters. A minimal workspace snapshot (`source=workspace`, `git=false`) with focused scope and canonical UI task now produces a 128,493-character coordinator prompt, compared with the 81,420-character baseline (+57.8%). The coordinator retains the complete catalog for isolated cross-domain handoffs; workers receive only shared/role/chosen-niche guidance. `SOURCES.md` remains outside runtime packaging. Character counts are not token, cost, or latency measurements.

## Workspace-first team and niche routing blueprint and completion

The team starts with `/pr-team <task> --scope focused|exhaustive` in the current workspace. A PR URL is optional. Existing-PR review remains compatible; local audits and fresh implementation do not require GitHub. An explicit publication request may authorize the launched team to create a new PR, while developing and testing this toolkit never mutates GitHub or Git history.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| prteam/routing.py; tests/test_routing.py | Validate human task data, select available role resources for known jobs, and leave natural-language intent routing to the coordinator without guessing authorization. |
| prteam/prompts.py; tests/test_prompts.py | Deterministically package shared contracts and role/niche resources, reject missing/unreadable/escaping resources, and keep dispatch instructions self-contained. |
| prteam/workspace.py; tests/test_workspace.py | Read a local workspace snapshot, including fresh directories without Git history; no GitHub dependency or state mutation. |
| prteam/scope.py; tests/test_scope.py | Add focused breadth while preserving existing surgical, exhaustive, and high-priority behavior. |
| prteam/cli.py; pr_team_any.py; tests/test_cli.py; tests/test_harness.py | Optional PR URL, task/scope/publication arguments, source-appropriate preflight, and backwards-compatible launch contracts. |
| .agents/skills/pr-team/SKILL.md; HARNESSES.md; references/shared.md; references/routing.md | Workspace-first invocation, top-down intent discovery, breadth/role separation, explicit new-PR publication authority, and portable self-contained worker contracts. |
| references/{sentinel,scalpel,harness,gatekeeper}/ROLE.md and niche guides | Preserve existing role identities and evidence standards; split security, correctness, testing, and readiness questions into focused resources. |
| references/{palette,bolt,mason,scribe}/ROLE.md and niche guides | Preserve existing specialist contracts; provide focused UI, performance, maintainability, and documentation questions. |
| README.md; ARCHITECTURE.md | Explain concrete command examples, per-file responsibilities, actual checks, and unverified live behavior. |

New resource responsibilities (paths below are relative to `.agents/skills/pr-team/references/`):

| Resource | Single responsibility |
| --- | --- |
| shared.md | Worker authority, baseline/provenance, dispatch, validation, and handoff contracts. |
| routing.md | Top-down intent discovery and relevant role/niche selection. |
| palette/ROLE.md | Own the requested user experience and route interaction questions. |
| palette/intent-flow.md | Establish actors, state transitions, recovery, and observable flow completion. |
| palette/keyboard-focus.md | Keyboard reachability, focus placement, and restoration. |
| palette/semantics.md | Accessible names, roles, relationships, and state. |
| palette/forms-feedback.md | Input validation, async feedback, success, and recovery interaction. |
| palette/responsive.md | Flow usability across content size, viewport, and zoom. |
| sentinel/ROLE.md | Own concrete security boundaries and security-specific evidence. |
| sentinel/authorization.md | Actor/action/resource permission enforcement. |
| sentinel/execution-boundaries.md | Injection, paths, subprocesses, and unsafe execution/deserialization. |
| sentinel/sensitive-data.md | Secret and sensitive-data exposure across storage and output. |
| scalpel/ROLE.md | Own requested correctness and reliability invariants. |
| scalpel/state-retries.md | State transitions, partial failure, retries, and idempotence. |
| scalpel/async-resources.md | Concurrency, cancellation, ordering, and resource cleanup. |
| scalpel/boundary-errors.md | Input boundaries, contextual errors, and caller contracts. |
| harness/ROLE.md | Own meaningful regression and acceptance protection. |
| harness/regression-proof.md | Failure-path and new-behavior proof across candidate transitions. |
| harness/isolation-flakiness.md | Deterministic clocks, fixtures, state isolation, and reproducible failures. |
| bolt/ROLE.md | Own measured performance and resource evidence. |
| bolt/latency-throughput.md | Request-path latency, workload, throughput, and measurement validity. |
| bolt/resource-lifecycle.md | CPU, memory, connection, and resource-lifetime costs. |
| mason/ROLE.md | Own cohesive responsibility boundaries and preserved behavior. |
| mason/responsibility-boundaries.md | Locate the owner of rules and prevent cross-layer contract drift. |
| mason/behavior-preservation.md | Preserve exports, ordering, side effects, and error behavior during refactors. |
| scribe/ROLE.md | Own source-backed documentation and contract communication. |
| scribe/interface-contracts.md | Document actual CLI/API/configuration inputs, defaults, outputs, and errors. |
| scribe/setup-guides.md | Validate setup/migration prerequisites and distinguish inspected from executed examples. |
| gatekeeper/ROLE.md | Independently assess scoped readiness without implementation or publication authority. |
| gatekeeper/evidence-freshness.md | Candidate completeness, stopped writers, and current validation/remote evidence. |
| gatekeeper/operational-readiness.md | Compatibility, failure/retry, diagnostic, and rollout/rollback evidence. |

Parallel ownership: runtime resource/snapshot modules, coordinator/core role resources, and UI/other specialist resources have separate owners. The integration owner handles entry points, scope, compatibility tests, and documentation. Preserve the current uncommitted harness changes. Stop once local/fresh and existing-PR launch paths package the relevant role/niche contracts, job and breadth remain independent, and offline verification covers the new boundaries. The previous baseline attempted 85 tests: 77 passed and eight temporary-directory cases encountered sandbox permissions; do not retry or bypass those locked paths.

Integration: the user explicitly approved the project-local `.agents` changes and overrode the locked-directory stop rule for this task. Approved creation of the eight directories succeeded; resource writing resumed within disjoint ownership. The coordinator receives the complete trusted catalog so isolated contexts can make evidence-backed cross-domain handoffs; initial roles are selected by job and only relevant shared/role/niche instructions are sent to each worker. Natural-language jobs are interpreted by the coordinator rather than a keyword classifier.

Completed: all eight role folders, 21 niche guides, and two shared/routing resources are present; old flat role files were removed after preserving and adapting their contracts. Fresh workspaces require no GitHub or Git history. Existing-PR commands retain their clean pinned-head preflight. Both launchers accept task and scope, and new-PR publication is separately authorized with `--publish`; the launcher never performs publication itself. Direct workspace prompt construction defaults to read-only audit authority. Codex fresh-directory launches include the no-Git-repository-check flag. UI metadata and documentation describe the same interface.

Verification: 120 tests discovered; 112 runnable offline tests passed. The eight known temporary-directory fixture cases were not retried after sandbox permission failures, so this is not a full-suite pass. Syntax validation passed for all 16 Python files and `git diff --check` passed. The skill validator passed; all 31 resource paths exactly match the catalog; all 33 skill Markdown files and 64 local links resolve. Six actual prompt-packaging scenarios passed without model execution. A no-PR exhaustive-audit dry run against the actual dirty workspace also passed, including the source snapshot, all eight role contracts, and disabled publication authority, without starting an agent. An independent instruction-only forward test reviewed audit, focused UI, fresh build, explicit new-PR publication, and task-data/README attempts to grant publication; it found bounded plans consistent with authority and source context. These checks do not prove live models, subagent execution, GitHub authentication, or new-PR publication. No paid model session, new PR, Git history change, or GitHub mutation was performed.

The sections below preserve historical blueprints and verification snapshots. Their older file paths, existing-PR-only boundaries, and test counts describe previous iterations; the completed workspace-first section above is the current architecture.

## Production-team & cross-harness hardening blueprint and completion

Harden the portable launcher, harness registry, coordinator skill, and eight specialist reference contracts so the PR team functions as a deterministic production engineering team across any agent harness while keeping the original `pr_team.py` and core `prteam/{cli,github,scope}.py` modules untouched.

| Owned paths | Single responsibility and acceptance |
| --- | --- |
| prteam/harness.py | Enforce `Harness.__post_init__` invariants (non-empty `name`/`command`, no control characters, reserved `"auto"` rejection, strict boolean `verified`, no `{prompt}` in `args` when `prompt_delivery == "stdin"`), single-pass placeholder substitution in `render()`, `select("auto")` fallback returning a `Harness` instance for custom overrides, Windows outer-quote stripping and `ValueError` handling in `custom()`, and built-in entries for `agy`, `aider`, and `goose`. |
| pr_team_any.py | Add `--config`, reject mutually exclusive `--harness` and `--harness-cmd`, and resolve the selected CLI executable via `require_command` before GitHub preflight so missing prerequisites fail early and Windows `.cmd`/`.exe` shims execute cleanly with `shell=False`. |
| harnesses.example.json | Document override templates for all unverified built-in harnesses including `agy`, `aider`, and `goose`. |
| .agents/skills/pr-team/SKILL.md | Define the 4-part harness portability & context-isolation matrix (including mandatory inlined role contracts for isolated subagent contexts and workspace-mode handling), `C0`/`C1`/`C2` candidate tracking, 9-field subagent dispatch contract, canonical finding deduplication (`F-01`, ...) and upfront cross-file contract alignment, standardized worker handoff records, and the 7-section final report contract. |
| .agents/skills/pr-team/HARNESSES.md | Document the expanded 11-CLI registry, `--config`, `--harness`/`--harness-cmd` mutual exclusion, preflight `PATH` resolution, and subagent vs single-session capability execution. |
| .agents/skills/pr-team/references/{sentinel,scalpel,harness,gatekeeper,bolt,palette,mason,scribe}.md | Align all eight specialist contracts on `C0`/`C1`/`C2` candidate tagging, provenance classification (`PR-regression`, `pre-existing-surgical-target`, `pre-existing-incidental`), self-contained subagent execution, red-to-green verification, and structured handoffs. |
| tests/test_harness.py | Offline coverage for `Harness` invariant validation, single-pass rendering, custom auto-select fallback, Windows quote stripping, `pr_team_any.py` end-to-end launch contracts, and skill/reference link and contract integrity. |
| README.md, ARCHITECTURE.md | Integration owner: synchronize documentation and architecture ledger with verified behavior. |

Completed: three parallel specialist subagents executed within disjoint file boundaries, followed by coordinator integration and verification. `pr_team.py`, `prteam/cli.py`, `prteam/github.py`, `prteam/scope.py`, and the original test modules (`test_cli.py`, `test_github.py`, `test_scope.py`) remain untouched.

Verification: all 85 offline unittest tests pass (`python -m unittest discover -s tests -v`), covering the original 47 tests plus 38 harness, portable-launcher, and skill-contract tests.

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

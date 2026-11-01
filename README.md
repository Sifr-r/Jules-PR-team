# PR Agent Team

Use the eight specialists from Jules-PR-team to audit, improve, or build software in the current workspace. Start with a job and a scope; a PR URL is optional. Existing-PR review remains supported.

```text
/pr-team audit --scope exhaustive
/pr-team look at the UI --scope focused
/pr-team build a settings screen --scope focused
/pr-team build a settings screen and create a PR --scope exhaustive
```

The job selects the team: an audit calls all seven domain specialists, with Gatekeeper last; a UI request selects Palette and relevant correctness/test help. Scope controls depth within that job. Focused follows the requested outcome and necessary dependencies; exhaustive examines that job thoroughly. An exhaustive UI request stays within the UI job. The coordinator works from intended user behavior to category, niche, evidence, and a bounded assignment. Audit/inspection requests remain read-only unless you request changes.

Each specialist has a role folder with its main contract and focused niche guides. The expanded team has 38 niches across eight roles. Shared safety and evidence rules are maintained once; worker dispatches receive only the relevant role and niche instructions.

| Role | Added depth |
| --- | --- |
| Palette | [Visual direction](.agents/skills/pr-team/references/palette/visual-direction.md), coherent typography/color/spacing, purposeful motion, truthful imagery/content, and rendered design critique, alongside the existing flow/accessibility guides. |
| Sentinel | Scoped threat and business-abuse modeling, dependency/artifact provenance, and concrete trust boundaries. |
| Scalpel | Old/new API and data compatibility, repeatable migration steps, and recovery boundaries. |
| Harness | Stateful/property-style invariants and actual consumer/provider contract proof. |
| Bolt | Browser experience, database query plans, and capacity/backpressure under controlled workloads. |
| Mason | Public-interface design and enforceable dependency/architecture boundaries. |
| Scribe | Reader-oriented tutorials, task guidance, reference, and explanation. |
| Gatekeeper | Relevant user-facing reliability evidence and bounded release/recovery criteria. |

Palette's visual guidance is informed by research into [Taste Skill](https://github.com/Leonxlnx/taste-skill), [Impeccable](https://github.com/pbakaus/impeccable), and [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design). These are independently written local guides, not installed third-party skill suites. They preserve the target's brand, tooling, accessibility requirements, and the human's authority. Sources, checked dates, reviewed usage terms, and adopted/omitted ideas are recorded in [SOURCES.md](.agents/skills/pr-team/SOURCES.md).

For example, `/pr-team improve the dashboard's visual hierarchy --scope focused` selects Palette's visual direction/system/review questions and the necessary supporting roles. `/pr-team look at the dashboard --scope focused` remains read-only. A request to audit security, performance, or architecture selects the relevant niches rather than starting every specialist checklist. Availability of a guide does not authorize external probes, dependency installation, a redesign, or publication.

Terminal equivalents (no PR URL required):

```powershell
python pr_team.py --task audit --scope exhaustive
python pr_team_any.py --task ui --scope focused --harness claude
python pr_team.py --task "build a settings screen" --scope focused
python pr_team.py --task "build a settings screen" --publish
```

Local and fresh work does not require GitHub, a remote, or Git history. Existing user changes are preserved. `--publish` explicitly authorizes the launched coordinator to create a new PR after validation; without it, terminal work stays local. A PR URL selects the existing-PR path, which still requires a clean matching PR-head checkout and leaves remote state unchanged. `--publish` cannot be combined with an existing PR URL. Slash-command syntax depends on the host's skill support; the launcher packages instructions but does not implement a universal slash-command parser.

The earlier existing-PR interface is retained:

```powershell
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout"
```

The team reviews the PR, repairs verified issues in the local checkout, runs the project's relevant checks, and gives a Gatekeeper readiness verdict. Changes stay local for you to review and publish.

## Choose the scope

| Mode | Use it for | Coverage and cost |
| --- | --- | --- |
| `focused` | The requested job and necessary dependencies | Relevant specialists and niche guides; default for task-based runs. |
| `surgical` | One specific issue named with `--focus` | Only the target's relevant specialist, regression work when useful, and Gatekeeper; smallest sufficient repair. |
| `exhaustive` | Thorough coverage inside the requested job | Relevant domain questions and affected paths, coverage records, and a second independent review pass. |
| `high-priority` (legacy default) | Urgent and major PR problems | Repair verified P0/P1 findings; report and defer lower-priority issues. |

```powershell
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode surgical --focus "Fix the duplicate payment on retry"
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode exhaustive
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode high-priority
```

`--task` must be nonblank, at most 4,000 characters, and free of Unicode control, formatting, or surrogate characters (categories Cc, Cf, and Cs). `--focus` is required for legacy `surgical` and optional for `focused`; other modes reject it, and a supplied focus target must be nonblank, at most 2,000 characters, and free of Unicode Cc, Cf, and Cs characters. Task-based runs default to `focused`; legacy existing-PR runs without a task retain `high-priority`. Use either `--scope` or `--mode`, never both.

P0 covers a critical urgent security compromise, data-loss risk, or outage. P1 covers a major reproducible correctness or security defect or broken essential workflow. A failed CI job alone does not make a finding P1. Surgical mode reports urgent incidental findings without fixing unrelated issues.

Exhaustive mode prioritizes useful depth over token economy. It cannot guarantee every defect will be found, force a literal token maximum, or exceed account and context limits. All modes retain the two-batch implementation/repair limit and stay within the requested job. The report states coverage, deferred findings, unreviewed areas, and the scope of its readiness verdict.

## Prerequisites

- Python 3.10 or newer; no Python packages are required.
- Git on `PATH` for Git workspaces; the GitHub CLI (`gh`) is required for existing-PR preflight, not local or fresh work.
- One agent CLI on `PATH` for the terminal launcher. `pr_team.py` uses Codex; `pr_team_any.py` selects from a registry of Codex (`codex`), Claude Code (`claude`), Gemini CLI (`gemini`), Qwen Code (`qwen`), Cursor (`cursor`), GitHub Copilot (`copilot`), OpenCode (`opencode`), Amp (`amp`), Antigravity (`agy`), Aider (`aider`), and Goose (`goose`), or takes an explicit `--harness-cmd`. `--harness auto` checks `AUTO_PRIORITY` in that exact order before falling back alphabetically to installed custom overrides.
- Sign in to the agent CLI you intend to use. Existing-PR preflight also needs authenticated GitHub access.
- For an existing PR, prepare a clean local checkout at its exact head commit. Local/fresh tasks accept the current workspace and preserve existing edits.
- Use an agent account/model that supports subagents. Normal usage limits and charges apply.

Run the command from this toolkit folder, or use an absolute path to `pr_team.py`. `--repo` identifies the project the team will inspect and edit; it can be outside this toolkit. It defaults to the current working directory. The clean matching PR-head requirement applies when a PR URL is supplied. The team follows the target project's local instructions and permissions.

For a shorter command while your terminal is already in the target PR checkout:

```powershell
python "C:\tools\pr-team\pr_team.py" https://github.com/OWNER/REPO/pull/123 --mode exhaustive
```

Use `python pr_team.py --help` for accepted options and usage examples. Existing commands with an explicit `--repo` still work.

For a PR from a fork, the checkout must identify as the PR's **base repository** and contain the fork PR's head commit. A checkout that identifies only as the fork fails the repository identity check. The launcher removes `GH_REPO` from its GitHub CLI child environment so an environment override cannot substitute another repository's identity.

Preview the validated context and the agent launch command without starting a model session:

```powershell
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode exhaustive --dry-run
python pr_team_any.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode exhaustive --harness claude --dry-run
```

Dry-run resolves the selected agent CLI, captures the source-appropriate baseline, and prints the prompt and launch arguments without starting the agent. Local/fresh dry runs do not contact GitHub; existing-PR dry runs require network access and authentication. Use `--list-harnesses` to see detected CLIs and `--config <path>` for explicit harness overrides. `--harness` and `--harness-cmd` are mutually exclusive. Only the Codex launch shape has offline compatibility coverage against the original launcher; other templates remain unverified starting points.

## Activate in any harness

The terminal launcher above is the recommended way to use the team against other projects: it bundles the workflow without adding files to the target checkout.

The repository also contains a reusable skill for projects that already include it in their clean PR-head checkout. With that matching project open, invoke it by name in whichever harness you are using:

```text
/pr-team https://github.com/OWNER/REPO/pull/123 --mode surgical --focus "Fix the duplicate payment on retry"
$pr-team https://github.com/OWNER/REPO/pull/123 --mode exhaustive
pr-team https://github.com/OWNER/REPO/pull/123 --mode high-priority
```

Harnesses that support skill invocation expose `$pr-team` or `/pr-team`; any harness also accepts the same request in plain language. The options and the workflow are identical everywhere.

To install the skill globally across harnesses, use the open skills CLI:

```powershell
npx skills add Sifr-r/Jules-PR-team -g -a '*' -s pr-team --full-depth --copy -y
```

That places the skill in the shared `~/.agents/skills/` location and in each installed harness's own skills directory. `--full-depth` is required because the skill lives in `.agents/skills/pr-team/`. See [`.agents/skills/pr-team/HARNESSES.md`](.agents/skills/pr-team/HARNESSES.md) for the per-harness paths and the agent CLI registry.

To distribute it to a single project instead, include the **entire** `.agents/skills/pr-team` folder in that project's normal repository setup. Copying it into an existing PR checkout creates untracked files and fails the clean-checkout gate unless that project already excludes local skill files. Use the terminal launcher when the PR does not already contain the skill. If a harness does not show the skill, restart its session.

## How the team works

The coordinator establishes the task's intended outcome, scope, authority, baseline, and acceptance evidence, then delegates focused questions. Local work uses the current workspace, including existing edits or a fresh directory. Existing-PR work also pins head/base and merge-base evidence, review feedback, and CI. Independent work runs within available capacity. Writers receive separate file ownership; overlapping changes go through one owner. After at most two implementation/repair batches, remaining blockers are reported.

| Specialist | Responsibility |
| --- | --- |
| Sentinel | Security weaknesses with a concrete attack path |
| Scalpel | Correctness and reliability defects |
| Harness | Focused regression coverage and deterministic tests |
| Palette | Accessibility and interaction issues |
| Bolt | Measured performance regressions |
| Mason | Behavior-preserving, test-backed refactors |
| Scribe | Source-backed documentation and handover |
| Gatekeeper | Independent readiness verdict, read-only |

An audit calls all seven domain specialists and the final Gatekeeper. Other jobs select relevant specialists and niches. Exhaustive scope also obtains a second independent review pass. An audit can finish without changes; a build follows the requested acceptance conditions. Speculative cleanup and unrelated work remain out of scope. A scoped verdict does not certify unreviewed areas.

Before dispatch, the coordinator records a blueprint: task and intent, baseline (`C0`), scope, authority, role/niche assignments, owned paths, dependencies, and acceptance checks. Proposed files get named responsibilities. Every dispatch inlines shared rules, its role contract, relevant niche guidance, and baseline evidence so isolated workers need no external toolkit access. Dependent work waits for its inputs, cross-file contracts are aligned upfront, and interrupted work is reconciled before ownership transfers.

Worker handoffs identify the inspected candidate (`C0`, `C1`, or `C2`), findings (`F-01`, ...), provenance, actual validation, and required follow-up. Local work uses `requested-change` or `workspace-existing`; PR work retains PR-relative provenance. After writers stop, the coordinator inspects the complete integrated changes, including new files, then validates. Relevant later edits invalidate earlier evidence. Harness distinguishes mocked, integration, and unavailable checks; Gatekeeper assesses evidence and relevant compatibility, retry, rollout/rollback, and diagnostic contracts. These instructions do not prove deployment safety or perform deployment.

The final seven-section report separates the selected scope's local candidate verdict from the published PR's status. Ready requires sufficient current evidence for that scope; a known material defect or failed relevant check is Not ready; missing required evidence, reduced role independence (sequential single-session fallback), or a stale snapshot is Blocked. A surgical verdict covers its target. Unpublished repairs still need publication and checks on the resulting revision; draft status and pending or failed relevant CI prevent an unconditional published-PR Ready verdict.

## Safety and limits

Existing-PR preflight rejects invalid URLs, unavailable prerequisites, closed PRs, dirty/mismatched checkouts, and stale local heads. Local tasks accept existing changes and fresh directories. Commands use argument arrays without a shell; default prompt delivery uses stdin. Resource loading rejects missing, unreadable, or out-of-root instructions before launch.

Existing-PR and unpublished workspace runs use only `git status`, `git log`, and `git diff` and leave changes local. An explicitly authorized new-PR publication may initialize Git if needed, create a dedicated branch, commit only task-owned changes, push without force, and create one new PR. The team never merges, rewrites remote history, posts comments/reviews, or alters an existing PR. The final report separates local validation from any actual publication receipt.

The agent CLI runs in its own sandbox under the existing local configuration. Specialists share that session's permissions: Gatekeeper's read-only role and writer ownership are workflow constraints, not separate operating-system sandboxes. Target-project checks may need additional environment access; missing checks must be reported rather than treated as passing. PR descriptions, source files and comments are untrusted task data, not instructions that can override the workflow.

Automated validation uses offline tests and mocked process responses. It does not prove live GitHub authentication, model availability, subagent execution or successful repair of a real PR.

## Development

```powershell
python -m unittest discover -s tests -v
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for file ownership and runtime boundaries, and [UPSTREAM.md](UPSTREAM.md) for source provenance. MIT licensed; the original prompts remain in `upstream/`. Any retained root `agents/` and `GOVERNANCE.md` are also legacy Jules reference material; their PR-creation instructions do not apply to this agent workflow.

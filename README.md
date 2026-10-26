# PR Agent Team

Run the eight specialists from [Jules-PR-team](https://github.com/Sifr-r/Jules-PR-team) as one coordinated agent team against an existing pull request. The team runs in any harness that supports the open Agent Skills layout, and the terminal launcher can drive any agent CLI.

```powershell
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout"
```

The team reviews the PR, repairs verified issues in the local checkout, runs the project's relevant checks, and gives a Gatekeeper readiness verdict. Changes stay local for you to review and publish.

## Choose the scope

| Mode | Use it for | Coverage and cost |
| --- | --- | --- |
| `surgical` | One specific issue named with `--focus` | Only the target's relevant specialist, regression work when useful, and Gatekeeper; smallest sufficient repair. |
| `exhaustive` | The most thorough review of the PR and affected code paths | Every relevant specialist, changed-file coverage, and a second independent review pass; highest expected token use. |
| `high-priority` (default) | Urgent and major problems | Repair verified P0/P1 findings; report and defer lower-priority issues. |

```powershell
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode surgical --focus "Fix the duplicate payment on retry"
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode exhaustive
python pr_team.py https://github.com/OWNER/REPO/pull/123 --repo "C:\path\to\checkout" --mode high-priority
```

`--focus` is required only for `surgical` and rejected with other modes. It must be nonblank, at most 2,000 characters, and contain no Unicode control, formatting, or surrogate characters (categories Cc, Cf, and Cs). Omitting `--mode` selects `high-priority`.

P0 covers a critical urgent security compromise, data-loss risk, or outage. P1 covers a major reproducible correctness or security defect or broken essential workflow. A failed CI job alone does not make a finding P1. Surgical mode reports urgent incidental findings without fixing unrelated issues.

Exhaustive mode prioritizes useful depth over token economy. It cannot guarantee every defect will be found, force a literal token maximum, or exceed account and context limits. All modes keep the two-repair-round limit and stay within the PR's scope. The report states coverage, deferred findings, unreviewed areas, and the scope of its readiness verdict.

## Prerequisites

- Python 3.10 or newer; no Python packages are required.
- Git and the GitHub CLI (`gh`) on `PATH`.
- One agent CLI on `PATH` for the terminal launcher. `pr_team.py` uses Codex; `pr_team_any.py` selects from a registry of Codex, Claude Code, Gemini CLI, Qwen Code, Cursor, GitHub Copilot, OpenCode, and Amp, or takes an explicit `--harness-cmd`.
- Authenticate using `gh auth login -h github.com`, and sign in to the agent CLI you intend to use (`codex login`, and so on).
- Prepare a clean local checkout of the target repository at the PR's exact head commit. The launcher does not fetch or switch branches.
- Use an agent account/model that supports subagents. Normal usage limits and charges apply.

Run the command from this toolkit folder, or use an absolute path to `pr_team.py`. `--repo` identifies the project the team will inspect and edit; it can be outside this toolkit. When omitted, it defaults to the current working directory, which must be the clean matching checkout root. The team follows that project's local instructions and permission boundaries.

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

Dry-run still performs read-only GitHub and Git preflight. It requires network access and GitHub authentication. It prints the selected scope, validated prompt and launch arguments without writing files or running the agent. Use `--list-harnesses` to see which agent CLIs the registry detects.

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

The coordinator validates the selected mode, pins the PR head and base, examines the PR's merge-base diff, review feedback and CI evidence, and delegates reviews according to that mode. It distinguishes defects introduced or worsened by the PR from older problems; an explicit surgical target can name an existing defect. Independent work runs in parallel within the available concurrency limit. It confirms findings before assigning repairs. Writers receive separate file ownership; overlapping changes go through one owner. After at most two repair rounds, it reports remaining blockers instead of looping indefinitely.

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

The coordinator chooses relevant specialists; every run need not use all eight. Exhaustive mode also obtains a second independent review pass. A clean PR can finish without changes. Speculative cleanup and unrelated feature work are out of scope. Finishing a surgical target does not certify unreviewed parts of the PR; deferred material findings remain visible to Gatekeeper.

Before dispatch, the coordinator records a team blueprint: the pinned revision, selected scope, relevant roles, file ownership, dependencies, and acceptance checks. Proposed new files get a named responsibility. Independent workers run within the session's available slots; dependent edits wait for their inputs and overlapping files have one writer. Failed or interrupted work is reconciled before a replacement takes ownership.

Worker handoffs identify the candidate they inspected, findings or changes, exact validation outcomes, and unresolved work. The coordinator waits for writers to finish, inspects tracked changes and the contents of new untracked files, then validates the integrated candidate. Check-generated changes require inspection; relevant later edits invalidate earlier evidence. Harness distinguishes observed local checks from mocked, unavailable, or remote evidence. Gatekeeper assesses operational contracts such as compatibility, retry safety, rollout, rollback, and diagnostics when the PR affects them. These instructions support a production review; they do not prove deployment safety or perform a deployment. No extra roles, services, or runtime dependencies are required.

The final report separates the selected scope's local candidate verdict from the published PR's status. Ready requires sufficient current evidence for that scope; a known material defect or failed relevant check is Not ready; missing required evidence or a stale snapshot is Blocked. A surgical verdict covers its target. Unpublished repairs still need publication and checks on the resulting revision; draft status and pending or failed relevant CI prevent an unconditional published-PR Ready verdict.

## Safety and limits

The launcher rejects invalid PR URLs, unavailable prerequisites, closed PRs, dirty checkouts, repository mismatches and a local commit that differs from the PR head. Command arguments are passed without a shell, and the prompt is supplied through standard input.

The team does not commit, push, merge, change branches, post GitHub comments or submit reviews. It uses only `git status`, `git log`, and `git diff`. The final report lists local changes, observed validation results, unresolved findings and readiness. Publishing the changes is a separate user action.

The agent CLI runs in its own sandbox under the existing local configuration. Specialists share that session's permissions: Gatekeeper's read-only role and writer ownership are workflow constraints, not separate operating-system sandboxes. Target-project checks may need additional environment access; missing checks must be reported rather than treated as passing. PR descriptions, source files and comments are untrusted task data, not instructions that can override the workflow.

Automated validation uses offline tests and mocked process responses. It does not prove live GitHub authentication, model availability, subagent execution or successful repair of a real PR.

## Development

```powershell
python -m unittest discover -s tests -v
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for file ownership and runtime boundaries, and [UPSTREAM.md](UPSTREAM.md) for source provenance. MIT licensed; the original prompts remain in `upstream/`. Any retained root `agents/` and `GOVERNANCE.md` are also legacy Jules reference material; their PR-creation instructions do not apply to this agent workflow.

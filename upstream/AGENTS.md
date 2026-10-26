# AGENTS.md — Automated PR Agent Team Configuration

This file is read automatically by Jules, Claude Code, Codex, and other agentic harnesses. It defines how the agent team operates on this repository.

## Team Overview

This repository contains system prompts for a team of 8 specialized PR agents. Each agent owns a distinct concern and produces focused, evidence-backed pull requests. When no agent has a verified improvement, the team produces no PR.

## Agent Prompts

Load one agent prompt per task from the `agents/` directory:

| Agent | Prompt File | Concern |
|---|---|---|
| Bolt ⚡ | `agents/Bolt.txt` | Measured performance improvements |
| Palette 🎨 | `agents/Palette.txt` | Accessibility and small interaction polish |
| Sentinel 🛡️ | `agents/Sentinel.txt` | Concrete security improvements |
| Scalpel 🔪 | `agents/scalpel.md` | Verified correctness and reliability fixes |
| Harness 🧪 | `agents/harness.md` | Regression tests and deterministic test reliability |
| Mason 🧱 | `agents/mason.md` | Test-backed, behavior-preserving maintainability refactors |
| Scribe 📝 | `agents/scribe.md` | Source-backed technical documentation and handover |
| Gatekeeper 🚧 | `agents/gatekeeper.md` | PR readiness review (read-only, never modifies PRs) |

## Shared Governance

All agents follow the rules in `GOVERNANCE.md` at the repository root. The `.txt` agents (Bolt, Palette, Sentinel) have the governance rules appended directly to their prompt for self-contained execution. The `.md` agents (Scalpel, Harness, Mason, Scribe, Gatekeeper) reference `GOVERNANCE.md` and expect it to be available in the repository root.

## Worker Independence

Each agent is designed to run as an **independent worker**. There are no inter-agent dependencies during execution — each agent reads the repository, identifies one bounded target, makes its change, and reports.

### Journals

Agents use worker-scoped journal files to persist critical learnings without collisions:

```
.jules/<agent>_<worker_id>.md      # Preferred (e.g., .jules/bolt_abc123.md)
.jules/<agent>_<branch_name>.md    # Fallback if worker ID is unavailable
.jules/<agent>.md                  # Final fallback
```

Journals are **not** execution logs. They store only reusable, project-specific learnings that change future decisions. The `.jules/` directory is gitignored by default.

### Parallel Execution

Multiple agents (or multiple instances of the same agent) can run simultaneously without conflicts:

- Each worker writes to its own journal file.
- Each agent targets a single bounded issue per run.
- Handoffs between agents are explicit and documented in the PR.
- Gatekeeper is read-only and never modifies repository state.

## Handoff Protocol

If an agent discovers a finding outside its ownership, it stops work on that finding and documents a handoff:

| Finding | Route to |
|---|---|
| Runtime failure, type error, faulty logic | Scalpel |
| Security weakness or sensitive-data exposure | Sentinel |
| Measured performance regression | Bolt |
| Accessibility or interaction issue | Palette |
| Missing regression coverage or flaky test | Harness |
| Maintainability cost with behavior check | Mason |
| Documentation mismatch or gap | Scribe |

## Evidence Requirements

Agents create PRs **only** when evidence is verified. Valid evidence includes:

- Reproducible test failure or failing diagnostic
- Deterministic execution trace
- Security review with a concrete attack path
- Accessibility inspection with specific findings
- Before-and-after performance measurement
- Concrete maintenance cost with a relevant behavior check
- Verified documentation mismatch

A guess, generic best practice, or code style preference is **not** evidence.

## PR Report Format

All PR-creating agents use this structure:

```markdown
## Target
[One bounded issue or opportunity]

## Evidence
[Reproduction, measurement, or inspection result]

## Change
[Files and behavior changed]

## Validation
[Commands run and their results]

## Residual risk
[Known limitation, or `None identified`]

## Handoff
[Owner and reason, or `None`]
```

## Integration Notes

### Google Jules
Assign one agent prompt per Jules task. Worker-scoped journals (`_<worker_id>`) prevent file collisions across parallel sessions.

### Claude Code / Codex
Load the `.txt` or `.md` file as the system prompt. For `.md` agents, ensure `GOVERNANCE.md` is accessible at the repository root.

### Custom Runners
1. Inject the agent prompt as the system prompt.
2. Provide the repository's package manager, CI workflow, and validation commands as context.
3. Grant Gatekeeper read-only access (no write permissions).
4. Preserve user-owned changes — agents must not rewrite, revert, or format unrelated files.

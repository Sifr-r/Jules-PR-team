# Automated PR Agent Team

A team of specialized AI agents that create focused, evidence-backed pull requests. Each agent owns a distinct concern and hands off cross-cutting findings to the appropriate specialist.

| Agent | File | Role | Can create PRs |
|---|---|---|---:|
| Palette | `agents/Palette.txt` | Accessibility and small interaction improvements | Yes |
| Sentinel | `agents/Sentinel.txt` | Concrete security improvements | Yes |
| Bolt | `agents/Bolt.txt` | Measured performance improvements | Yes |
| Scalpel | `agents/scalpel.md` | Verified correctness and reliability fixes | Yes |
| Harness | `agents/harness.md` | Regression tests and deterministic test reliability | Yes |
| Mason | `agents/mason.md` | Test-backed, behavior-preserving maintainability refactors | Yes |
| Scribe | `agents/scribe.md` | Source-backed technical documentation and handover | Yes, on demand |
| Gatekeeper | `agents/gatekeeper.md` | PR readiness review | No |

## Quick Start

The agent prompts are **pre-migrated, fully self-contained, and optimized for all agentic harnesses** (Google Jules, Claude Code, Codex, Devin, and custom runners). Each worker runs independently with isolated journals to prevent parallel-run conflicts.

1. Copy this repository into your target project (or reference it as a submodule).
2. Load agent prompt files from `agents/` into your agent runner's system prompt configuration.
3. Place `GOVERNANCE.md` at your repository root so agents can read the shared contract.
4. Configure the runner to provide each agent with the repository's actual commands, current diff, and local conventions.
5. Ensure the runner preserves user-owned changes and grants Gatekeeper read-only review authority.

### Google Jules

In Jules, each agent runs as an independent worker session. Assign one agent prompt per task. The worker-scoped journal naming (`_<worker_id>` / `_<branch_name>`) prevents file collisions when multiple Jules workers execute in parallel.

### Claude Code / Codex / Other Harnesses

Each `.txt` or `.md` file in `agents/` is a complete, standalone system prompt. The Bolt, Palette, and Sentinel prompts include the full governance contract appended at the end, so they work without needing a separate governance injection step.

For Harness, Scalpel, Mason, Scribe, and Gatekeeper, prepend or inject `GOVERNANCE.md` into the system prompt, or instruct the agent to read it from the repository root (already referenced in each prompt).

## Operating Model

Run one PR-creating specialist for a verified target. Mason requires a relevant behavior check before it refactors; Scribe runs only for a source-backed documentation need. Use Gatekeeper after the specialist reports its evidence.

The team is deliberately **not** a pool of agents that generates daily activity: when no agent has a bounded, evidence-backed improvement, it produces no PR.

See `GOVERNANCE.md` for the full ownership and handoff contract.

## Repository Structure

```
├── AGENTS.md              # Jules/harness configuration file
├── GOVERNANCE.md           # Shared operating rules, ownership map, and PR format
├── MIGRATION.md            # Historical: migration steps (already applied)
├── README.md               # This file
├── .gitignore              # Ignores .jules/ journals
└── agents/
    ├── Bolt.txt            # ⚡ Performance agent (self-contained + governance)
    ├── Palette.txt         # 🎨 UX/a11y agent (self-contained + governance)
    ├── Sentinel.txt        # 🛡️ Security agent (self-contained + governance)
    ├── scalpel.md          # 🔪 Correctness agent
    ├── harness.md          # 🧪 Test coverage agent
    ├── mason.md            # 🧱 Maintainability agent
    ├── scribe.md           # 📝 Documentation agent
    └── gatekeeper.md       # 🚧 PR review agent (read-only)
```

## License

MIT

# Harness compatibility

The skill uses `SKILL.md`, shared resources, and eight role folders. Its workflow is vendor-neutral; detect the host's actual GitHub, delegation, and filesystem capabilities instead of assuming them from a CLI name.

## Install and invoke

The skill lives at `.agents/skills/pr-team/`. The existing install form is:

```powershell
npx skills add Sifr-r/Jules-PR-team -g -a '*' -s pr-team --full-depth --copy -y
```

The skills CLI reports the host locations it supports. `--copy` copies resources rather than linking them. For project-local installation, copy the complete skill folder, including `references/`; preserve a clean checkout when using the existing-PR launcher.

| Job | Invocation |
| --- | --- |
| Current workspace audit | `/pr-team audit --scope focused` |
| UI investigation | `$pr-team look at the UI --scope exhaustive` |
| Build requested behavior | `/pr-team build a settings screen --scope focused` |
| Terminal local task | `python pr_team.py --repo <workspace> --task "look at the UI" --scope exhaustive` |
| Terminal portable host | `python pr_team_any.py --repo <workspace> --task "build a settings screen" --scope focused --harness claude` |
| Explicit new PR after implementation | `python pr_team_any.py --repo <workspace> --task "build a settings screen" --scope focused --publish --harness claude` |
| Existing PR compatibility | `python pr_team.py <PR-URL> --repo <checkout> --mode surgical --focus "reproduce and fix the reported failure"` |
| Explicit harness config | `python pr_team_any.py --repo <workspace> --task audit --config path/to/harnesses.json --harness claude` |

A PR URL is optional. Local/fresh tasks do not require GitHub, `gh`, a remote or Git history. Omitting both task and PR selects a focused, read-only workspace audit. Audit/review/look-at requests are read-only unless the human requests changes; build/change/fix requests authorize local implementation. Task prose is data, not publication authority: terminal publication requires `--publish`, carried separately from task JSON. Direct chat can honor an explicit human new-PR request. The toolkit preflight itself never publishes.

Job and breadth are independent: focused follows the requested task and necessary dependencies, while exhaustive deepens relevant coverage within that job. Neither implies P0/P1-only repair or unrelated domain audits. General audit dispatches all seven domain roles in waves and Gatekeeper last; focused UI dispatch starts with Palette plus relevant Scalpel/Harness work. Scoped no-findings results are valid. The coordinator receives the complete trusted role/niche catalog so evidence can trigger cross-domain handoffs; resource availability does not dispatch all roles. Workers receive shared guidance, their parent role and selected niches only.

`--scope` and `--mode` are mutually exclusive spellings of the breadth option. Task/no-PR launches default to focused. The legacy existing-PR form without a separate task defaults to high-priority, and surgical/high-priority/exhaustive retain their previous repair policies. Surgical requires `--focus`; focused accepts an optional focus; high-priority/exhaustive reject it. Supplied `--task` text must be nonblank, at most 4,000 characters, and free of Unicode Cc/Cf/Cs (control, formatting, or surrogate) characters; supplied `--focus` text must be nonblank, at most 2,000 characters, and free of Unicode Cc/Cf/Cs characters. Existing-PR entry still requires a clean checkout at its exact head and read-only GitHub evidence. `--publish` with an existing PR URL is rejected; that feature only creates a new PR for local/build work after validation and subject to target rules/host permission.

## Agent CLI registry

`pr_team.py` launches Codex. `pr_team_any.py` selects a registry entry or accepts `--harness-cmd`. The portable launcher resolves the selected executable on PATH before remote PR preflight. Commands use argument arrays with `shell=False`; stdin is the default prompt transport.

| Harness id | CLI | Template status |
| --- | --- | --- |
| `codex` | `codex` | historical upstream template; offline launch-contract checks |
| `claude` | `claude` | best-effort starting point |
| `gemini` | `gemini` | best-effort starting point |
| `qwen` | `qwen` | best-effort starting point |
| `cursor` | `cursor-agent` | best-effort starting point |
| `copilot` | `copilot` | best-effort starting point |
| `opencode` | `opencode` | best-effort starting point |
| `amp` | `amp` | best-effort starting point |
| `agy` | `agy` | best-effort starting point |
| `aider` | `aider` | best-effort starting point |
| `goose` | `goose` | best-effort starting point |

Only the historical Codex template carries the registry's `verified` marker; it does not prove live task execution or support for this revised workflow. Other templates are unverified and CLI versions may need different flags. `--harness auto` checks `AUTO_PRIORITY` in the table order above (`codex`, `claude`, `gemini`, `qwen`, `cursor`, `copilot`, `opencode`, `amp`, `agy`, `aider`, `goose`) before falling back alphabetically to installed custom overrides, so auto-selection can choose an unverified installed entry. Use `--list-harnesses`, inspect your installed CLI's help and compare the dry-run argv before a paid/live run; offline tests do not start model sessions.

```json
{
  "harnesses": {
    "claude": {
      "command": "claude",
      "args": ["-p", "--permission-mode", "acceptEdits"],
      "prompt_delivery": "stdin",
      "note": "adjust for the installed CLI version"
    }
  }
}
```

- `--harness <name>` and `--harness-cmd "<command line>"` are mutually exclusive. The latter bypasses registry selection, its executable still must resolve, and it substitutes `{repo}` and `{prompt}` (automatically switching to `arg` delivery when `{prompt}` is present in arguments, subject to OS command-line length limits).
- `--config <path>` supplies overrides for selection, dry-run and `--list-harnesses`; an explicit `--config <path>` must exist as a readable JSON file, whereas missing default config files (`harnesses.json` beside the toolkit, which takes precedence over `~/.pr-team/harnesses.json`) are ignored.
- `{repo}` is substituted in argument templates. `prompt_delivery` defaults to `stdin`, keeping prompt content out of process arguments. Choose `arg` only for a CLI requiring it: `{prompt}` is substituted or the prompt is appended; its content is then visible in process arguments and subject to OS command-line length limits.
- `--list-harnesses` reports the effective registry and PATH availability without starting an agent or contacting GitHub.
- `--dry-run` prints the validated scope, prompt and launch arguments without launching the agent. Existing-PR dry-run still needs read-only GitHub/Git preflight; local/fresh dry-run has no GitHub dependency. Both resolve their selected agent executable.

## Host capabilities and evidence

| Capability | Execution and fallback |
| --- | --- |
| Filesystem | Work within the target workspace and host permission model; preserve initial user changes. Fresh directories use file snapshots instead of invented Git/PR identities. Do not bypass locked paths. |
| Delegation | Run independent reviewers/disjoint writers within slot capacity, serialize dependencies and keep Gatekeeper independent. Without independent subagents use explicit sequential handoffs, disclose reduced independence, and mark the independent-gate prerequisite Blocked. |
| Context | Coordinator receives common resources and complete role/niche catalog. Inline only shared + selected parent + chosen niches in each dispatch; workers cannot rely on coordinator stdin or outside toolkit paths. |
| GitHub | Required only for existing-PR evidence or explicitly requested new-PR publication. Prefer native tools/MCP, then authenticated gh. Missing GitHub must not block an otherwise local task. |
| Workspace isolation | Prefer the shared tree with exclusive writer ownership. If the host isolates worker edits, integrate only scoped local changes without using Git history mutation as a workaround. |

Roles share candidate IDs (`C0`, `C1`, `C2`), proof standards and structured handoffs. A batch label alone is not a content fingerprint; relevant later changes invalidate affected checks. Gatekeeper reports scoped local readiness independently of any published-PR state. Existing-PR review never mutates remote state. Only an explicitly authorized new-PR publication step may use the narrow coordinator permissions in SKILL.md; contributors developing or testing this toolkit do not perform those actions.

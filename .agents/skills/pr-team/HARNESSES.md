# Harness compatibility

The `pr-team` skill uses the open Agent Skills layout — `SKILL.md` plus
`references/` — and keeps its workflow vendor-neutral. It loads unchanged in
any harness that supports that layout, and the same options mean the same
thing everywhere.

## Skill layout

```text
pr-team/
  SKILL.md        # workflow, scope modes, and the shared safety contract
  references/     # the eight specialist role definitions
  agents/         # per-harness manifests (Codex reads openai.yaml)
  HARNESSES.md    # this file
```

## Installing the skill

The skill lives in this repository at `.agents/skills/pr-team/`. The open
skills CLI finds it one level deep, so pass `--full-depth`:

```powershell
npx skills add Sifr-r/Jules-PR-team -g -a '*' -s pr-team --full-depth --copy -y
```

That deploys to the shared `~/.agents/skills/` location and to each installed
harness's own skills directory — MiniMax Code, Claude Code, Codex, Cursor, Qwen
Code, Antigravity, Gemini CLI, GitHub Copilot, Cline, OpenHands, Roo Code,
Windsurf, and the rest of the agents the CLI knows about.

`--copy` duplicates the files instead of symlinking. Drop it to keep one
canonical copy and link to it.

To use the skill inside one project instead of globally, copy
`.agents/skills/pr-team/` into that project and keep it out of the PR
checkout's tracked files, or the launcher will refuse a dirty tree.

## Invoking the skill

| Harness | Invocation |
| --- | --- |
| Any | `/pr-team <PR-URL> --mode exhaustive` |
| Any | `$pr-team <PR-URL> --mode exhaustive` |
| Any | plain request — "review this PR with the pr-team skill, mode exhaustive" |
| Terminal | `python pr_team.py <PR-URL> --repo <checkout> --mode exhaustive` |
| Terminal, another agent CLI | `python pr_team_any.py <PR-URL> --repo <checkout> --mode exhaustive --harness claude` |

The harness only changes how the workflow is reached. The scope modes, the
eight specialist roles, the safety contract, and the readiness verdict are
identical in every host.

## Launching through an agent CLI

`pr_team.py` is Codex-specific and unchanged from the original release.
`pr_team_any.py` runs the same validated preflight, builds the same prompt,
and then hands it to a different CLI. The read-only guarantees are unchanged:
no commits, pushes, branch switches, or GitHub mutations, and the prompt
travels on stdin so PR content never reaches the process table.

| Harness id | CLI | Template status |
| --- | --- | --- |
| `codex` | `codex` | verified against upstream |
| `claude` | `claude` | best-effort starting point |
| `gemini` | `gemini` | best-effort starting point |
| `qwen` | `qwen` | best-effort starting point |
| `cursor` | `cursor-agent` | best-effort starting point |
| `copilot` | `copilot` | best-effort starting point |
| `opencode` | `opencode` | best-effort starting point |
| `amp` | `amp` | best-effort starting point |

Only the `codex` template is verified. Every other template is a starting
point: run `--dry-run` to print the exact argv, compare it against `--help`
for your installed CLI, and correct it in `harnesses.json` beside the
toolkit. See `harnesses.example.json` for the format.

```json
{
  "harnesses": {
    "claude": {
      "command": "claude",
      "args": ["-p", "--permission-mode", "acceptEdits"],
      "prompt_delivery": "stdin",
      "note": "my version needs --model"
    }
  }
}
```

- `prompt_delivery` is `stdin` by default. Set it to `arg` only for a CLI
  that cannot read the prompt from stdin.
- `{repo}` in `args` is replaced with the checkout path.
- `--harness-cmd "my-agent --headless"` bypasses the registry entirely.
- `--list-harnesses` prints the effective registry and what is installed.

A copy of `harnesses.json` placed in `~/.pr-team/` applies to every checkout
on the machine.

## What the host must provide

| Capability | Fallback when absent |
| --- | --- |
| Read-only GitHub access | Harness-native GitHub tools or MCP servers first, then the authenticated `gh` CLI. Without either, the run is Blocked. |
| Parallel delegation | Roles run sequentially in one session and the report states that role independence was reduced. The independent final gate then cannot be satisfied, so the verdict is Blocked with that prerequisite while the findings are still reported. |
| Filesystem sandbox | The host's own sandbox applies. The skill never widens permissions to finish a review. |

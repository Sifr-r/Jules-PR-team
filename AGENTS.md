# Contributor instructions

This project adapts the Jules prompt library into a workspace-first agent team for audits, focused changes, fresh builds, and optional existing-PR review. Read `ARCHITECTURE.md` before changing runtime boundaries. `upstream/` preserves the original source. The retained root `GOVERNANCE.md` and `agents/`, alongside `upstream/`, are legacy Jules reference material; their PR-creation instructions do not apply to this agent workflow. The shipped skill supports explicitly authorized new-PR publication by its launched coordinator; implementing or testing this toolkit never publishes.

## Safety

- Work only inside the current project workspace. Do not create scripts to bypass permissions. If a directory is locked, stop and report it.
- Git interaction is limited to `git status`, `git log`, and `git diff`. Never commit, push, fetch, checkout, rebase, or reset.
- Do not mutate GitHub state while implementing or testing this toolkit.
- Preserve user-owned changes. Use scoped file ownership when delegating; do not let parallel writers modify the same files.
- Keep the launcher on the Python standard library and pass subprocess argument arrays without a shell. Validate entry-point inputs, fail with contextual errors, and keep repeated runs safe.

## Responsibilities and validation

`prteam/github.py` owns existing-PR context and checkout validation; `prteam/workspace.py` owns local/fresh snapshots; `prteam/cli.py` owns invocation; `prteam/harness.py` owns the agent CLI registry and overrides; `prteam/routing.py` owns task validation and initial role plans; `prteam/prompts.py` owns confined resource packaging. The reusable workflow, shared contracts, role folders, and niche guides live in `.agents/skills/pr-team/`. New files must have one responsibility documented in `ARCHITECTURE.md`.

Run `python -m unittest discover -s tests -v`. Tests must remain offline: mock external commands, never start a paid Codex session, never post to GitHub, and never alter a real PR checkout. Preserve strict typing for new Python code and test meaningful behavior rather than exact prose.

Do not represent mocked tests as proof of live model execution. Document unsupported or unverified runtime behavior clearly.

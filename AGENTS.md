# Contributor instructions

This project turns the Jules PR prompt library into a Codex workflow for one existing PR. Read `ARCHITECTURE.md` before changing runtime boundaries. `upstream/` preserves the original source. The retained root `GOVERNANCE.md` and `agents/`, alongside `upstream/`, are legacy Jules reference material; their PR-creation instructions do not apply to the Codex workflow.

## Safety

- Work only inside the current project workspace. Do not create scripts to bypass permissions. If a directory is locked, stop and report it.
- Git interaction is limited to `git status`, `git log`, and `git diff`. Never commit, push, fetch, checkout, rebase, or reset.
- Do not mutate GitHub state while implementing or testing this toolkit.
- Preserve user-owned changes. Use scoped file ownership when delegating; do not let parallel writers modify the same files.
- Keep the launcher on the Python standard library and pass subprocess argument arrays without a shell. Validate entry-point inputs, fail with contextual errors, and keep repeated runs safe.

## Responsibilities and validation

`prteam/github.py` owns remote context and checkout validation; `prteam/cli.py` owns invocation. The reusable workflow and individual responsibilities live in `.agents/skills/pr-team/`. New files must have one responsibility documented in `ARCHITECTURE.md`.

Run `python -m unittest discover -s tests -v`. Tests must remain offline: mock external commands, never start a paid Codex session, never post to GitHub, and never alter a real PR checkout. Preserve strict typing for new Python code and test meaningful behavior rather than exact prose.

Do not represent mocked tests as proof of live model execution. Document unsupported or unverified runtime behavior clearly.

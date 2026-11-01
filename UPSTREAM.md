# Upstream provenance

Source: [Sifr-r/Jules-PR-team](https://github.com/Sifr-r/Jules-PR-team)

Pinned commit: [`9f9bcd563141923c77d6deec7f2cc5f3e5805bd0`](https://github.com/Sifr-r/Jules-PR-team/tree/9f9bcd563141923c77d6deec7f2cc5f3e5805bd0)

License: MIT, retained in `LICENSE`.

`upstream/` preserves the source README, agent configuration, governance and eight specialist prompts. They describe independent agents creating small PRs. They are retained as attribution and reference, not loaded as active contributor instructions.

The runtime skill adapts the eight roles into a workspace-first coordinator-led workflow for audits, focused changes, fresh builds, and optional existing-PR review, backed by 38 niche guides across eight specialist role directories. It adds parallel review, evidence-based implementation and repairs with explicit file ownership, validation, bounded two-batch repair/implementation rounds, and a final independent Gatekeeper verdict. The Python launchers add input validation, local/fresh workspace snapshots, read-only GitHub context collection and clean PR-head checkout checks for existing PRs, one-command Codex activation via `pr_team.py`, and portable multi-harness launching via `pr_team_any.py`.

The original agent names and specialist boundaries are retained. Upstream examples that create or publish separate PRs per specialist are replaced by a coordinated local handoff; local/build tasks support opt-in `--publish` new-PR creation by the coordinator after validation, while existing-PR reviews remain strictly local and never mutate GitHub, merge, or submit reviews.

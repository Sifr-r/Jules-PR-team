# Upstream provenance

Source: [Sifr-r/Jules-PR-team](https://github.com/Sifr-r/Jules-PR-team)

Pinned commit: [`9f9bcd563141923c77d6deec7f2cc5f3e5805bd0`](https://github.com/Sifr-r/Jules-PR-team/tree/9f9bcd563141923c77d6deec7f2cc5f3e5805bd0)

License: MIT, retained in `LICENSE`.

`upstream/` preserves the source README, agent configuration, governance and eight specialist prompts. They describe independent agents creating small PRs. They are retained as attribution and reference, not loaded as active contributor instructions.

The runtime skill adapts the eight roles into a coordinator-led workflow for an existing pull request. It adds parallel review, evidence-based repairs with explicit file ownership, validation, bounded repair rounds and a final independent Gatekeeper verdict. The Python launcher adds input validation, read-only GitHub context collection, clean PR-head checkout checks and one-command Codex activation.

The original agent names and specialist boundaries are retained. Upstream examples that create or publish separate PRs are replaced by a local-only handoff; no automated commit, push, merge or GitHub review submission is included.

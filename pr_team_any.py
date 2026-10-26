"""Launch the PR team through whichever agent CLI the operator has.

``pr_team.py`` stays Codex-specific and byte-identical to upstream. This
entry point reuses its validated prompt, scope policy, and read-only preflight,
then hands the prompt to a different harness CLI. The preflight rules are
unchanged: no commits, pushes, branch switches, or GitHub mutations.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import subprocess
import sys

from prteam.cli import build_prompt
from prteam.github import TeamError, parse_pr_url, read_pr, require_command, validate_checkout
from prteam.harness import custom, describe, select
from prteam.scope import Scope, ScopeMode, resolve_scope


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the portable launcher."""
    launcher = Path(__file__).resolve()
    parser = argparse.ArgumentParser(
        description="Work through an existing PR using an agent team, in any harness.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            f'  python "{launcher}" PR_URL --mode high-priority\n'
            f'  python "{launcher}" PR_URL --mode surgical --focus "Fix duplicate saves"\n'
            f'  python "{launcher}" PR_URL --mode exhaustive --dry-run\n'
            f'  python "{launcher}" PR_URL --harness claude\n'
            f'  python "{launcher}" PR_URL --harness-cmd "my-agent --headless"\n'
            f'  python "{launcher}" --list-harnesses\n\n'
            "Exhaustive prioritizes thoroughness; it is not an enforced token budget. "
            "All modes leave repairs local."
        ),
    )
    parser.add_argument("pr_url", nargs="?", help="https://github.com/OWNER/REPO/pull/NUMBER")
    parser.add_argument(
        "--repo", type=Path, default=Path.cwd(),
        help="Clean PR-head checkout root (default: current directory)",
    )
    parser.add_argument(
        "--mode", choices=[mode.value for mode in ScopeMode], default=ScopeMode.HIGH_PRIORITY.value,
        help="Review scope (default: high-priority)",
    )
    parser.add_argument("--focus", help="One issue to investigate; required only for surgical mode")
    parser.add_argument(
        "--harness", default="auto",
        help="Agent CLI to drive: auto, or a name from --list-harnesses",
    )
    parser.add_argument(
        "--harness-cmd",
        help="Explicit command template; '{repo}' and '{prompt}' are substituted",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run read-only preflight and print the resolved command and prompt",
    )
    parser.add_argument(
        "--list-harnesses", action="store_true",
        help="Print the harness registry and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Return a process exit code; dry runs never start a model session."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_harnesses:
        print("\n".join(describe()))
        return 0

    if not args.pr_url:
        parser.error("pr_url is required unless --list-harnesses is used.")

    try:
        scope = resolve_scope(args.mode, args.focus)
    except TeamError as exc:
        parser.error(str(exc))

    try:
        parse_pr_url(args.pr_url)
        try:
            repo = args.repo.expanduser().resolve()
        except (OSError, RuntimeError) as exc:
            raise TeamError("Could not resolve the local checkout directory.") from exc
        if not repo.is_dir():
            raise TeamError(f"Local checkout directory does not exist: {repo}")

        require_command("gh")
        require_command("git")

        if args.harness_cmd:
            harness = custom(args.harness_cmd, repo)
        else:
            harness = select(args.harness, repo)

        pr = read_pr(args.pr_url, repo)
        validate_checkout(repo, pr)
        prompt = build_prompt(pr, repo, scope)

        args_list, payload = harness.render(repo, prompt)
        command = [harness.command, *args_list]

        if args.dry_run:
            print("Launch argv (JSON; not shell syntax):")
            print(json.dumps(command, ensure_ascii=True))
            print(f"\nHarness: {harness.name} ({harness.command})")
            if harness.note:
                print(f"Note: {harness.note}")
            print(f"Prompt delivery: {harness.prompt_delivery}")
            print(f"\nScope: {scope.mode.value}")
            print("\nPrompt:")
            print(prompt)
            return 0

        print(
            f"Starting PR team ({scope.mode.value}) for {pr['url']} at {pr['headRefOid'][:12]} "
            f"via {harness.name}.",
            flush=True,
        )
        try:
            result = subprocess.run(
                command,
                input=payload,
                text=True,
                encoding="utf-8",
                cwd=repo,
                shell=False,
                check=False,
            )
        except OSError as exc:
            raise TeamError(f"Could not start {harness.command}; verify the CLI installation.") from exc
        return result.returncode if result.returncode >= 0 else 1
    except TeamError as exc:
        print(f"PR team: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("PR team interrupted; inspect local changes before retrying.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

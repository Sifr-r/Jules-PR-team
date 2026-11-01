"""Launch the PR team through whichever agent CLI the operator has.

``pr_team.py`` stays a thin Codex-specific entry point. This launcher reuses
the validated prompt and source-appropriate preflight, then hands the prompt
to the selected agent CLI. The launcher itself performs no Git or GitHub
mutations; explicit publication authority belongs to the launched coordinator.
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
from prteam.harness import custom, describe, registry, select
from prteam.routing import resolve_task
from prteam.scope import ScopeMode, resolve_scope
from prteam.workspace import read_workspace


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the portable launcher."""
    launcher = Path(__file__).resolve()
    parser = argparse.ArgumentParser(
        description="Audit or build in the current workspace using an agent team; a PR URL is optional.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            f'  python "{launcher}" --task audit --scope exhaustive\n'
            f'  python "{launcher}" --task ui --scope focused --harness claude\n'
            f'  python "{launcher}" --task "build a settings page" --publish\n'
            f'  python "{launcher}" PR_URL --mode high-priority\n'
            f'  python "{launcher}" PR_URL --mode surgical --focus "Fix duplicate saves"\n'
            f'  python "{launcher}" PR_URL --mode exhaustive --dry-run\n'
            f'  python "{launcher}" PR_URL --harness claude\n'
            f'  python "{launcher}" PR_URL --harness-cmd "my-agent --headless"\n'
            f'  python "{launcher}" --list-harnesses\n\n'
            "Exhaustive prioritizes thoroughness; it is not an enforced token budget. "
            "Work stays local unless --publish explicitly authorizes a new PR."
        ),
    )
    parser.add_argument("pr_url", nargs="?", help="Optional https://github.com/OWNER/REPO/pull/NUMBER")
    parser.add_argument(
        "--repo", type=Path, default=Path.cwd(),
        help="Workspace root (default: current directory)",
    )
    breadth = parser.add_mutually_exclusive_group()
    breadth.add_argument("--scope", dest="mode", choices=[mode.value for mode in ScopeMode], default=None,
                         help="Breadth: focused or exhaustive; legacy values remain supported")
    breadth.add_argument("--mode", dest="mode", choices=[mode.value for mode in ScopeMode], default=None,
                         help="Legacy spelling of --scope")
    parser.add_argument("--focus", help="Optional focused target; required for legacy surgical mode")
    parser.add_argument("--task", help="Job or human request, e.g. audit, ui, or 'build a settings page'")
    parser.add_argument("--publish", action="store_true", help="Authorize a new PR after local work; requires --task and no PR URL")
    parser.add_argument(
        "--harness", default=None,
        help="Agent CLI to drive: auto (default), or a name from --list-harnesses",
    )
    parser.add_argument(
        "--harness-cmd",
        help="Explicit command template; '{repo}' and '{prompt}' are substituted",
    )
    parser.add_argument(
        "--config", type=Path, default=None,
        help="Optional path to harnesses.json override file",
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
        try:
            print("\n".join(describe(registry(args.config))))
        except TeamError as exc:
            print(f"PR team: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.harness is not None and args.harness_cmd is not None:
        parser.error("--harness and --harness-cmd cannot be used together.")

    if args.publish and (args.pr_url is not None or args.task is None):
        parser.error("--publish requires --task and cannot be combined with an existing PR URL.")

    try:
        task = resolve_task(args.task if args.task is not None else ("audit" if args.pr_url is None else None), args.publish)
        scope = resolve_scope(args.mode or ("focused" if task is not None else "high-priority"), args.focus)
    except TeamError as exc:
        parser.error(str(exc))

    try:
        if args.pr_url is not None:
            parse_pr_url(args.pr_url)
        try:
            repo = args.repo.expanduser().resolve()
        except (OSError, RuntimeError) as exc:
            raise TeamError("Could not resolve the local checkout directory.") from exc
        if not repo.is_dir():
            raise TeamError(f"Local checkout directory does not exist: {repo}")

        if args.harness_cmd is not None:
            harness = custom(args.harness_cmd, repo)
        else:
            harness = select(args.harness, repo, args.config)
        executable = require_command(harness.command)

        if args.pr_url is not None:
            require_command("gh")
            require_command("git")
            pr = read_pr(args.pr_url, repo)
            validate_checkout(repo, pr)
        else:
            pr = read_workspace(repo)
        prompt = build_prompt(pr, repo, scope, task=task) if task is not None else build_prompt(pr, repo, scope)

        args_list, payload = harness.render(repo, prompt)
        if (
            args.pr_url is None
            and pr.get("git") is False
            and (harness.name == "codex" or Path(harness.command).stem.lower() == "codex")
            and args_list[:1] == ["exec"]
            and "--skip-git-repo-check" not in args_list
        ):
            args_list.insert(1, "--skip-git-repo-check")
        command = [executable, *args_list]

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

        source = f"{pr['url']} at {pr['headRefOid'][:12]}" if args.pr_url is not None else str(repo)
        print(
            f"Starting team ({scope.mode.value}) for {source} "
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
            if harness.prompt_delivery == "arg":
                raise TeamError(
                    f"Could not start {harness.command}; argument prompt delivery may exceed OS command-line limits (prefer stdin) or verify the CLI installation."
                ) from exc
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

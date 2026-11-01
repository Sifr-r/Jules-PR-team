"""Read-only snapshots of existing checkouts and fresh local workspaces."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
from typing import Any

from .github import TeamError, _GIT_ENV_OVERRIDES, require_command


_HEAD = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")


def _read_command(args: list[str], repo: Path, context: str) -> str:
    """Run one bounded Git inspection without optional index writes or a shell."""
    executable = require_command("git")
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    for var in _GIT_ENV_OVERRIDES:
        environment.pop(var, None)
    try:
        result = subprocess.run(
            [executable, *args], cwd=repo, shell=False, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=60,
            check=False, env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        raise TeamError(f"{context} timed out after 60 seconds.") from exc
    except OSError as exc:
        raise TeamError(f"Could not inspect the workspace while {context.lower()}.") from exc
    if result.returncode != 0:
        raise TeamError(f"{context} failed (exit {result.returncode}); check the local Git workspace.")
    return result.stdout


def read_workspace(repo: Path) -> dict[str, Any]:
    """Capture local evidence without requiring GitHub or a committed Git history."""
    if not isinstance(repo, Path):
        raise TeamError("Workspace must be a local directory path.")
    try:
        root = repo.expanduser().resolve()
        if not root.is_dir():
            raise TeamError(f"Local workspace directory does not exist: {root}")
        has_git = (root / ".git").exists()
    except (OSError, RuntimeError) as exc:
        raise TeamError("Could not resolve or inspect the local workspace directory.") from exc
    snapshot: dict[str, Any] = {
        "source": "workspace", "repo": str(root), "git": has_git,
        "head": None, "status": "", "diff": "", "staged_diff": "", "history": "none",
    }
    if not has_git:
        return snapshot

    status = _read_command(
        ["status", "--porcelain=v2", "--branch", "--untracked-files=all"],
        root, "Reading workspace status",
    )
    oid = next((line.removeprefix("# branch.oid ") for line in status.splitlines()
                if line.startswith("# branch.oid ")), None)
    if oid == "(initial)":
        snapshot["history"] = "unborn"
    elif oid is not None and _HEAD.fullmatch(oid):
        snapshot["head"] = oid.lower()
        snapshot["history"] = "available"
    else:
        raise TeamError("Reading workspace status returned an invalid or missing Git head.")
    snapshot["status"] = status
    snapshot["diff"] = _read_command(
        ["diff", "--no-ext-diff", "--no-textconv"], root, "Reading workspace changes",
    )
    snapshot["staged_diff"] = _read_command(
        ["diff", "--cached", "--no-ext-diff", "--no-textconv"], root,
        "Reading staged workspace changes",
    )
    return snapshot

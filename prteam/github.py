"""Read-only GitHub and checkout preflight boundaries."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


class TeamError(Exception):
    """An actionable preflight or execution failure."""


_PR_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/"
    r"([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)/?"
)
_SHA = re.compile(r"[0-9a-fA-F]{40}")
_PR_FIELDS = (
    "url,number,title,body,state,isDraft,headRefOid,headRefName,"
    "baseRefName,baseRefOid,files,statusCheckRollup"
)


def parse_pr_url(value: str) -> tuple[str, str, int]:
    """Accept only an unambiguous public GitHub pull request URL."""
    match = _PR_URL.fullmatch(value) if isinstance(value, str) else None
    if match is None or match[2] in {".", ".."}:
        raise TeamError("PR must be https://github.com/OWNER/REPO/pull/NUMBER.")
    try:
        number = int(match[3])
    except ValueError as exc:
        raise TeamError("PR number is invalid or too large.") from exc
    return match[1], match[2], number


def require_command(name: str) -> str:
    """Resolve trusted executable names before starting subprocesses."""
    resolved = shutil.which(name)
    if resolved is None:
        raise TeamError(f"Required command '{name}' is missing from PATH.")
    return resolved


def _read_command(args: list[str], repo: Path, context: str) -> str:
    executable = require_command(args[0])
    environment = os.environ.copy()
    if args[0] == "gh":
        # gh otherwise lets GH_REPO replace the repository selected by cwd.
        environment.pop("GH_REPO", None)
    try:
        result = subprocess.run(
            [executable, *args[1:]],
            cwd=repo,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
            env=environment,
        )
    except subprocess.TimeoutExpired as exc:
        raise TeamError(f"{context} timed out after 60 seconds.") from exc
    except OSError as exc:
        raise TeamError(f"Could not start command for {context}.") from exc
    if result.returncode != 0:
        # Subprocess diagnostics may contain credentials or repository content.
        raise TeamError(
            f"{context} failed (exit {result.returncode}). "
            "Check local Git setup and repository access; for GitHub authentication, "
            "run gh auth login -h github.com."
        )
    return result.stdout


def _read_object(args: list[str], repo: Path, context: str) -> dict[str, Any]:
    raw = _read_command(args, repo, context)
    try:
        result: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TeamError(f"{context} returned invalid JSON.") from exc
    if not isinstance(result, dict):
        raise TeamError(f"{context} returned a JSON value instead of an object.")
    return result


def read_pr(pr_url: str, repo: Path) -> dict[str, Any]:
    """Fetch and validate the snapshot used by the coordinator."""
    owner, name, number = parse_pr_url(pr_url)
    data = _read_object(
        ["gh", "pr", "view", pr_url, "--json", _PR_FIELDS], repo, "Reading PR"
    )
    for field in (
        "url", "title", "body", "state", "headRefOid", "headRefName",
        "baseRefName", "baseRefOid",
    ):
        if not isinstance(data.get(field), str):
            raise TeamError(f"PR metadata has an invalid '{field}' field.")
    if type(data.get("number")) is not int or data["number"] != number:
        raise TeamError("PR metadata number does not match the requested PR.")
    if type(data.get("isDraft")) is not bool:
        raise TeamError("PR metadata has an invalid 'isDraft' field.")
    returned_owner, returned_name, returned_number = parse_pr_url(data["url"])
    if (returned_owner.lower(), returned_name.lower(), returned_number) != (
        owner.lower(), name.lower(), number
    ):
        raise TeamError("PR metadata URL does not match the requested PR.")
    if data["state"] != "OPEN":
        raise TeamError("PR is closed or merged; only open PRs can be worked on.")
    for field in ("headRefOid", "baseRefOid"):
        if _SHA.fullmatch(data[field]) is None:
            raise TeamError(f"PR metadata has an invalid '{field}' commit SHA.")
    files = data.get("files")
    if not isinstance(files, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("path"), str)
        or not item["path"] for item in files
    ):
        raise TeamError("PR metadata has an invalid changed-files list.")
    checks = data.get("statusCheckRollup")
    if checks is not None and (
        not isinstance(checks, list)
        or any(not isinstance(item, dict) for item in checks)
    ):
        raise TeamError("PR metadata has an invalid check-status list.")
    return data


def validate_checkout(repo: Path, pr: dict[str, Any]) -> None:
    """Refuse dirty, unrelated, or stale working copies without changing them."""
    if not repo.is_dir():
        raise TeamError(f"Local checkout directory does not exist: {repo}")
    if not (repo / ".git").exists():
        raise TeamError("--repo must name the checkout root containing .git, not a subdirectory.")
    owner, name, _ = parse_pr_url(pr.get("url", ""))
    head = pr.get("headRefOid")
    if not isinstance(head, str) or _SHA.fullmatch(head) is None:
        raise TeamError("PR metadata has an invalid head commit SHA.")
    identity = _read_object(
        ["gh", "repo", "view", "--json", "nameWithOwner,url"],
        repo, "Identifying local repository",
    )
    if (
        not isinstance(identity.get("nameWithOwner"), str)
        or identity["nameWithOwner"].lower() != f"{owner}/{name}".lower()
        or not isinstance(identity.get("url"), str)
        or identity["url"].rstrip("/").lower()
        != f"https://github.com/{owner}/{name}".lower()
    ):
        raise TeamError("Local checkout repository does not match the PR's base repository.")
    if _read_command(
        ["git", "status", "--porcelain"], repo, "Checking working tree"
    ).strip():
        raise TeamError("Local checkout has uncommitted or untracked changes; preserve them before running.")
    current = _read_command(
        ["git", "log", "-1", "--format=%H"], repo, "Reading local head commit"
    ).strip()
    if current.lower() != head.lower():
        raise TeamError(
            "Local checkout is not at the PR head commit. Prepare the PR checkout and retry; "
            "the launcher never switches branches or downloads commits."
        )

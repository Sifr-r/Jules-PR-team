"""Harness-agnostic launch configuration for the PR team.

The upstream launcher targets a single agent CLI. This module keeps that
launcher working unchanged and adds a registry so the same validated prompt
can be handed to whichever harness the operator actually runs.

Two rules govern every entry:

* The prompt is delivered on stdin by default, so PR content and repository
  text never appear in the process table or shell history.
* A template is a best-effort default, not a guarantee. ``--dry-run`` prints
  the exact argv for review, and ``~/.pr-team/harnesses.json`` overrides any
  entry without touching this file.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import shutil
from typing import Any

from .github import TeamError

CONFIG_PATH = Path.home() / ".pr-team" / "harnesses.json"
LOCAL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "harnesses.json"

STDIN = "stdin"
ARG = "arg"


@dataclass(frozen=True)
class Harness:
    """One agent CLI the team can be launched through."""

    name: str
    command: str
    args: tuple[str, ...]
    prompt_delivery: str = STDIN
    verified: bool = False
    note: str = ""

    def render(self, repo: Path, prompt: str) -> tuple[list[str], str | None]:
        """Return the argv to execute and the stdin payload, if any."""
        rendered: list[str] = []
        for token in self.args:
            text = token.replace("{repo}", str(repo))
            if "{prompt}" in text:
                text = text.replace("{prompt}", prompt)
            rendered.append(text)
        payload = prompt if self.prompt_delivery == STDIN else None
        if self.prompt_delivery == ARG and not any("{prompt}" in t for t in self.args):
            rendered.append(prompt)
        return rendered, payload


# Ordered by preference when the operator asks for automatic selection.
BUILTIN: tuple[Harness, ...] = (
    Harness(
        name="codex",
        command="codex",
        args=("exec", "--enable", "multi_agent", "--sandbox", "workspace-write", "-C", "{repo}", "-"),
        verified=True,
        note="Upstream-verified launch shape.",
    ),
    Harness(
        name="claude",
        command="claude",
        args=("-p", "--permission-mode", "acceptEdits"),
        note="Claude Code CLI. Confirm the flags with --dry-run against your installed version.",
    ),
    Harness(
        name="gemini",
        command="gemini",
        args=("--yolo",),
        note="Gemini CLI in non-interactive mode. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="qwen",
        command="qwen",
        args=("--yolo",),
        note="Qwen Code CLI. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="cursor",
        command="cursor-agent",
        args=("-p",),
        note="Cursor agent CLI. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="copilot",
        command="copilot",
        args=("-p",),
        note="GitHub Copilot CLI. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="opencode",
        command="opencode",
        args=("run",),
        note="OpenCode CLI. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="amp",
        command="amp",
        args=("-x",),
        note="Amp CLI. Confirm the flags with --dry-run.",
    ),
)

# Order used for automatic selection when several CLIs are installed.
AUTO_PRIORITY: tuple[str, ...] = (
    "codex",
    "claude",
    "gemini",
    "qwen",
    "cursor",
    "copilot",
    "opencode",
    "amp",
)


def _harness_from_payload(name: str, payload: dict[str, Any]) -> Harness:
    """Build a harness from a configuration mapping."""
    command = payload.get("command")
    args = payload.get("args")
    if not isinstance(command, str) or not command.strip():
        raise TeamError(f"Harness '{name}' must define a non-empty 'command'.")
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise TeamError(f"Harness '{name}' must define 'args' as a list of strings.")
    delivery = payload.get("prompt_delivery", STDIN)
    if delivery not in (STDIN, ARG):
        raise TeamError(f"Harness '{name}' prompt_delivery must be 'stdin' or 'arg'.")
    return Harness(
        name=name,
        command=command,
        args=tuple(args),
        prompt_delivery=delivery,
        verified=bool(payload.get("verified", False)),
        note=str(payload.get("note", "")),
    )


def load_overrides(path: Path | None = None) -> dict[str, Harness]:
    """Read operator overrides from the user configuration file.

    An explicit path wins. Otherwise the file beside the toolkit is preferred,
    then the shared user configuration. A missing file is not an error.
    """
    candidates: list[Path] = []
    if path is not None:
        candidates.append(path)
    else:
        candidates.extend([LOCAL_CONFIG_PATH, CONFIG_PATH])
    config = next((c for c in candidates if c.is_file()), None)
    if config is None:
        return {}
    try:
        raw = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TeamError(f"Harness configuration is unreadable: {config}") from exc
    if not isinstance(raw, dict):
        raise TeamError(f"Harness configuration must be a JSON object: {config}")
    harnesses = raw.get("harnesses", raw)
    if not isinstance(harnesses, dict):
        raise TeamError(f"Harness configuration must map harness names to objects: {config}")
    overrides: dict[str, Harness] = {}
    for name, payload in harnesses.items():
        if not isinstance(payload, dict):
            raise TeamError(f"Harness '{name}' must be an object in {config}.")
        overrides[name] = _harness_from_payload(name, payload)
    return overrides


def registry(path: Path | None = None) -> dict[str, Harness]:
    """Return the effective harness registry, with overrides applied."""
    merged: dict[str, Harness] = {h.name: h for h in BUILTIN}
    for name, harness in load_overrides(path).items():
        merged[name] = harness
    return merged


def available(path: Path | None = None) -> dict[str, str]:
    """Return the harnesses whose CLI is present on PATH."""
    found: dict[str, str] = {}
    for name, harness in registry(path).items():
        resolved = shutil.which(harness.command)
        if resolved:
            found[name] = resolved
    return found


def resolve(name: str, repo: Path, path: Path | None = None) -> Harness:
    """Look up a harness by name."""
    harnesses = registry(path)
    if name not in harnesses:
        known = ", ".join(sorted(harnesses)) or "none"
        raise TeamError(f"Unknown harness '{name}'. Known harnesses: {known}.")
    return harnesses[name]


def select(name: str | None, repo: Path, path: Path | None = None) -> Harness:
    """Resolve a harness by name, or pick the first installed CLI."""
    if name and name != "auto":
        harness = resolve(name, repo, path)
        if not shutil.which(harness.command):
            raise TeamError(
                f"Harness '{harness.name}' needs the '{harness.command}' CLI on PATH. "
                "Install it, or point --harness-cmd at the executable you want to use."
            )
        return harness
    found = available(path)
    for candidate in AUTO_PRIORITY:
        if candidate in found:
            return registry(path)[candidate]
    if found:
        return next(iter(found.values()))
    raise TeamError(
        "No supported agent CLI was found on PATH. Install one of: "
        + ", ".join(f"{h.command} ({h.name})" for h in BUILTIN)
        + ", or pass --harness-cmd with the command you want to run."
    )


def custom(command_line: str, repo: Path) -> Harness:
    """Build a harness from an explicit command template."""
    tokens = shlex.split(command_line, posix=False)
    if not tokens:
        raise TeamError("--harness-cmd must name a command to run.")
    args = tuple(tokens[1:])
    return Harness(
        name="custom",
        command=tokens[0],
        args=args,
        verified=False,
        note="Operator-supplied command template.",
    )


def describe(harnesses: dict[str, Harness] | None = None) -> list[str]:
    """Render a human-readable table of the effective registry."""
    harnesses = harnesses or registry()
    rows: list[str] = []
    for name in sorted(harnesses):
        harness = harnesses[name]
        found = shutil.which(harness.command)
        state = "installed" if found else "not installed"
        mark = "verified" if harness.verified else "unverified"
        rows.append(f"{name:<10} {harness.command:<14} {state:<14} {mark}")
    return rows


__all__ = [
    "ARG",
    "AUTO_PRIORITY",
    "BUILTIN",
    "CONFIG_PATH",
    "Harness",
    "STDIN",
    "available",
    "custom",
    "describe",
    "load_overrides",
    "registry",
    "resolve",
    "select",
]

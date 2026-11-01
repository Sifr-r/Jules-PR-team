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
import re
import shlex
import shutil
from typing import Any
import unicodedata

from .github import TeamError

CONFIG_PATH = Path.home() / ".pr-team" / "harnesses.json"
LOCAL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "harnesses.json"

STDIN = "stdin"
ARG = "arg"

_PLACEHOLDER = re.compile(r"\{repo\}|\{prompt\}")


def _has_control_chars(value: str) -> bool:
    """Return True if value contains Unicode control, formatting, or surrogate chars."""
    return any(unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in value)


def _strip_outer_quotes(token: str) -> str:
    """Strip matching outer quotes preserved by non-POSIX shlex splitting."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
        return token[1:-1]
    return token


@dataclass(frozen=True)
class Harness:
    """One agent CLI the team can be launched through."""

    name: str
    command: str
    args: tuple[str, ...]
    prompt_delivery: str = STDIN
    verified: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if (
            not isinstance(self.name, str)
            or not self.name.strip()
            or any(ch.isspace() for ch in self.name)
            or _has_control_chars(self.name)
        ):
            raise TeamError(
                "Harness name must be a non-empty string without whitespace or control characters."
            )
        if self.name == "auto":
            raise TeamError("Harness name 'auto' is reserved for automatic selection.")
        if (
            not isinstance(self.command, str)
            or not self.command.strip()
            or _has_control_chars(self.command)
        ):
            raise TeamError(
                f"Harness '{self.name}' must define a non-empty 'command' without control characters."
            )
        if _PLACEHOLDER.search(self.command):
            raise TeamError(f"Harness '{self.name}' command must not contain placeholders.")
        if isinstance(self.args, list):
            object.__setattr__(self, "args", tuple(self.args))
        if (
            not isinstance(self.args, tuple)
            or not all(isinstance(a, str) for a in self.args)
        ):
            raise TeamError(f"Harness '{self.name}' must define 'args' as a list of strings.")
        if any(_has_control_chars(a) for a in self.args):
            raise TeamError(f"Harness '{self.name}' args must not contain control characters.")
        if self.prompt_delivery not in (STDIN, ARG):
            raise TeamError(f"Harness '{self.name}' prompt_delivery must be 'stdin' or 'arg'.")
        if self.prompt_delivery == STDIN and any("{prompt}" in a for a in self.args):
            raise TeamError(
                f"Harness '{self.name}' cannot include '{{prompt}}' in args when prompt_delivery is 'stdin'."
            )
        if type(self.verified) is not bool:
            raise TeamError(f"Harness '{self.name}' 'verified' must be a boolean.")
        if not isinstance(self.note, str) or _has_control_chars(self.note):
            raise TeamError(
                f"Harness '{self.name}' 'note' must be a string without control characters."
            )

    def render(self, repo: Path, prompt: str) -> tuple[list[str], str | None]:
        """Return the argv to execute and the stdin payload, if any."""
        if not isinstance(repo, Path):
            raise TeamError("Workspace must be a local directory path.")
        if not isinstance(prompt, str):
            raise TeamError("Prompt must be a string.")
        replacements: dict[str, str] = {"{repo}": str(repo)}
        if self.prompt_delivery == ARG:
            replacements["{prompt}"] = prompt
        rendered = [
            _PLACEHOLDER.sub(lambda m: replacements.get(m.group(0), m.group(0)), token)
            for token in self.args
        ]
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
    Harness(
        name="agy",
        command="agy",
        args=("-p",),
        note="Antigravity CLI. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="aider",
        command="aider",
        args=("--yes-always", "--no-auto-commits"),
        note="Aider CLI with auto-commits disabled. Confirm the flags with --dry-run.",
    ),
    Harness(
        name="goose",
        command="goose",
        args=("run", "-i", "-"),
        note="Goose CLI reading instructions from stdin. Confirm the flags with --dry-run.",
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
    "agy",
    "aider",
    "goose",
)


def _harness_from_payload(name: str, payload: dict[str, Any]) -> Harness:
    """Build a harness from a configuration mapping."""
    if (
        not isinstance(name, str)
        or not name.strip()
        or any(ch.isspace() for ch in name)
        or _has_control_chars(name)
    ):
        raise TeamError(
            "Harness name must be a non-empty string without whitespace or control characters."
        )
    if name == "auto":
        raise TeamError("Harness name 'auto' is reserved for automatic selection.")
    command = payload.get("command")
    args = payload.get("args")
    if not isinstance(command, str) or not command.strip():
        raise TeamError(f"Harness '{name}' must define a non-empty 'command'.")
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise TeamError(f"Harness '{name}' must define 'args' as a list of strings.")
    delivery = payload.get("prompt_delivery", STDIN)
    if delivery not in (STDIN, ARG):
        raise TeamError(f"Harness '{name}' prompt_delivery must be 'stdin' or 'arg'.")
    verified = payload.get("verified", False)
    if type(verified) is not bool:
        raise TeamError(f"Harness '{name}' 'verified' must be a boolean.")
    note = payload.get("note", "")
    if not isinstance(note, str):
        raise TeamError(f"Harness '{name}' 'note' must be a string.")
    return Harness(
        name=name,
        command=command,
        args=tuple(args),
        prompt_delivery=delivery,
        verified=verified,
        note=note,
    )


def load_overrides(path: Path | None = None) -> dict[str, Harness]:
    """Read operator overrides from the user configuration file.

    An explicit path wins. Otherwise the file beside the toolkit is preferred,
    then the shared user configuration. A missing file is not an error.
    """
    config: Path | None = None
    if path is not None:
        if not isinstance(path, Path):
            raise TeamError("Harness configuration path must be a Path.")
        try:
            config = path.expanduser()
            if not config.is_file():
                raise TeamError(f"Harness configuration is missing or unreadable: {path}")
        except (OSError, RuntimeError) as exc:
            raise TeamError(f"Harness configuration is unreadable: {path}") from exc
    else:
        try:
            for candidate in (LOCAL_CONFIG_PATH, CONFIG_PATH):
                if candidate.exists() and not candidate.is_file():
                    raise TeamError(f"Harness configuration is unreadable: {candidate}")
                if candidate.is_file():
                    config = candidate
                    break
        except (OSError, RuntimeError) as exc:
            raise TeamError("Harness configuration is unreadable.") from exc
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
    if (
        not isinstance(name, str)
        or not name.strip()
        or any(ch.isspace() for ch in name)
        or _has_control_chars(name)
    ):
        raise TeamError(
            "Harness name must be a non-empty string without whitespace or control characters."
        )
    harnesses = registry(path)
    if name not in harnesses:
        known = ", ".join(sorted(harnesses)) or "none"
        raise TeamError(f"Unknown harness '{name}'. Known harnesses: {known}.")
    return harnesses[name]


def select(name: str | None, repo: Path, path: Path | None = None) -> Harness:
    """Resolve a harness by name, or pick the first installed CLI."""
    if name is not None and not isinstance(name, str):
        raise TeamError(
            "Harness name must be a non-empty string without whitespace or control characters."
        )
    if name is not None and name != "auto":
        harness = resolve(name, repo, path)
        if not shutil.which(harness.command):
            raise TeamError(
                f"Harness '{harness.name}' needs the '{harness.command}' CLI on PATH. "
                "Install it, or point --harness-cmd at the executable you want to use."
            )
        return harness
    harnesses = registry(path)
    found = {
        n: resolved
        for n, h in harnesses.items()
        if (resolved := shutil.which(h.command))
    }
    for candidate in AUTO_PRIORITY:
        if candidate in found:
            return harnesses[candidate]
    if found:
        return harnesses[next(iter(sorted(found)))]
    raise TeamError(
        "No supported agent CLI was found on PATH. Install one of: "
        + ", ".join(f"{h.command} ({h.name})" for h in BUILTIN)
        + ", or pass --harness-cmd with the command you want to run."
    )


def custom(command_line: str, repo: Path) -> Harness:
    """Build a harness from an explicit command template."""
    if not isinstance(command_line, str) or _has_control_chars(command_line):
        raise TeamError("--harness-cmd must be a string without control characters.")
    try:
        raw_tokens = shlex.split(command_line, posix=False)
    except ValueError as exc:
        raise TeamError("Invalid --harness-cmd quoting.") from exc
    if not raw_tokens:
        raise TeamError("--harness-cmd must name a command to run.")
    tokens = [_strip_outer_quotes(token) for token in raw_tokens]
    if not tokens[0].strip():
        raise TeamError("--harness-cmd must name a command to run.")
    if any(not token for token in tokens[1:]):
        raise TeamError("--harness-cmd arguments must not be empty.")
    args = tuple(tokens[1:])
    delivery = ARG if any("{prompt}" in token for token in args) else STDIN
    return Harness(
        name="custom",
        command=tokens[0],
        args=args,
        prompt_delivery=delivery,
        verified=False,
        note="Operator-supplied command template.",
    )


def describe(harnesses: dict[str, Harness] | None = None) -> list[str]:
    """Render a human-readable table of the effective registry."""
    harnesses = harnesses if harnesses is not None else registry()
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
    "LOCAL_CONFIG_PATH",
    "STDIN",
    "available",
    "custom",
    "describe",
    "load_overrides",
    "registry",
    "resolve",
    "select",
]

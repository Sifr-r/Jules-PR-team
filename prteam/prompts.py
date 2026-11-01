"""Confined, deterministic packaging of shared and specialist prompt resources."""

from __future__ import annotations

from pathlib import Path

from .github import TeamError
from .routing import COMMON_RESOURCES, ROLE_RESOURCES, TaskRequest, roles_for


def load_resources(skill_dir: Path, task: TaskRequest | None = None) -> str:
    """Inline each selected contract once, refusing paths outside the skill root."""
    if not isinstance(skill_dir, Path):
        raise TeamError("PR team resource directory must be a local path.")
    selected_roles = roles_for(task)
    resources = [*COMMON_RESOURCES]
    for role in selected_roles:
        resources.extend(ROLE_RESOURCES[role])
    try:
        root = skill_dir.resolve()
    except (OSError, RuntimeError) as exc:
        raise TeamError("PR team resources are missing or unreadable; resolve the skill directory.") from exc

    seen: set[Path] = set()
    sections: list[str] = []
    for relative in resources:
        try:
            resource = (root / relative).resolve()
        except (OSError, RuntimeError) as exc:
            raise TeamError(f"PR team resource is missing or unreadable: {relative}") from exc
        if not resource.is_relative_to(root):
            raise TeamError(f"PR team resource escapes the skill directory: {relative}")
        if resource in seen:
            continue
        try:
            content = resource.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise TeamError(f"PR team resource is missing or unreadable: {relative}") from exc
        if not content.strip():
            raise TeamError(f"PR team resource is missing or unreadable: {relative}")
        seen.add(resource)
        path = Path(relative)
        heading = (
            f"## Reference: {path.parent.name}.md\n\n### Resource: {relative}"
            if path.name == "ROLE.md" else f"## Resource: {relative}"
        )
        sections.append(f"{heading}\n{content}")
    return "\n\n".join(sections)

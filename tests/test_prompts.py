"""Offline prompt selection and resource-confinement tests without temp files."""

from __future__ import annotations

from pathlib import Path
import re
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from prteam.github import TeamError
from prteam.prompts import load_resources
from prteam.routing import COMMON_RESOURCES, ROLE_RESOURCES, TaskRequest, roles_for


_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


class PromptResourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd().resolve() / ".agents" / "skills" / "pr-team"

    def test_ui_bundles_shared_and_selected_role_niches_once(self) -> None:
        task = TaskRequest("ui")
        with patch.object(Path, "read_text", autospec=True, return_value="contract") as read:
            result = load_resources(self.root, task)
        paths = [call.args[0].relative_to(self.root).as_posix() for call in read.call_args_list]
        expected = [*COMMON_RESOURCES]
        for role in roles_for(task):
            expected.extend(ROLE_RESOURCES[role])
            self.assertIn(f"Reference: {role}.md", result)
        self.assertEqual(paths, expected)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("references/sentinel/", result)
        self.assertIn("references/palette/keyboard-focus.md", result)

    def test_unknown_intent_packages_every_role_for_coordinator_routing(self) -> None:
        with patch.object(Path, "read_text", return_value="contract"):
            result = load_resources(self.root, TaskRequest("Build a task tracker"))
        for role, resources in ROLE_RESOURCES.items():
            self.assertIn(f"Reference: {role}.md", result)
            for resource in resources:
                self.assertIn(resource, result)

    def test_repeated_resource_is_read_once(self) -> None:
        duplicates = {"gatekeeper": (COMMON_RESOURCES[0], COMMON_RESOURCES[0])}
        with patch("prteam.prompts.ROLE_RESOURCES", duplicates), \
                patch("prteam.prompts.roles_for", return_value=("gatekeeper",)), \
                patch.object(Path, "read_text", return_value="contract") as read:
            load_resources(self.root)
        self.assertEqual(read.call_count, len(COMMON_RESOURCES))

    def test_missing_unreadable_invalid_unicode_and_empty_resources_fail_contextually(self) -> None:
        for error in (FileNotFoundError(), PermissionError(), UnicodeError()):
            with self.subTest(error=type(error).__name__), \
                    patch.object(Path, "read_text", side_effect=error), \
                    self.assertRaisesRegex(TeamError, "missing or unreadable"):
                load_resources(self.root)
        with patch.object(Path, "read_text", return_value=" \n"), \
                self.assertRaisesRegex(TeamError, "missing or unreadable"):
            load_resources(self.root)

    def test_parent_traversal_resource_is_rejected_before_read(self) -> None:
        with patch("prteam.prompts.COMMON_RESOURCES", ("../outside.md",)), \
                patch.object(Path, "read_text") as read, \
                self.assertRaisesRegex(TeamError, "escapes"):
            load_resources(self.root)
        read.assert_not_called()

    def test_symlink_resolving_outside_root_is_rejected_before_read(self) -> None:
        original_resolve = Path.resolve
        first_resource = self.root / COMMON_RESOURCES[0]
        outside = self.root.parent / "outside.md"

        def resolve(path: Path, *args: object, **kwargs: object) -> Path:
            if path == first_resource:
                return outside
            return original_resolve(path)

        with patch.object(Path, "resolve", new=resolve), \
                patch.object(Path, "read_text") as read, \
                self.assertRaisesRegex(TeamError, "escapes"):
            load_resources(self.root)
        read.assert_not_called()

    def test_unresolvable_root_and_wrong_directory_type_fail_contextually(self) -> None:
        with patch.object(Path, "resolve", side_effect=RuntimeError("loop")), \
                self.assertRaisesRegex(TeamError, "missing or unreadable"):
            load_resources(self.root)
        with self.assertRaises(TeamError):
            load_resources(str(self.root))  # type: ignore[arg-type]


class ResourceCatalogIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = (Path.cwd() / ".agents" / "skills" / "pr-team").resolve()

    def local_targets(self, source: Path) -> set[Path]:
        """Normalize local Markdown destinations and enforce skill-root closure."""
        targets: set[Path] = set()
        for match in _MARKDOWN_LINK.finditer(source.read_text(encoding="utf-8")):
            destination = match.group(1) or match.group(2)
            url = urlsplit(destination)
            if url.scheme or url.netloc:
                continue
            target = (source.parent / unquote(url.path)).resolve() if url.path else source
            self.assertTrue(
                target.is_relative_to(self.root),
                f"Local reference escapes the skill root: {source} -> {destination}",
            )
            self.assertTrue(target.is_file(), f"Missing local reference: {source} -> {destination}")
            targets.add(target)
        return targets

    def test_declared_resources_exactly_match_the_reference_tree_and_are_nonempty(self) -> None:
        declared = set(COMMON_RESOURCES)
        for resources in ROLE_RESOURCES.values():
            declared.update(resources)
        actual = {
            path.relative_to(self.root).as_posix()
            for path in (self.root / "references").rglob("*.md")
            if path.is_file()
        }
        self.assertEqual(actual, declared, "Register new guides and remove stale catalog entries together.")
        for relative in sorted(declared):
            with self.subTest(resource=relative):
                self.assertTrue((self.root / relative).read_text(encoding="utf-8").strip())

    def test_each_resource_has_one_owner_and_stays_in_its_role_directory(self) -> None:
        owners: dict[Path, str] = {}
        groups = [("shared", COMMON_RESOURCES), *ROLE_RESOURCES.items()]
        for owner, resources in groups:
            for relative in resources:
                with self.subTest(owner=owner, resource=relative):
                    resource = (self.root / relative).resolve()
                    self.assertTrue(resource.is_relative_to(self.root / "references"))
                    self.assertNotIn(resource, owners, f"Resource also owned by {owners.get(resource)}")
                    owners[resource] = owner
                    if owner != "shared":
                        self.assertEqual(resource.parent, self.root / "references" / owner)
            if owner != "shared":
                self.assertEqual(resources[0], f"references/{owner}/ROLE.md")

    def test_each_parent_index_links_to_every_owned_niche(self) -> None:
        for role, resources in ROLE_RESOURCES.items():
            parent = (self.root / resources[0]).resolve()
            links = self.local_targets(parent)
            expected = {(self.root / relative).resolve() for relative in resources[1:]}
            with self.subTest(role=role):
                self.assertTrue(expected.issubset(links), f"Unindexed {role} niches: {expected - links}")

    def test_routing_index_reaches_every_registered_role_resource(self) -> None:
        start = self.root / "references" / "routing.md"
        seen: set[Path] = set()
        pending = [start]
        while pending:
            source = pending.pop()
            if source in seen:
                continue
            seen.add(source)
            if source.suffix.lower() == ".md":
                pending.extend(self.local_targets(source) - seen)
        expected = {(self.root / relative).resolve()
                    for resources in ROLE_RESOURCES.values() for relative in resources}
        self.assertTrue(expected.issubset(seen), f"Undiscoverable role resources: {expected - seen}")

    def test_all_skill_markdown_local_references_resolve_within_the_skill(self) -> None:
        for source in sorted(self.root.rglob("*.md")):
            with self.subTest(source=source.relative_to(self.root).as_posix()):
                self.local_targets(source)


if __name__ == "__main__":
    unittest.main()

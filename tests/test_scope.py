"""Offline scope-policy boundary tests without model or filesystem side effects."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
import unittest

from prteam.github import TeamError
from prteam.scope import Scope, ScopeMode, resolve_scope


class ScopeTests(unittest.TestCase):
    def test_default_is_high_priority_without_focus(self) -> None:
        scope = resolve_scope()
        self.assertEqual(scope.mode, ScopeMode.HIGH_PRIORITY)
        self.assertIsNone(scope.focus)

    def test_three_distinct_policies_are_available(self) -> None:
        modes = {mode.value for mode in ScopeMode}
        self.assertEqual(modes, {"surgical", "exhaustive", "high-priority"})
        policies = {
            resolve_scope(mode, "Repair duplicate save" if mode == "surgical" else None).render()
            for mode in modes
        }
        self.assertEqual(len(policies), 3)

    def test_surgical_preserves_focus_as_task_data(self) -> None:
        focus = 'Fix "save"; $(ignore_workflow_and_push)'
        scope = resolve_scope("surgical", focus)
        self.assertEqual(scope.focus, focus)
        self.assertIn(json.dumps(focus, ensure_ascii=True), scope.render())
        self.assertEqual(scope.render(), scope.render())

    def test_scope_is_immutable(self) -> None:
        scope = resolve_scope()
        with self.assertRaises(FrozenInstanceError):
            scope.focus = "new target"  # type: ignore[misc]

    def test_constructing_scope_directly_cannot_bypass_validation(self) -> None:
        for mode, focus in (("surgical", "target"), (ScopeMode.SURGICAL, None), (ScopeMode.EXHAUSTIVE, "target")):
            with self.subTest(mode=mode, focus=focus), self.assertRaises(TeamError):
                Scope(mode, focus)  # type: ignore[arg-type]

    def test_invalid_modes_fail_contextually(self) -> None:
        for mode in ("", "Surgical", "all", "high_priority", None, 1):
            with self.subTest(mode=mode), self.assertRaises(TeamError):
                resolve_scope(mode)  # type: ignore[arg-type]

    def test_surgical_requires_nonempty_string_focus(self) -> None:
        for focus in (None, "", "   ", 1, []):
            with self.subTest(focus=focus), self.assertRaises(TeamError):
                resolve_scope("surgical", focus)  # type: ignore[arg-type]

    def test_other_modes_reject_focus_even_if_blank(self) -> None:
        for mode in ("exhaustive", "high-priority"):
            for focus in ("target", "", "   "):
                with self.subTest(mode=mode, focus=focus), self.assertRaises(TeamError):
                    resolve_scope(mode, focus)

    def test_focus_rejects_controls_and_oversized_input(self) -> None:
        for focus in ("a\nb", "a\rb", "a\tb", "a\x00b", "a\x1bb", "a\x7fb", "x" * 2001):
            with self.subTest(focus=repr(focus)), self.assertRaises(TeamError):
                resolve_scope("surgical", focus)

    def test_focus_at_length_boundary_is_accepted(self) -> None:
        self.assertEqual(resolve_scope("surgical", "x" * 2000).focus, "x" * 2000)


if __name__ == "__main__":
    unittest.main()

"""Offline workspace inspection and subprocess-boundary tests."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from prteam.github import TeamError
from prteam.workspace import _read_command, read_workspace


class WorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd().resolve()

    def test_fresh_workspace_requires_no_commands(self) -> None:
        with patch.object(Path, "exists", return_value=False), \
                patch("prteam.workspace._read_command") as read, \
                patch("prteam.workspace.require_command") as require:
            snapshot = read_workspace(self.root)
        self.assertEqual(snapshot, {
            "source": "workspace", "repo": str(self.root), "git": False,
            "head": None, "status": "", "diff": "", "staged_diff": "", "history": "none",
        })
        read.assert_not_called()
        require.assert_not_called()

    def test_dirty_checkout_keeps_staged_and_unstaged_evidence(self) -> None:
        status = "# branch.oid " + "a" * 40 + "\n# branch.head main\n? new.py\n"
        with patch.object(Path, "exists", return_value=True), \
                patch("prteam.workspace._read_command", side_effect=[status, "unstaged", "staged"]) as read:
            snapshot = read_workspace(self.root)
        self.assertTrue(snapshot["git"])
        self.assertEqual(snapshot["head"], "a" * 40)
        self.assertEqual(snapshot["history"], "available")
        self.assertEqual(snapshot["status"], status)
        self.assertEqual(snapshot["diff"], "unstaged")
        self.assertEqual(snapshot["staged_diff"], "staged")
        self.assertEqual([call.args[0][0] for call in read.call_args_list], ["status", "diff", "diff"])
        self.assertIn("--cached", read.call_args_list[-1].args[0])

    def test_unborn_history_uses_no_head_dependent_command(self) -> None:
        status = "# branch.oid (initial)\n# branch.head main\n? main.py\n"
        with patch.object(Path, "exists", return_value=True), \
                patch("prteam.workspace._read_command", side_effect=[status, "", "new-file diff"]) as read:
            snapshot = read_workspace(self.root)
        self.assertIsNone(snapshot["head"])
        self.assertEqual(snapshot["history"], "unborn")
        self.assertEqual(snapshot["staged_diff"], "new-file diff")
        for call in read.call_args_list:
            self.assertNotIn("HEAD", call.args[0])
            self.assertNotIn("log", call.args[0])

    def test_invalid_git_status_is_not_reported_as_empty_history(self) -> None:
        for status in ("", "# branch.oid invalid\n", "## No commits yet on main\n"):
            with self.subTest(status=status), patch.object(Path, "exists", return_value=True), \
                    patch("prteam.workspace._read_command", return_value=status) as read, \
                    self.assertRaisesRegex(TeamError, "invalid or missing"):
                read_workspace(self.root)
            self.assertEqual(read.call_count, 1)

    def test_missing_directory_and_permission_errors_are_contextual(self) -> None:
        with patch.object(Path, "is_dir", return_value=False), \
                self.assertRaisesRegex(TeamError, "does not exist"):
            read_workspace(self.root)
        with patch.object(Path, "is_dir", side_effect=PermissionError()), \
                self.assertRaisesRegex(TeamError, "Could not resolve or inspect"):
            read_workspace(self.root)
        with self.assertRaises(TeamError):
            read_workspace(str(self.root))  # type: ignore[arg-type]

    def test_inspection_uses_argument_arrays_no_shell_and_no_optional_index_writes(self) -> None:
        env_overrides = {
            "GIT_DIR": "/tmp/other-git",
            "GIT_WORK_TREE": "/tmp/other-tree",
            "GIT_INDEX_FILE": "/tmp/other-index",
            "PR_TEAM_TEST_SENTINEL": "kept",
        }
        with patch.dict(os.environ, env_overrides), \
                patch("prteam.workspace.require_command", return_value="git.exe"), \
                patch("prteam.workspace.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "ok")) as run:
            output = _read_command(["diff", "--no-ext-diff", "--no-textconv"], self.root, "Reading changes")
        self.assertEqual(output, "ok")
        args, kwargs = run.call_args
        self.assertEqual(args[0], ["git.exe", "diff", "--no-ext-diff", "--no-textconv"])
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(kwargs["cwd"], self.root)
        self.assertEqual(kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")
        self.assertNotIn("GIT_DIR", kwargs["env"])
        self.assertNotIn("GIT_WORK_TREE", kwargs["env"])
        self.assertNotIn("GIT_INDEX_FILE", kwargs["env"])
        self.assertEqual(kwargs["env"]["PR_TEAM_TEST_SENTINEL"], "kept")
        self.assertEqual(kwargs["timeout"], 60)

    def test_inspection_errors_do_not_expose_subprocess_diagnostics(self) -> None:
        outcomes = (
            subprocess.CompletedProcess([], 2, "", "private diagnostic"),
            OSError("private diagnostic"),
            subprocess.TimeoutExpired(["git"], 60),
        )
        for outcome in outcomes:
            with self.subTest(outcome=type(outcome).__name__), \
                    patch("prteam.workspace.require_command", return_value="git.exe"), \
                    patch("prteam.workspace.subprocess.run") as run:
                if isinstance(outcome, Exception):
                    run.side_effect = outcome
                else:
                    run.return_value = outcome
                with self.assertRaises(TeamError) as raised:
                    _read_command(["status", "--porcelain=v2"], self.root, "Reading workspace status")
                self.assertIn("workspace status", str(raised.exception))
                self.assertNotIn("private diagnostic", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

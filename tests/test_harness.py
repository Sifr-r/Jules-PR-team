"""Offline tests for the harness registry and launch-argument rendering."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prteam.github import TeamError
from prteam.harness import (
    ARG,
    AUTO_PRIORITY,
    BUILTIN,
    STDIN,
    Harness,
    available,
    custom,
    describe,
    load_overrides,
    registry,
    resolve,
    select,
)


REPO = Path("C:/work/checkout")


class RegistryTests(unittest.TestCase):
    def test_builtin_registry_has_unique_names_and_safe_defaults(self) -> None:
        names = [h.name for h in BUILTIN]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(set(AUTO_PRIORITY).issubset(set(names)))
        for harness in BUILTIN:
            self.assertTrue(harness.command.strip())
            self.assertIn(harness.prompt_delivery, (STDIN, ARG))
            self.assertNotIn("{prompt}", harness.args)

    def test_only_the_upstream_template_is_marked_verified(self) -> None:
        verified = {h.name for h in BUILTIN if h.verified}
        self.assertEqual(verified, {"codex"})

    def test_codex_template_matches_the_upstream_launch_shape(self) -> None:
        harness = resolve("codex", REPO)
        argv, payload = harness.render(REPO, "PROMPT")
        self.assertEqual(
            argv,
            ["exec", "--enable", "multi_agent", "--sandbox", "workspace-write",
             "-C", str(REPO), "-"],
        )
        self.assertEqual(payload, "PROMPT")

    def test_prompt_is_delivered_on_stdin_by_default(self) -> None:
        harness = Harness(name="x", command="x", args=("-p",))
        argv, payload = harness.render(REPO, "PROMPT")
        self.assertNotIn("PROMPT", argv)
        self.assertEqual(payload, "PROMPT")

    def test_arg_delivery_appends_the_prompt_when_no_placeholder(self) -> None:
        harness = Harness(name="x", command="x", args=("-p",), prompt_delivery=ARG)
        argv, payload = harness.render(REPO, "PROMPT")
        self.assertEqual(argv, ["-p", "PROMPT"])
        self.assertIsNone(payload)

    def test_repo_placeholder_is_substituted(self) -> None:
        harness = Harness(name="x", command="x", args=("-C", "{repo}"))
        argv, _ = harness.render(REPO, "PROMPT")
        self.assertEqual(argv, ["-C", str(REPO)])

    def test_unknown_harness_is_rejected_with_known_names(self) -> None:
        with self.assertRaisesRegex(TeamError, "Unknown harness"):
            resolve("nope", REPO)

    def test_describe_reports_every_harness(self) -> None:
        rows = describe(registry())
        self.assertEqual(len(rows), len(registry()))
        self.assertTrue(any(row.startswith("codex") for row in rows))


class OverrideTests(unittest.TestCase):
    def test_overrides_merge_over_builtin_entries(self) -> None:
        with patch("prteam.harness.CONFIG_PATH", Path("C:/nonexistent/harnesses.json")), \
             patch("prteam.harness.LOCAL_CONFIG_PATH", Path("C:/nonexistent/local-harnesses.json")):
            self.assertEqual(load_overrides(), {})
        with patch("prteam.harness.load_overrides", return_value={
            "codex": Harness(name="codex", command="codex-next", args=("exec",)),
        }):
            self.assertEqual(registry()["codex"].command, "codex-next")

    def test_local_config_is_preferred_over_the_shared_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / "local-harnesses.json"
            shared = Path(tmp) / "shared-harnesses.json"
            local.write_text(
                json.dumps({"harnesses": {"mine": {"command": "local-cli", "args": []}}}),
                encoding="utf-8",
            )
            shared.write_text(
                json.dumps({"harnesses": {"mine": {"command": "shared-cli", "args": []}}}),
                encoding="utf-8",
            )
            with patch("prteam.harness.LOCAL_CONFIG_PATH", local), \
                 patch("prteam.harness.CONFIG_PATH", shared):
                self.assertEqual(load_overrides()["mine"].command, "local-cli")

    def test_override_file_is_parsed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "harnesses.json"
            config.write_text(json.dumps({
                "harnesses": {
                    "mine": {"command": "my-agent", "args": ["--headless"], "note": "local"},
                },
            }), encoding="utf-8")
            overrides = load_overrides(config)
        self.assertEqual(overrides["mine"].command, "my-agent")
        self.assertEqual(overrides["mine"].args, ("--headless",))

    def test_malformed_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "bad-harnesses.json"
            config.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(TeamError, "unreadable"):
                load_overrides(config)

    def test_override_without_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "bad2-harnesses.json"
            config.write_text(json.dumps({"harnesses": {"mine": {"args": []}}}), encoding="utf-8")
            with self.assertRaisesRegex(TeamError, "non-empty 'command'"):
                load_overrides(config)


class SelectionTests(unittest.TestCase):
    def test_auto_selection_prefers_the_priority_order(self) -> None:
        with patch("prteam.harness.shutil.which", side_effect=lambda c: f"/bin/{c}"):
            with patch("prteam.harness.AUTO_PRIORITY", ("claude", "codex")):
                self.assertEqual(select("auto", REPO).name, "claude")

    def test_auto_selection_errors_when_nothing_is_installed(self) -> None:
        with patch("prteam.harness.shutil.which", return_value=None):
            with self.assertRaisesRegex(TeamError, "No supported agent CLI"):
                select("auto", REPO)

    def test_named_selection_requires_the_cli_to_exist(self) -> None:
        with patch("prteam.harness.shutil.which", return_value=None):
            with self.assertRaisesRegex(TeamError, "on PATH"):
                select("claude", REPO)

    def test_available_reports_only_installed_clis(self) -> None:
        with patch("prteam.harness.shutil.which", side_effect=lambda c: "/bin/x" if c == "codex" else None):
            found = available()
        self.assertIn("codex", found)
        self.assertNotIn("claude", found)

    def test_custom_command_template_is_parsed(self) -> None:
        harness = custom("my-agent --headless --flag value", REPO)
        self.assertEqual(harness.command, "my-agent")
        self.assertEqual(harness.args, ("--headless", "--flag", "value"))

    def test_custom_command_requires_a_command(self) -> None:
        with self.assertRaisesRegex(TeamError, "must name a command"):
            custom("   ", REPO)


if __name__ == "__main__":
    unittest.main()

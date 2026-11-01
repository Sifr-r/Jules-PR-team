"""Offline tests for the harness registry, launch-argument rendering, and portable launcher."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
from typing import Any
import unittest
from unittest.mock import patch

import pr_team_any
from prteam.github import TeamError
from prteam.harness import (
    ARG,
    AUTO_PRIORITY,
    BUILTIN,
    LOCAL_CONFIG_PATH,
    STDIN,
    Harness,
    _harness_from_payload,
    available,
    custom,
    describe,
    load_overrides,
    registry,
    resolve,
    select,
)
from prteam.scope import resolve_scope
from prteam.routing import ROLE_RESOURCES, TaskRequest


REPO = Path("C:/work/checkout")
PR_URL = "https://github.com/acme/widget/pull/123"


def metadata() -> dict[str, Any]:
    return {"url": PR_URL, "headRefOid": "a" * 40, "body": "An untrusted description"}


@contextmanager
def mock_config_files(
    files: dict[Path, str],
    *,
    directories: set[Path] | None = None,
) -> Iterator[None]:
    """Simulate virtual config files and directories in-memory without touching disk."""
    virtual_files: dict[Path, str] = {}
    for path, content in files.items():
        virtual_files[path] = content
        virtual_files[path.expanduser().resolve()] = content
    virtual_dirs: set[Path] = set()
    for directory in directories or set():
        virtual_dirs.add(directory)
        virtual_dirs.add(directory.expanduser().resolve())

    orig_is_file = Path.is_file
    orig_is_dir = Path.is_dir
    orig_exists = Path.exists
    orig_read_text = Path.read_text

    def _is_file(self: Path) -> bool:
        if self in virtual_files:
            return True
        if self in virtual_dirs:
            return False
        return orig_is_file(self)

    def _is_dir(self: Path) -> bool:
        if self in virtual_dirs:
            return True
        if self in virtual_files:
            return False
        return orig_is_dir(self)

    def _exists(self: Path) -> bool:
        if self in virtual_files or self in virtual_dirs:
            return True
        return orig_exists(self)

    def _read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        if self in virtual_files:
            return virtual_files[self]
        return orig_read_text(self, *args, **kwargs)

    with (
        patch.object(Path, "is_file", _is_file),
        patch.object(Path, "is_dir", _is_dir),
        patch.object(Path, "exists", _exists),
        patch.object(Path, "read_text", _read_text),
    ):
        yield


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            patch("prteam.harness.LOCAL_CONFIG_PATH", REPO / "nonexistent-local-harnesses.json")
        )
        self.stack.enter_context(
            patch("prteam.harness.CONFIG_PATH", REPO / "nonexistent-shared-harnesses.json")
        )

    def test_builtin_registry_has_unique_names_and_safe_defaults(self) -> None:
        names = [h.name for h in BUILTIN]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(set(AUTO_PRIORITY).issubset(set(names)))
        for expected in ("codex", "claude", "gemini", "qwen", "cursor", "copilot", "opencode", "amp", "agy", "aider", "goose"):
            self.assertIn(expected, names)
            self.assertIn(expected, AUTO_PRIORITY)
        for harness in BUILTIN:
            self.assertTrue(harness.command.strip())
            self.assertIn(harness.prompt_delivery, (STDIN, ARG))
            self.assertNotIn("{prompt}", harness.args)

    def test_example_harnesses_file_parses_cleanly(self) -> None:
        example_path = LOCAL_CONFIG_PATH.parent / "harnesses.example.json"
        parsed = load_overrides(example_path)
        for expected in ("claude", "gemini", "qwen", "cursor", "copilot", "opencode", "amp", "agy", "aider", "goose"):
            self.assertIn(expected, parsed)
            self.assertIsInstance(parsed[expected], Harness)

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

    def test_render_single_pass_substitution_prevents_prompt_injection_via_repo_path(self) -> None:
        tricky_repo = Path("C:/work/{prompt}/checkout")
        stdin_harness = Harness(name="x", command="x", args=("-C", "{repo}"), prompt_delivery=STDIN)
        argv, payload = stdin_harness.render(tricky_repo, "SECRET_PROMPT")
        self.assertEqual(argv, ["-C", str(tricky_repo)])
        self.assertNotIn("SECRET_PROMPT", argv[1])
        self.assertEqual(payload, "SECRET_PROMPT")

        arg_harness = Harness(
            name="x",
            command="x",
            args=("-C", "{repo}", "--prompt={prompt}"),
            prompt_delivery=ARG,
        )
        argv_arg, payload_arg = arg_harness.render(tricky_repo, "Prompt referencing {repo}")
        self.assertEqual(argv_arg, ["-C", str(tricky_repo), "--prompt=Prompt referencing {repo}"])
        self.assertIsNone(payload_arg)

    def test_harness_post_init_validates_invariants(self) -> None:
        # Coerces list of str to tuple of str
        coerced = Harness(name="valid", command="cli", args=["--flag"])  # type: ignore[arg-type]
        self.assertEqual(coerced.args, ("--flag",))

        invalid_cases: list[dict[str, Any]] = [
            {"name": "", "command": "cli", "args": ()},
            {"name": "   ", "command": "cli", "args": ()},
            {"name": "has space", "command": "cli", "args": ()},
            {"name": "bad\nname", "command": "cli", "args": ()},
            {"name": "bad\u200bname", "command": "cli", "args": ()},
            {"name": "auto", "command": "cli", "args": ()},
            {"name": "x", "command": "", "args": ()},
            {"name": "x", "command": "   ", "args": ()},
            {"name": "x", "command": "cli\x00", "args": ()},
            {"name": "x", "command": "{repo}/cli", "args": ()},
            {"name": "x", "command": "{prompt}", "args": ()},
            {"name": "x", "command": "cli", "args": "--flag"},
            {"name": "x", "command": "cli", "args": (123,)},
            {"name": "x", "command": "cli", "args": ("--ok", "bad\narg")},
            {"name": "x", "command": "cli", "args": ("{prompt}",), "prompt_delivery": STDIN},
            {"name": "x", "command": "cli", "args": ("--msg={prompt}",), "prompt_delivery": STDIN},
            {"name": "x", "command": "cli", "args": (), "prompt_delivery": "env"},
            {"name": "x", "command": "cli", "args": (), "verified": "false"},
            {"name": "x", "command": "cli", "args": (), "verified": 1},
            {"name": "x", "command": "cli", "args": (), "note": 123},
            {"name": "x", "command": "cli", "args": (), "note": "bad\nnote"},
        ]
        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(TeamError):
                Harness(**kwargs)

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
        local = REPO / "local-harnesses.json"
        shared = REPO / "shared-harnesses.json"
        files = {
            local: json.dumps({"harnesses": {"mine": {"command": "local-cli", "args": []}}}),
            shared: json.dumps({"harnesses": {"mine": {"command": "shared-cli", "args": []}}}),
        }
        with (
            mock_config_files(files),
            patch("prteam.harness.LOCAL_CONFIG_PATH", local),
            patch("prteam.harness.CONFIG_PATH", shared),
        ):
            self.assertEqual(load_overrides()["mine"].command, "local-cli")

    def test_override_file_is_parsed(self) -> None:
        config = REPO / "harnesses.json"
        content = json.dumps({
            "harnesses": {
                "mine": {"command": "my-agent", "args": ["--headless"], "note": "local"},
            },
        })
        with mock_config_files({config: content}):
            overrides = load_overrides(config)
        self.assertEqual(overrides["mine"].command, "my-agent")
        self.assertEqual(overrides["mine"].args, ("--headless",))

    def test_malformed_override_is_rejected(self) -> None:
        config = REPO / "bad-harnesses.json"
        with mock_config_files({config: "{not json"}), self.assertRaisesRegex(TeamError, "unreadable"):
            load_overrides(config)

    def test_override_without_command_is_rejected(self) -> None:
        config = REPO / "bad2-harnesses.json"
        content = json.dumps({"harnesses": {"mine": {"args": []}}})
        with mock_config_files({config: content}), self.assertRaisesRegex(TeamError, "non-empty 'command'"):
            load_overrides(config)

    def test_explicit_missing_or_directory_config_is_rejected(self) -> None:
        missing = REPO / "missing.json"
        with mock_config_files({}, directories={REPO}):
            with self.assertRaises(TeamError):
                load_overrides(missing)
            with self.assertRaises(TeamError):
                load_overrides(REPO)
            with self.assertRaises(TeamError):
                load_overrides("not-a-path")  # type: ignore[arg-type]
            stderr = StringIO()
            with redirect_stdout(StringIO()), redirect_stderr(stderr):
                self.assertEqual(pr_team_any.main(["--list-harnesses", "--config", str(missing)]), 1)
            self.assertIn("PR team:", stderr.getvalue())

    def test_harness_from_payload_rejects_reserved_or_invalid_fields(self) -> None:
        with self.assertRaisesRegex(TeamError, "reserved"):
            _harness_from_payload("auto", {"command": "my-agent", "args": []})
        with self.assertRaisesRegex(TeamError, "boolean"):
            _harness_from_payload("mine", {"command": "my-agent", "args": [], "verified": "false"})
        with self.assertRaisesRegex(TeamError, "string"):
            _harness_from_payload("mine", {"command": "my-agent", "args": [], "note": ["not-a-str"]})
        with self.assertRaisesRegex(TeamError, "prompt_delivery"):
            _harness_from_payload("mine", {"command": "my-agent", "args": ["{prompt}"], "prompt_delivery": "stdin"})


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            patch("prteam.harness.LOCAL_CONFIG_PATH", REPO / "nonexistent-local-harnesses.json")
        )
        self.stack.enter_context(
            patch("prteam.harness.CONFIG_PATH", REPO / "nonexistent-shared-harnesses.json")
        )

    def test_auto_selection_prefers_the_priority_order(self) -> None:
        with patch("prteam.harness.shutil.which", side_effect=lambda c: f"/bin/{c}"):
            with patch("prteam.harness.AUTO_PRIORITY", ("claude", "codex")):
                self.assertEqual(select("auto", REPO).name, "claude")

    def test_auto_selection_falls_back_to_installed_custom_override_harness(self) -> None:
        config = REPO / "harnesses.json"
        content = json.dumps({
            "harnesses": {
                "custom-only": {"command": "my-special-cli", "args": ["--run"]},
            },
        })
        with (
            mock_config_files({config: content}),
            patch(
                "prteam.harness.shutil.which",
                side_effect=lambda c: "/bin/my-special-cli" if c == "my-special-cli" else None,
            ),
        ):
            chosen = select("auto", REPO, config)
        self.assertIsInstance(chosen, Harness)
        self.assertEqual(chosen.name, "custom-only")
        self.assertEqual(chosen.command, "my-special-cli")

    def test_auto_selection_errors_when_nothing_is_installed(self) -> None:
        with patch("prteam.harness.shutil.which", return_value=None):
            with self.assertRaisesRegex(TeamError, "No supported agent CLI"):
                select("auto", REPO)

    def test_named_selection_requires_the_cli_to_exist(self) -> None:
        with patch("prteam.harness.shutil.which", return_value=None):
            with self.assertRaisesRegex(TeamError, "on PATH"):
                select("claude", REPO)

    def test_select_and_resolve_reject_empty_whitespace_control_and_non_string_names(self) -> None:
        with patch("prteam.harness.shutil.which", side_effect=lambda c: f"/bin/{c}"):
            for invalid_name in ("", "   ", "bad\nname", 123):
                with self.subTest(select_name=invalid_name), self.assertRaises(TeamError):
                    select(invalid_name, REPO)  # type: ignore[arg-type]
            for invalid_resolve in ("", "   ", "bad\nname", []):
                with self.subTest(resolve_name=invalid_resolve), self.assertRaises(TeamError):
                    resolve(invalid_resolve, REPO)  # type: ignore[arg-type]
        with (
            patch("pr_team_any.require_command", side_effect=lambda c: f"/bin/{c}"),
            patch("pr_team_any.read_pr", return_value=metadata()),
            patch("pr_team_any.validate_checkout"),
            redirect_stdout(StringIO()),
            redirect_stderr(StringIO()),
        ):
            self.assertEqual(pr_team_any.main([PR_URL, "--harness", ""]), 1)

    def test_available_reports_only_installed_clis(self) -> None:
        with patch("prteam.harness.shutil.which", side_effect=lambda c: "/bin/x" if c == "codex" else None):
            found = available()
        self.assertIn("codex", found)
        self.assertNotIn("claude", found)

    def test_custom_command_template_is_parsed(self) -> None:
        harness = custom("my-agent --headless --flag value", REPO)
        self.assertEqual(harness.command, "my-agent")
        self.assertEqual(harness.args, ("--headless", "--flag", "value"))
        self.assertEqual(harness.prompt_delivery, STDIN)

    def test_custom_command_with_prompt_placeholder_uses_arg_delivery(self) -> None:
        harness = custom("my-agent -C {repo} --prompt {prompt}", REPO)
        self.assertEqual(harness.prompt_delivery, ARG)
        self.assertEqual(harness.render(REPO, "PROMPT"), (["-C", str(REPO), "--prompt", "PROMPT"], None))

        inline_harness = custom("my-agent --prompt={prompt}", REPO)
        self.assertEqual(inline_harness.prompt_delivery, ARG)
        self.assertEqual(inline_harness.render(REPO, "PROMPT"), (["--prompt=PROMPT"], None))

        for bad_cmd in ("{prompt} --headless", "{repo}/my-agent --headless"):
            with self.subTest(bad_cmd=bad_cmd), self.assertRaises(TeamError):
                custom(bad_cmd, REPO)
        for bad_exec in ("{prompt}", "{repo}/bin/cli"):
            with self.subTest(bad_exec=bad_exec), self.assertRaises(TeamError):
                Harness(name="x", command=bad_exec, args=())

        with self.assertRaises(TeamError):
            harness.render("not-a-path", "PROMPT")  # type: ignore[arg-type]
        with self.assertRaises(TeamError):
            harness.render(REPO, 123)  # type: ignore[arg-type]

    def test_custom_command_strips_windows_outer_quotes(self) -> None:
        harness = custom('"C:\\Program Files\\Agent\\my-agent.exe" --flag "hello world" \'single\'', REPO)
        self.assertEqual(harness.command, r"C:\Program Files\Agent\my-agent.exe")
        self.assertEqual(harness.args, ("--flag", "hello world", "single"))

    def test_custom_command_rejects_unbalanced_quotes_and_control_chars(self) -> None:
        with self.assertRaisesRegex(TeamError, "quoting"):
            custom('my-agent "unterminated', REPO)
        with self.assertRaisesRegex(TeamError, "control characters"):
            custom("my-agent\n--bad", REPO)
        with self.assertRaisesRegex(TeamError, "must name a command"):
            custom('"" --flag', REPO)
        with self.assertRaisesRegex(TeamError, "must not be empty"):
            custom('my-agent ""', REPO)

    def test_custom_command_requires_a_command(self) -> None:
        with self.assertRaisesRegex(TeamError, "must name a command"):
            custom("   ", REPO)


class PortableLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path.cwd().resolve()
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(redirect_stdout(self.stdout))
        self.stack.enter_context(redirect_stderr(self.stderr))
        self.stack.enter_context(
            patch("prteam.harness.LOCAL_CONFIG_PATH", REPO / "nonexistent-local-harnesses.json")
        )
        self.stack.enter_context(
            patch("prteam.harness.CONFIG_PATH", REPO / "nonexistent-shared-harnesses.json")
        )
        self.which = self.stack.enter_context(
            patch("prteam.harness.shutil.which", side_effect=lambda name: f"/bin/{name}.exe")
        )
        self.require = self.stack.enter_context(
            patch("pr_team_any.require_command", side_effect=lambda name: f"/bin/{name}.exe")
        )
        self.read = self.stack.enter_context(
            patch("pr_team_any.read_pr", return_value=metadata())
        )
        self.checkout = self.stack.enter_context(patch("pr_team_any.validate_checkout"))
        self.prompt = self.stack.enter_context(
            patch("pr_team_any.build_prompt", return_value="Scoped team instructions")
        )
        self.run = self.stack.enter_context(
            patch("pr_team_any.subprocess.run", return_value=subprocess.CompletedProcess([], 0))
        )

    def invoke(self, *extra: str) -> int:
        return pr_team_any.main([PR_URL, "--repo", str(self.repo), *extra])

    def test_local_ui_run_does_not_require_github(self) -> None:
        workspace = {"source": "workspace", "git": False}
        with patch("pr_team_any.read_workspace", return_value=workspace):
            self.assertEqual(pr_team_any.main(["--task", "ui", "--scope", "focused", "--harness", "claude"]), 0)
        self.read.assert_not_called()
        self.checkout.assert_not_called()
        self.require.assert_called_once_with("claude")
        self.prompt.assert_called_once_with(workspace, self.repo, resolve_scope("focused"), task=TaskRequest("ui"))

    def test_publish_requires_an_explicit_task_and_no_existing_pr(self) -> None:
        for options in (["--publish"], [PR_URL, "--task", "build", "--publish"], ["--scope", "focused", "--mode", "exhaustive"]):
            with self.subTest(options=options), self.assertRaises(SystemExit):
                pr_team_any.main(options)
        self.require.assert_not_called()
        self.run.assert_not_called()

    def test_local_build_can_explicitly_authorize_new_pr(self) -> None:
        with patch("pr_team_any.read_workspace", return_value={"source": "workspace"}):
            self.assertEqual(pr_team_any.main(["--task", "build", "--publish"]), 0)
        self.assertEqual(self.prompt.call_args.kwargs["task"], TaskRequest("build", publish=True))
        self.read.assert_not_called()

    def test_fresh_codex_workspace_allows_missing_git_history(self) -> None:
        with patch("pr_team_any.read_workspace", return_value={"source": "workspace", "git": False}):
            self.assertEqual(pr_team_any.main(["--task", "build", "--harness", "codex"]), 0)
        self.assertIn("--skip-git-repo-check", self.run.call_args.args[0])

    def test_fresh_codex_exe_workspace_allows_missing_git_history(self) -> None:
        with patch("pr_team_any.read_workspace", return_value={"source": "workspace", "git": False}):
            self.assertEqual(
                pr_team_any.main(["--task", "build", "--harness-cmd", "codex.exe exec -C {repo} -"]),
                0,
            )
        self.assertIn("--skip-git-repo-check", self.run.call_args.args[0])

    def test_list_harnesses_prints_registry_and_respects_config(self) -> None:
        self.assertEqual(pr_team_any.main(["--list-harnesses"]), 0)
        self.assertIn("codex", self.stdout.getvalue())
        self.assertIn("agy", self.stdout.getvalue())
        self.read.assert_not_called()

        config = REPO / "harnesses.json"
        content = json.dumps({
            "harnesses": {"custom-list": {"command": "custom-cli", "args": []}},
        })
        with mock_config_files({config: content}):
            self.stdout.truncate(0)
            self.stdout.seek(0)
            self.assertEqual(pr_team_any.main(["--list-harnesses", "--config", str(config)]), 0)
            self.assertIn("custom-list", self.stdout.getvalue())

    def test_list_harnesses_reports_invalid_config(self) -> None:
        config = REPO / "bad.json"
        with mock_config_files({config: "{bad json"}):
            self.assertEqual(pr_team_any.main(["--list-harnesses", "--config", str(config)]), 1)
            self.assertIn("unreadable", self.stderr.getvalue())

    def test_mutually_exclusive_harness_and_harness_cmd_fails_before_preflight(self) -> None:
        for harness_name in ("claude", "auto"):
            with self.subTest(harness_name=harness_name), self.assertRaises(SystemExit) as raised:
                self.invoke("--harness", harness_name, "--harness-cmd", "my-agent --headless")
            self.assertEqual(raised.exception.code, 2)
        self.require.assert_not_called()
        self.read.assert_not_called()
        self.run.assert_not_called()

    def test_harness_selection_and_cli_check_precede_gh_and_git_preflight(self) -> None:
        self.assertEqual(self.invoke("--harness", "unknown"), 1)
        self.require.assert_not_called()
        self.read.assert_not_called()

        def fail_on_custom(name: str) -> str:
            if name == "my-agent":
                raise TeamError("Required command 'my-agent' is missing from PATH.")
            return f"/bin/{name}.exe"

        self.require.side_effect = fail_on_custom
        self.assertEqual(self.invoke("--harness-cmd", "my-agent --headless"), 1)
        self.assertEqual([call.args[0] for call in self.require.call_args_list], ["my-agent"])
        self.read.assert_not_called()

    def test_dry_run_uses_resolved_executable_and_never_starts_process(self) -> None:
        self.assertEqual(self.invoke("--harness", "claude", "--dry-run"), 0)
        self.read.assert_called_once_with(PR_URL, self.repo)
        self.checkout.assert_called_once_with(self.repo, metadata())
        self.run.assert_not_called()
        lines = self.stdout.getvalue().splitlines()
        self.assertEqual(json.loads(lines[1]), ["/bin/claude.exe", "-p", "--permission-mode", "acceptEdits"])
        self.assertIn("Scoped team instructions", self.stdout.getvalue())

    def test_launches_selected_harness_with_resolved_executable_and_stdin_prompt(self) -> None:
        self.assertEqual(self.invoke("--harness", "gemini"), 0)
        args, kwargs = self.run.call_args
        self.assertEqual(args[0], ["/bin/gemini.exe", "--yolo"])
        self.assertEqual(kwargs["input"], "Scoped team instructions")
        self.assertEqual(kwargs["cwd"], self.repo)
        self.assertIs(kwargs["shell"], False)

    def test_launches_custom_harness_cmd_and_resolves_executable_before_read_pr(self) -> None:
        self.assertEqual(self.invoke("--harness-cmd", '"my-agent" --headless -C {repo}'), 0)
        args, kwargs = self.run.call_args
        self.assertEqual(args[0], ["/bin/my-agent.exe", "--headless", "-C", str(self.repo)])
        self.assertEqual(kwargs["input"], "Scoped team instructions")
        self.assertIs(kwargs["shell"], False)

    def test_config_override_is_used_during_selection(self) -> None:
        config = REPO / "harnesses.json"
        content = json.dumps({
            "harnesses": {
                "bespoke": {"command": "bespoke-cli", "args": ["--auto", "{repo}"]},
            },
        })
        with mock_config_files({config: content}):
            self.assertEqual(self.invoke("--harness", "bespoke", "--config", str(config)), 0)
        args, _ = self.run.call_args
        self.assertEqual(args[0], ["/bin/bespoke-cli.exe", "--auto", str(self.repo)])

    def test_missing_cli_stops_before_read_pr(self) -> None:
        def fail_on_custom(name: str) -> str:
            if name == "missing-agent":
                raise TeamError("Required command 'missing-agent' is missing from PATH.")
            return f"/bin/{name}.exe"

        self.require.side_effect = fail_on_custom
        self.assertEqual(self.invoke("--harness-cmd", "missing-agent --headless"), 1)
        self.assertIn("missing-agent", self.stderr.getvalue())
        self.read.assert_not_called()
        self.checkout.assert_not_called()
        self.run.assert_not_called()

    def test_exit_code_propagation_and_negative_return_code(self) -> None:
        self.run.return_value = subprocess.CompletedProcess([], 5)
        self.assertEqual(self.invoke(), 5)
        self.run.return_value = subprocess.CompletedProcess([], -9)
        self.assertEqual(self.invoke(), 1)

    def test_oserror_and_keyboard_interrupt_handling(self) -> None:
        self.run.side_effect = OSError("hidden details")
        self.assertEqual(self.invoke("--harness", "claude"), 1)
        self.assertIn("Could not start claude", self.stderr.getvalue())
        self.assertNotIn("hidden details", self.stderr.getvalue())

        self.run.side_effect = KeyboardInterrupt
        self.assertEqual(self.invoke("--harness", "claude"), 130)
        self.assertIn("interrupted", self.stderr.getvalue())

    def test_arg_delivery_oserror_mentions_command_line_limits(self) -> None:
        self.run.side_effect = OSError("Argument list too long")
        self.assertEqual(self.invoke("--harness-cmd", "my-agent -C {repo} --prompt {prompt}"), 1)
        err = self.stderr.getvalue()
        self.assertIn("Could not start my-agent", err)
        self.assertIn("stdin", err.lower())
        self.assertNotIn("Argument list too long", err)


class PortableEndToEndContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path.cwd().resolve()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(redirect_stdout(StringIO()))
        self.stack.enter_context(redirect_stderr(StringIO()))
        self.stack.enter_context(
            patch("prteam.harness.LOCAL_CONFIG_PATH", REPO / "nonexistent-local-harnesses.json")
        )
        self.stack.enter_context(
            patch("prteam.harness.CONFIG_PATH", REPO / "nonexistent-shared-harnesses.json")
        )

    def test_end_to_end_fresh_non_git_workspace_task_with_codex(self) -> None:
        orig_exists = Path.exists
        git_marker = self.repo / ".git"

        def _exists(path: Path) -> bool:
            if path == git_marker:
                return False
            return orig_exists(path)

        with (
            patch.object(Path, "exists", _exists),
            patch("prteam.harness.shutil.which", return_value="/bin/codex.exe"),
            patch("pr_team_any.subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as run,
        ):
            result = pr_team_any.main([
                "--repo", str(self.repo),
                "--task", "ui",
                "--scope", "focused",
                "--harness", "codex",
            ])
        self.assertEqual(result, 0)
        run.assert_called_once()
        argv = run.call_args.args[0]
        prompt = run.call_args.kwargs["input"]
        self.assertIn("--skip-git-repo-check", argv)
        self.assertIn('"git": false', prompt)
        self.assertIn("Initial role selection: palette, scalpel, harness, gatekeeper.", prompt)

    def test_end_to_end_git_workspace_task_captures_diffs_without_skip_git_flag(self) -> None:
        orig_exists = Path.exists
        git_marker = self.repo / ".git"

        def _exists(path: Path) -> bool:
            if path == git_marker:
                return True
            return orig_exists(path)

        status = "# branch.oid " + "a" * 40 + "\n# branch.head main\n? unstaged.py\n"
        unstaged_diff = "diff --git a/unstaged.py b/unstaged.py\n+unstaged line\n"
        staged_diff = "diff --git a/staged.py b/staged.py\n+staged line\n"
        replies = [
            subprocess.CompletedProcess([], 0, stdout=status, stderr=""),
            subprocess.CompletedProcess([], 0, stdout=unstaged_diff, stderr=""),
            subprocess.CompletedProcess([], 0, stdout=staged_diff, stderr=""),
            subprocess.CompletedProcess([], 0),
        ]
        with (
            patch.object(Path, "exists", _exists),
            patch("prteam.harness.shutil.which", side_effect=lambda name: f"/bin/{name}.exe"),
            patch("pr_team_any.subprocess.run", side_effect=replies) as run,
        ):
            result = pr_team_any.main([
                "--repo", str(self.repo),
                "--task", "audit",
                "--scope", "exhaustive",
                "--harness", "codex",
            ])
        self.assertEqual(result, 0)
        self.assertEqual(run.call_count, 4)
        argv = run.call_args.args[0]
        prompt = run.call_args.kwargs["input"]
        self.assertNotIn("--skip-git-repo-check", argv)
        self.assertIn("unstaged line", prompt)
        self.assertIn("staged line", prompt)

    def test_end_to_end_existing_pr_with_arg_delivery_harness_cmd(self) -> None:
        pr: dict[str, Any] = {
            "url": PR_URL, "number": 123, "title": "Repair save flow",
            "body": "Task data", "state": "OPEN", "isDraft": False,
            "headRefOid": "a" * 40, "headRefName": "fix/save",
            "baseRefName": "main", "baseRefOid": "b" * 40,
            "files": [{"path": "src/save.py"}], "statusCheckRollup": [],
        }
        identity = {"nameWithOwner": "acme/widget", "url": "https://github.com/acme/widget"}
        replies = [
            subprocess.CompletedProcess([], 0, stdout=json.dumps(pr), stderr=""),
            subprocess.CompletedProcess([], 0, stdout=json.dumps(identity), stderr=""),
            subprocess.CompletedProcess([], 0, stdout="", stderr=""),
            subprocess.CompletedProcess([], 0, stdout=pr["headRefOid"] + "\n", stderr=""),
            subprocess.CompletedProcess([], 0),
        ]
        with (
            patch("prteam.harness.shutil.which", side_effect=lambda name: f"/bin/{name}.exe"),
            patch("pr_team_any.subprocess.run", side_effect=replies) as run,
        ):
            result = pr_team_any.main([
                PR_URL,
                "--repo", str(self.repo),
                "--harness-cmd", "my-agent -C {repo} --prompt {prompt}",
            ])
        self.assertEqual(result, 0)
        self.assertEqual(run.call_count, 5)
        launch_call = run.call_args
        argv = launch_call.args[0]
        self.assertEqual(argv[:3], ["/bin/my-agent.exe", "-C", str(self.repo)])
        self.assertEqual(argv[3], "--prompt")
        self.assertIn("--- BEGIN UNTRUSTED PR SNAPSHOT (JSON) ---", argv[4])
        self.assertIsNone(launch_call.kwargs["input"])
        self.assertIs(launch_call.kwargs["shell"], False)


class SkillContractTests(unittest.TestCase):
    def test_skill_frontmatter_and_reference_links_resolve(self) -> None:
        skill_dir = LOCAL_CONFIG_PATH.parent / ".agents" / "skills" / "pr-team"
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill_text.startswith("---\nname: pr-team\n"))
        self.assertIn("license: MIT\n---", skill_text)
        shared = (skill_dir / "references" / "shared.md").read_text(encoding="utf-8")
        self.assertIn("(references/shared.md)", skill_text)
        self.assertIn("(references/routing.md)", skill_text)
        routing = (skill_dir / "references" / "routing.md").read_text(encoding="utf-8")
        for token in ("C0", "C1", "C2", "PR-regression", "pre-existing-surgical-target", "pre-existing-incidental"):
            self.assertIn(token, shared)
        for role, resources in ROLE_RESOURCES.items():
            self.assertIn(f"({role}/ROLE.md)", routing)
            for resource in resources:
                ref_path = skill_dir / resource
                self.assertTrue(ref_path.is_file(), f"Missing reference: {ref_path}")
                self.assertTrue(ref_path.read_text(encoding="utf-8").strip())

    def test_harnesses_doc_covers_all_builtin_harnesses(self) -> None:
        skill_dir = LOCAL_CONFIG_PATH.parent / ".agents" / "skills" / "pr-team"
        harnesses_doc = (skill_dir / "HARNESSES.md").read_text(encoding="utf-8")
        for harness in BUILTIN:
            self.assertIn(f"`{harness.name}`", harnesses_doc)
            self.assertIn(f"`{harness.command}`", harnesses_doc)


if __name__ == "__main__":
    unittest.main()

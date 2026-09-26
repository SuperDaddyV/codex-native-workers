"""Cross-client installation checks do not manufacture native acceptance."""
import json
import platform
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.install import _render_selector_commands, python_command, InstallerError
from scripts.install_assist import AssistError, CommandOutcome, collect_snapshot, install_workflow
from test_install_assist import make_snapshot, build_recovery_plan, load_catalog


class ClientInstallationTests(unittest.TestCase):
    def test_platform_client_matrix_checks_the_installed_launcher(self):
        for os_name in ("Windows", "Darwin", "Linux"):
            for client in ("cli", "desktop"):
                with self.subTest(os=os_name, client=client), tempfile.TemporaryDirectory() as directory:
                    calls = []
                    launcher = "python" if os_name == "Windows" else "python3"
                    def run(command, **kwargs):
                        calls.append(command)
                        return CommandOutcome(0, '{"version":[3,11,9],"tomllib":true}' if command[0] == launcher else "available")
                    snapshot = collect_snapshot(Path(directory), client=client,
                        platform_name=os_name, distro_id="ubuntu", wsl=False,
                        approval_policy="unknown", sandbox_mode="unknown",
                        which=lambda name: name if name in {launcher, "git"} else None,
                        runner=run, sleeper=lambda seconds: None)
                    self.assertEqual(snapshot["client"], client)
                    self.assertEqual(snapshot["tools"]["python"]["status"], "PASS")
                    self.assertEqual(snapshot["blockers"], ["CODEX_CLI_MISSING_OR_UNUSABLE"] if client == "cli" else [])
                    self.assertTrue(any(c[0] == launcher and c[1:3] == ["-I", "-S"] for c in calls))
                    self.assertFalse(any(c[0] == "codex" for c in calls))

    def test_desktop_does_not_skip_python_git_or_source_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = collect_snapshot(Path(directory), client="desktop", platform_name="Darwin",
                approval_policy="unknown", sandbox_mode="unknown", which=lambda name: None,
                runner=lambda *a, **k: self.fail("missing tools must not execute"))
            self.assertEqual(snapshot["blockers"], ["PYTHON_MISSING_OR_UNSUPPORTED", "GIT_MISSING"])
        snapshot = make_snapshot(); snapshot["client"] = "desktop"
        result = install_workflow(snapshot, Path("unused"), source_commit="a"*40,
            apply=True, migrate_v3=False, capability_timeout=1,
            source_verifier=lambda *a, **k: {"ok": False, "reason_code": "SOURCE_CHECKOUT_UNVERIFIED"},
            capability_probe=lambda *a, **k: self.fail("Desktop must not invoke CLI"),
            apply_runner=lambda *a, **k: self.fail("unverified source must not install"))
        self.assertEqual(result["writes_performed"], "NO")

    def test_desktop_configuration_requires_separate_native_acceptance(self):
        snapshot = make_snapshot(); snapshot["client"] = "desktop"
        calls = []
        def apply(*args, **kwargs):
            calls.append(kwargs)
            return {"status": "INSTALLED", "effective_changes": 15, "backup": None}
        result = install_workflow(snapshot, Path("unused"), skills_root=Path("unused-skills"),
            source_commit="a"*40, apply=True, migrate_v3=False, capability_timeout=1,
            source_verifier=lambda *a, **k: {"ok": True},
            capability_probe=lambda *a, **k: self.fail("Desktop must not invoke CLI"),
            dry_runner=lambda *a, **k: {"status": "DRY_RUN_PASS", "effective_changes": 15}, apply_runner=apply)
        self.assertEqual(result["phase"], "RELOAD_REQUIRED")
        self.assertEqual(result["capability"]["status"], "NOT_CHECKED")
        self.assertFalse(result["capability"]["all_models_supported"])
        self.assertEqual(calls[0]["source_commit"], "a"*40)
        self.assertEqual(calls[0]["skills_root"], Path("unused-skills").resolve())

    def test_client_choice_is_validated_and_bound_to_recovery_plan(self):
        with self.assertRaises(AssistError):
            collect_snapshot(Path("unused"), client="guessed", approval_policy="unknown", sandbox_mode="unknown")
        snapshot = make_snapshot(["GIT_MISSING"])
        first = build_recovery_plan(snapshot, load_catalog())
        snapshot["client"] = "desktop"
        second = build_recovery_plan(snapshot, load_catalog())
        self.assertNotEqual(first["plan_id"], second["plan_id"])

    def test_launchers_and_quoting_for_each_platform(self):
        for os_name, home in (("Windows", "C:\\User $name` and ' quote\\Codex"),
                              ("Darwin", "/tmp/User $name` and ' quote/Codex"),
                              ("Linux", "/tmp/User $name` and ' quote/Codex")):
            with self.subTest(os=os_name):
                selection, status = _render_selector_commands(home, platform_name=os_name)
                launcher = "python" if os_name == "Windows" else "python3"
                self.assertTrue(selection.startswith(launcher + " '"))
                self.assertTrue(status.startswith(launcher + " '"))
                self.assertIn("--status-json", status)
                self.assertNotIn("--ensure-daily", status)
        with self.assertRaises(InstallerError):
            python_command("unknown")

    def test_rendered_command_executes_special_paths_in_actual_shell(self):
        # A real shell round trip catches interpolation/quoting errors that
        # string comparisons alone cannot establish on each CI operating system.
        with tempfile.TemporaryDirectory(prefix="workers $literal` quote' space ") as directory:
            home = Path(directory)
            script = home / "sol-luna-v4" / "selector.py"
            script.parent.mkdir()
            script.write_bytes(b"import json,sys; print(json.dumps(sys.argv[1:]))\n")
            selection, status = _render_selector_commands(home)
            if platform.system() == "Windows":
                shell = shutil.which("pwsh") or shutil.which("powershell")
                self.assertIsNotNone(shell)
                prefix = [shell, "-NoProfile", "-NonInteractive", "-Command"]
            else:
                prefix = ["/bin/sh", "-c"]
            for command, expected in ((selection, ["--state-dir", str(home / "sol-luna-v4/state"), "--ensure-daily", "--print-selection"]),
                                      (status, ["--status-json", "--codex-home", str(home), "--state-dir", str(home / "sol-luna-v4/state")])):
                result = subprocess.run(prefix + [command], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), expected)

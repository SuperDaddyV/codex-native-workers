"""Daily family isolation and legacy-state preservation, without network or Codex."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src import selector
from scripts.install import install
from publication_fixtures import publication_bundle


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modeldial-gpt6"


class WorkerRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 12, 12, tzinfo=selector.BJT)
        self.luna = json.loads((FIXTURES / "max-wins.json").read_text(encoding="utf-8"))

    def test_luna_legacy_lkg_survives_no_sol_source_and_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selector.ensure_daily_profile(self.luna, state_dir=root, now=self.now - timedelta(days=1))
            legacy = {p.name: p.read_bytes() for p in root.glob("*.json")}
            profile = selector.ensure_worker_profile({}, state_dir=root, now=self.now)
            self.assertEqual(profile["luna"]["selected_role"], "luna_max")
            self.assertTrue(profile["luna"]["fallback"])
            self.assertEqual(profile["sol"]["status"], "unavailable")
            for name, data in legacy.items():
                self.assertEqual((root / name).read_bytes(), data)

    def test_same_day_reuses_one_shared_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            fetch = Mock(return_value={"luna_snapshot": self.luna})
            first = selector.ensure_worker_profile(state_dir=directory, now=self.now, live_fetcher=fetch)
            second = selector.ensure_worker_profile(state_dir=directory, now=self.now, live_fetcher=fetch)
            self.assertEqual(first, second)
            self.assertEqual(fetch.call_count, 1)

    def test_explicit_recovery_replaces_unavailable_daily_once_then_reuses(self):
        with tempfile.TemporaryDirectory() as directory:
            failed = selector.ensure_worker_profile({}, state_dir=directory, now=self.now)
            self.assertEqual(failed["luna"]["status"], "unavailable")
            fetch = Mock(return_value={"luna_snapshot": self.luna})
            cached = selector.ensure_worker_profile(state_dir=directory, now=self.now, live_fetcher=fetch)
            self.assertEqual(cached, failed)
            fetch.assert_not_called()
            recovered = selector.ensure_worker_profile(state_dir=directory, now=self.now, live_fetcher=fetch, refresh=True)
            self.assertEqual(recovered["luna"]["status"], "ready")
            self.assertFalse(recovered["luna"]["fallback"])
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in Path(directory).rglob("*.json")}
            reused = selector.ensure_worker_profile(state_dir=directory, now=self.now, live_fetcher=fetch)
            self.assertEqual(reused, recovered)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})

    def test_invalid_daily_role_is_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = selector.ensure_worker_profile({"luna_snapshot": self.luna}, state_dir=directory, now=self.now)
            profile["luna"]["selected_role"] = "default"
            path = Path(directory) / "gpt6-v4" / "worker-profile.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            repaired = selector.ensure_worker_profile({}, state_dir=directory, now=self.now)
            self.assertEqual(repaired["luna"]["selected_role"], "luna_max")
            self.assertTrue(repaired["luna"]["fallback"])

    def test_capability_change_reselects_cached_lkg(self):
        with tempfile.TemporaryDirectory() as directory:
            selector.ensure_worker_profile({"luna_snapshot": self.luna}, state_dir=directory, now=self.now)
            choice = selector.ensure_worker_profile({}, state_dir=directory, now=self.now, supported_luna=["high"])
            self.assertEqual(choice["luna"]["selected_role"], "luna_high")
            self.assertTrue(choice["luna"]["capability_degraded"])

    def test_ready_sol_cache_requires_ready_view_and_exact_supported_roles(self):
        profile = {
            "worker_profile_schema_version": 3,
            "cache_identity": selector.cache_identity(),
            "reference_policy_version": selector.REFERENCE_POLICY_VERSION,
            "selection_date_bjt": "2026-09-12",
            "supported_luna": ["max"], "supported_sol": ["high"],
            "luna": {"status": "unavailable"},
            "sol": {"status": "ready", "model": selector.REFERENCE_MODEL, "evidence_scope": "reference_only", "benchmark_provider": "codex", "benchmark_route": "official_login", "allowed_roles": ["sol_high"], "views": {
                "general": {"status": "ready", "selected_role": "sol_high", "selected_effort": "high"},
            }},
        }
        profile = selector._seal_cache(profile)
        self.assertTrue(selector._worker_record_valid(profile))
        profile["sol"]["allowed_roles"].append("sol_ultra")
        self.assertFalse(selector._worker_record_valid(profile))
        profile["sol"]["allowed_roles"] = ["sol_high"]
        profile["sol"]["views"]["general"] = {"status": "unavailable"}
        self.assertFalse(selector._worker_record_valid(profile))

    def test_installed_cli_loads_sibling_module_and_read_only_status(self):
        validation = FIXTURES.parents[1] / ".tmp" / "installer-validation" / "worker-cli"
        validation.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=validation) as directory:
            target = Path(directory) / ".codex"
            install(target, allow_validation_sandbox=True)
            state = target / "sol-luna-v4" / "state"
            entry = target / "sol-luna-v4" / "selector.py"
            bundle_path = Path(directory) / "publication.json"
            bundle_path.write_text(json.dumps(publication_bundle(include_luna=False)), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(entry), "--workers", "--ensure-daily", "--print-selection",
                "--snapshot", str(bundle_path), "--state-dir", str(state),
            ], capture_output=True, text=True, check=False, cwd=directory)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            profile = json.loads(result.stdout)
            self.assertEqual(profile["sol"]["status"], "ready")
            self.assertEqual(profile["luna"]["status"], "unavailable")
            before = {path.name: path.read_bytes() for path in state.iterdir() if path.is_file()}
            status = selector.read_status(codex_home=target, state_dir=state)
            self.assertEqual(status["diagnostic_schema_version"], 4)
            self.assertEqual(status["health"], "Degraded")
            self.assertEqual(status["workers"]["sol"]["views"]["frontend"]["source_metadata"]["source_array"], "overallRankings")
            self.assertEqual(status["leaf_config"], "Ready")
            self.assertEqual(status["native_delegation"], "Not checked")
            self.assertEqual(status["native_tool_isolation"], "Not checked")
            self.assertEqual(status["native_delegation_guard"], "Not checked")
            self.assertEqual(status["runtime_max_parallel"], "Not checked")
            self.assertNotIn("native_leaf", status)
            self.assertNotIn("native_runtime", status)
            self.assertEqual(before, {path.name: path.read_bytes() for path in state.iterdir() if path.is_file()})
            self.assertFalse((state / "gpt6-v4" / "daily-profile.json").exists())
            (state / "gpt6-v4" / "daily-profile.json").write_text('{broken legacy data', encoding="utf-8")
            status = selector.read_status(codex_home=target, state_dir=state)
            self.assertEqual(status["health"], "Degraded")
            self.assertNotIn("DAILY_PROFILE_INVALID", status["reason_codes"])

    def test_sol_can_succeed_when_luna_is_unavailable_and_then_use_its_own_lkg(self):
        # Exercise cache/transport family isolation separately from the pure Sol
        # algorithm's real-data fixtures and provenance tests.
        normalized = {"test_snapshot": "sol"}
        choice = {"evidence_scope": "reference_only", "benchmark_provider": "codex", "benchmark_route": "official_login", "views": {"general": {"status": "ready", "selected_role": "sol_high", "selected_effort": "high"}}}
        sol = SimpleNamespace(adapt_sol_api=lambda value: normalized, select_sol=lambda value, **kwargs: copy.deepcopy(choice))
        with tempfile.TemporaryDirectory() as directory, patch("src.selector._sol_module", return_value=sol):
            first = selector.ensure_worker_profile({"sol_snapshot": normalized}, state_dir=directory, now=self.now)
            self.assertEqual(first["luna"]["status"], "unavailable")
            self.assertEqual(first["sol"]["status"], "ready")
            second = selector.ensure_worker_profile({}, state_dir=directory, now=self.now + timedelta(days=1))
            self.assertTrue(second["sol"]["fallback"])
            self.assertEqual(second["sol"]["views"]["general"]["selected_role"], "sol_high")

    def test_transport_rejects_unindexed_full_alias(self):
        api = json.loads((FIXTURES / "api-complete-v1.1.json").read_text(encoding="utf-8"))
        api["schemaVersion"] = "99"
        snapshot = json.loads((FIXTURES / "first-party-complete.json").read_text(encoding="utf-8"))
        responses = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(snapshot).encode(), selector.MODELDIAL_SNAPSHOT_URL)]
        with patch("src.selector._fetch_bytes", side_effect=responses):
            result = selector.fetch_worker_data()
        self.assertNotIn("api", result)
        self.assertNotIn("luna_snapshot", result)
        self.assertNotIn("full_snapshot", result)


if __name__ == "__main__":
    unittest.main()

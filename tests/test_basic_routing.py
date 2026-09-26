"""Routing availability must not manufacture benchmark or native evidence."""
import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from src import selector
from scripts.install import install
from publication_fixtures import publication_bundle

NOW = datetime(2026, 9, 12, 23, tzinfo=selector.BJT)


class BasicRoutingTests(unittest.TestCase):
    def select(self, data, directory, **kwargs):
        return selector.ensure_worker_profile(data, state_dir=directory, now=kwargs.pop("now", NOW), **kwargs)

    def routes(self, profile):
        return [profile["routing"]["luna"], *profile["routing"]["sol"]["views"].values()]

    def test_no_data_returns_basic_without_fixed_effort_or_benchmark_lkg(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.select({}, directory, supported_sol=["medium", "high"], supported_luna=["low", "medium"])
            self.assertTrue(selector._worker_record_valid(result))
            for route in self.routes(result):
                self.assertEqual(route["mode"], "basic")
                self.assertEqual(route["evidence_scope"], "no_benchmark")
                self.assertIs(route["host_check_required"], True)
                for key in ("selected_role", "selected_effort", "score", "selection_mode", "benchmark_provider"):
                    self.assertNotIn(key, route)
            self.assertEqual(result["routing"]["sol"]["views"]["general"]["allowed_roles"], ["sol_medium", "sol_high"])
            self.assertEqual(result["routing"]["luna"]["allowed_roles"], ["luna_low", "luna_medium"])
            cache = json.loads((Path(directory) / selector.CACHE_NAMESPACE / "worker-last-good.json").read_bytes())
            self.assertFalse({"luna", "sol", "sol_views", "routing"}.intersection(cache))

    def test_verified_live_then_cache_are_preferred_to_basic(self):
        with tempfile.TemporaryDirectory() as directory:
            live = self.select(publication_bundle(), directory)
            self.assertTrue(all(route["mode"] == "live" for route in self.routes(live)))
            cached = self.select({}, directory, now=NOW + timedelta(days=1))
            self.assertTrue(all(route["mode"] == "cached" for route in self.routes(cached)))
            for first, second in zip(self.routes(live), self.routes(cached)):
                self.assertEqual(first["selected_role"], second["selected_role"])
                self.assertEqual(second["evidence_scope"], "reference_only")

    def test_basic_daily_reuses_without_fetch_or_writes_and_recovers_next_day(self):
        with tempfile.TemporaryDirectory() as directory:
            first = self.select({}, directory)
            paths = list(Path(directory).rglob("*.json"))
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
            fetch = Mock(return_value=publication_bundle())
            again = self.select(None, directory, live_fetcher=fetch)
            self.assertEqual(first, again)
            fetch.assert_not_called()
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})
            recovered = self.select(None, directory, live_fetcher=fetch, now=NOW + timedelta(days=1))
            self.assertEqual(fetch.call_count, 1)
            self.assertTrue(all(row["mode"] == "live" for row in self.routes(recovered)))

    def test_partial_live_uses_intact_cached_views_and_preserves_them(self):
        with tempfile.TemporaryDirectory() as directory:
            original = self.select(publication_bundle(), directory)
            bundle = publication_bundle()
            del bundle["benchmark_snapshots"]["frontend"]
            partial = self.select(bundle, directory, now=NOW + timedelta(days=1))
            routes = partial["routing"]["sol"]["views"]
            self.assertEqual(routes["backend"]["mode"], "live")
            self.assertEqual(routes["reasoning"]["mode"], "live")
            self.assertEqual(routes["frontend"]["mode"], "cached")
            self.assertEqual(routes["general"]["mode"], "cached")
            self.assertTrue(partial["sol"]["fallback"])
            self.assertFalse(partial["sol"]["views"]["backend"]["fallback"])
            self.assertTrue(partial["sol"]["views"]["general"]["fallback"])
            self.assertEqual(partial["sol"]["views"]["general"]["selected_score"], original["sol"]["views"]["general"]["selected_score"])
            self.assertTrue(selector._worker_record_valid(partial))
            next_day = self.select({}, directory, now=NOW + timedelta(days=2))
            self.assertTrue(all(row["mode"] == "cached" for row in self.routes(next_day)))

    def test_partial_live_without_cache_has_basic_only_for_missing_views(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = publication_bundle()
            del bundle["benchmark_snapshots"]["frontend"]
            result = self.select(bundle, directory)
            routes = result["routing"]["sol"]["views"]
            self.assertEqual(routes["frontend"]["mode"], "basic")
            self.assertEqual(routes["general"]["mode"], "basic")
            self.assertEqual(routes["backend"]["mode"], "live")
            self.assertEqual(routes["reasoning"]["mode"], "live")
            self.assertEqual(result["routing"]["luna"]["mode"], "live")

    def test_bad_publication_stays_rejected_while_basic_has_no_reference_claim(self):
        for mutation in ("hash", "batch", "missing", "score"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                bundle = publication_bundle()
                if mutation == "hash":
                    bundle["full_snapshot"]["batch_sha256"] = "sha256:" + "0" * 64
                elif mutation == "batch":
                    bundle["api"]["batch"]["id"] = "different-batch"
                elif mutation == "missing":
                    del bundle["full_snapshot"]
                else:
                    for row in bundle["api"]["rankings"]:
                        row["score"] += 1
                result = self.select(bundle, directory)
                self.assertEqual(result["luna"]["status"], "unavailable")
                self.assertEqual(result["routing"]["luna"]["mode"], "basic")
                self.assertNotIn("selected_role", result["routing"]["luna"])

    def test_forged_basic_roles_modes_and_malformed_views_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            valid = self.select({}, directory)
            mutations = []
            bad = copy.deepcopy(valid); bad["routing"]["luna"]["allowed_roles"].append("sol_max"); mutations.append(bad)
            bad = copy.deepcopy(valid); bad["routing"]["luna"]["selected_role"] = "luna_max"; mutations.append(bad)
            bad = copy.deepcopy(valid); bad["routing"]["luna"]["mode"] = "live"; mutations.append(bad)
            bad = copy.deepcopy(valid); bad["routing"]["policy_version"] = True; mutations.append(bad)
            bad = copy.deepcopy(valid); bad["routing"]["luna"]["host_check_required"] = 1; mutations.append(bad)
            for views in ([], {"general": "invalid"}, {"general": {"status": "ready", "selected_role": "sol_max"}}):
                bad = copy.deepcopy(valid); bad["sol"]["views"] = views; mutations.append(bad)
            for bad in mutations:
                self.assertFalse(selector._worker_record_valid(selector._seal_cache(bad)))

    def test_prior_verified_daily_gains_routing_without_rewriting_history(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.select(publication_bundle(), directory)
            result.pop("routing")
            path = Path(directory) / selector.CACHE_NAMESPACE / "worker-profile.json"
            path.write_bytes(json.dumps(selector._seal_cache(result)).encode())
            before = (path.read_bytes(), path.stat().st_mtime_ns)
            after = self.select(None, directory, live_fetcher=Mock(side_effect=AssertionError("no refetch")))
            self.assertTrue(all(row["mode"] == "live" for row in self.routes(after)))
            self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns))

    def test_empty_or_unknown_capability_set_does_not_create_basic_roles(self):
        with tempfile.TemporaryDirectory() as directory:
            for efforts in ([], ["ultra"]):
                with self.assertRaises(selector.SelectionUnavailable):
                    self.select({}, directory, supported_sol=efforts)
            self.assertFalse(list(Path(directory).rglob("*.json")))

    def test_cli_outage_returns_explicit_basic_success_not_reference_success(self):
        with tempfile.TemporaryDirectory() as directory, patch("src.selector.fetch_worker_data", return_value={}):
            stream = io.StringIO()
            with redirect_stdout(stream):
                result = selector.main(["--workers", "--ensure-daily", "--print-selection", "--state-dir", directory])
            self.assertEqual(result, 0)
            profile = json.loads(stream.getvalue())
            self.assertEqual(profile["luna"]["status"], "unavailable")
            self.assertEqual(profile["routing"]["luna"]["mode"], "basic")

    def test_status_reports_basic_as_degraded_without_native_pass_and_is_read_only(self):
        validation = Path(__file__).resolve().parents[1] / ".tmp/installer-validation/basic-routing"
        validation.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=validation) as directory:
            target = Path(directory) / ".codex"
            install(target, allow_validation_sandbox=True)
            state = target / "sol-luna-v4/state"
            self.select({}, state)
            paths = [p for p in Path(directory).rglob("*") if p.is_file()]
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
            with patch("src.selector._fetch_bytes", side_effect=AssertionError("read-only")):
                status = selector.read_status(codex_home=target, state_dir=state, now=NOW)
            self.assertEqual(status["health"], "Degraded")
            self.assertIn("SOL_BASIC_ROUTING_ACTIVE", status["reason_codes"])
            self.assertIn("LUNA_BASIC_ROUTING_ACTIVE", status["reason_codes"])
            self.assertTrue(status["selection_initialized"])
            self.assertEqual(status["selected_role"], "Not selected")
            self.assertEqual(status["routing"]["luna"]["mode"], "basic")
            self.assertEqual(status["native_delegation"], "Not checked")
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})
            (target / "agents/sol-high.toml").write_bytes(b"invalid")
            broken = selector.read_status(codex_home=target, state_dir=state, now=NOW)
            self.assertEqual(broken["health"], "Misconfigured")

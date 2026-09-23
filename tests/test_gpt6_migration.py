"""GPT-6 generation, publication integrity, and exact historical upgrade gates."""
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from src import selector, worker_selector
from test_reference_runtime import indexed_fixture, NOW
from test_installer_lifecycle import (
    sandbox, simulate_published_v420_install, installation_hash, call_install,
    dry_run_install, rollback, ROOT, FIXED_TIME, InstallerError,
)


FIXTURES = ROOT / "fixtures" / "modeldial-gpt6"


def api_fixture():
    return json.loads((FIXTURES / "reference-api-v1.1.json").read_bytes())


class GenerationCacheTests(unittest.TestCase):
    def test_luna_only_lkg_corruption_rejected_by_both_selectors(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = json.loads((FIXTURES / "complete.json").read_bytes())
            selector.ensure_daily_profile(snapshot, state_dir=directory, now=NOW)
            path = Path(directory) / selector.CACHE_NAMESPACE / "last-good-profile.json"
            record = json.loads(path.read_bytes())
            record["snapshot"]["scores"]["max"] = 100
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(selector.SelectionUnavailable):
                selector.ensure_daily_profile(None, state_dir=directory, now=NOW + timedelta(days=1))
            worker = selector.ensure_worker_profile({}, state_dir=directory, now=NOW + timedelta(days=1))
            self.assertEqual(worker["luna"]["status"], "unavailable")

    def test_old_generation_and_unbound_lkg_cannot_authorize_workers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = json.loads((ROOT / "fixtures/modeldial/complete.json").read_bytes())
            for name in ("daily-profile.json", "last-good-profile.json", "worker-profile.json", "worker-last-good.json"):
                (root / name).write_text(json.dumps({"snapshot": old}), encoding="utf-8")
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.iterdir()}
            selected = selector.ensure_worker_profile({}, state_dir=root, now=NOW)
            self.assertEqual([selected[f]["status"] for f in ("sol", "luna")], ["unavailable"] * 2)
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})
            # Even copying old canonical scores into the new namespace is invalid.
            old_normalized = {"snapshot_id": "old", "published_at": NOW.isoformat(), "scores": dict.fromkeys(selector.EFFORTS, 90)}
            with self.assertRaises(selector.SnapshotInvalid):
                selector.validate_snapshot(old_normalized)

    def test_same_generation_fallback_and_repeat_have_no_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = selector.ensure_worker_profile({"api": api_fixture()}, state_dir=root, now=NOW)
            second = selector.ensure_worker_profile({}, state_dir=root, now=NOW + timedelta(days=1))
            self.assertTrue(second["sol"]["fallback"])
            self.assertEqual(second["sol"]["model"], "gpt-6-sol")
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in root.rglob("*") if p.is_file()}
            fetch = Mock(side_effect=AssertionError("repeat must not fetch"))
            again = selector.ensure_worker_profile(state_dir=root, now=NOW + timedelta(days=1), live_fetcher=fetch)
            self.assertEqual(again, second)
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})
            self.assertFalse(first["sol"]["fallback"])

    def test_luna_same_generation_fallback_requires_model_axis_and_policy(self):
        for field, value in (("models", {"sol": "gpt-5.6-sol", "luna": "gpt-5.6-luna"}), ("luna_axis", ["overallRankings", "overallScore"]), ("policy_version", 1)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                api, _, _ = indexed_fixture()
                first = selector.ensure_worker_profile({"api": api}, state_dir=directory, now=NOW)
                self.assertEqual(first["luna"]["model"], "gpt-6-luna")
                root = Path(directory) / selector.CACHE_NAMESPACE
                for name in ("worker-profile.json", "worker-last-good.json"):
                    payload = json.loads((root / name).read_bytes())
                    payload["cache_identity"][field] = value
                    (root / name).write_text(json.dumps(selector._seal_cache(payload)), encoding="utf-8")
                rejected = selector.ensure_worker_profile({}, state_dir=directory, now=NOW)
                self.assertEqual(rejected["luna"]["status"], "unavailable")
                self.assertEqual(rejected["sol"]["status"], "unavailable")

    def test_cache_body_corruption_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            api, _, _ = indexed_fixture()
            selector.ensure_worker_profile({"api": api}, state_dir=directory, now=NOW)
            root = Path(directory) / selector.CACHE_NAMESPACE
            for name in ("worker-profile.json", "worker-last-good.json"):
                payload = json.loads((root / name).read_bytes())
                payload["luna"]["model"] = "gpt-5.6-luna"
                (root / name).write_text(json.dumps(payload), encoding="utf-8")
            rejected = selector.ensure_worker_profile({}, state_dir=directory, now=NOW)
            self.assertEqual(rejected["luna"]["status"], "unavailable")

    def test_historical_model_rows_rejected_by_both_adapters(self):
        old = json.loads((ROOT / "fixtures/modeldial/reference-api-v1.1.json").read_bytes())
        with self.assertRaises(selector.SnapshotInvalid):
            selector.adapt_modeldial_api(old, now=NOW, allow_reference=True)
        selected = worker_selector.select_sol(worker_selector.adapt_sol_api(old))
        self.assertEqual(selected["status"], "unavailable")


class PublicationIntegrityTests(unittest.TestCase):
    def test_archive_failure_can_only_use_qualified_cache(self):
        for failure in ("offline", "corrupt", "other_batch"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                api, index, full = indexed_fixture()
                replies = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(index).encode(), selector.MODELDIAL_INDEX_URL)]
                if failure == "offline":
                    replies.append(OSError("404"))
                else:
                    full["batch_id"] = "another-batch" if failure == "other_batch" else full["batch_id"]
                    if failure == "corrupt":
                        full["entries"][0]["score"] += 1
                    else:
                        full["batch_sha256"] = worker_selector.full_snapshot_hash(full)
                    replies.append((json.dumps(full).encode(), index["snapshots"][0]["fullSnapshotUrl"]))
                with patch("src.selector._fetch_bytes", side_effect=replies) as fetch:
                    data = selector.fetch_worker_data()
                self.assertEqual(fetch.call_count, 3)
                self.assertEqual(data, {"full_snapshot_status": "unavailable_or_mismatched"})
                empty = selector.ensure_worker_profile(data, state_dir=directory, now=NOW)
                self.assertEqual([empty[f]["status"] for f in ("sol", "luna")], ["unavailable"] * 2)
                selector.ensure_worker_profile({"api": api}, state_dir=directory, now=NOW, refresh=True)
                cached = selector.ensure_worker_profile(data, state_dir=directory, now=NOW + timedelta(days=1))
                self.assertTrue(cached["luna"]["fallback"])

    def test_full_snapshot_body_must_match_publisher_canonical_hash(self):
        full = json.loads((FIXTURES / "reference-full-snapshot.json").read_bytes())
        worker_selector.require_full_snapshot_hash(full)
        full["entries"][0]["score"] += 1
        with self.assertRaises(ValueError):
            worker_selector.adapt_sol_full_snapshot(full)
        with self.assertRaises(selector.SnapshotInvalid):
            selector.adapt_modeldial_snapshot(full, now=NOW, allow_reference=True)

    def test_protocol_index_mismatch_cannot_authorize_api_quality(self):
        for field in ("sha256", "graderVersion", "questionPackVersion", "scoreBaselineId", "evaluationProfile", "pricingSnapshotId"):
            with self.subTest(field=field):
                api, index, _ = indexed_fixture()
                index["snapshots"][0][field] = "wrong"
                replies = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(index).encode(), selector.MODELDIAL_INDEX_URL)]
                with patch("src.selector._fetch_bytes", side_effect=replies) as fetch:
                    data = selector.fetch_worker_data()
                self.assertEqual(fetch.call_count, 2)
                self.assertNotIn("api", data)
                self.assertNotIn("luna_snapshot", data)

    def test_uncovered_compact_cost_is_quality_only(self):
        api, _, _ = indexed_fixture()
        for row in api["rankings"]:
            for key in ("costCoverage", "costProtocolId", "pricingSnapshotId"):
                row.pop(key, None)
        luna = selector.adapt_modeldial_api(api, now=NOW, allow_reference=True)
        self.assertNotIn("reference_costs", luna)
        sol = worker_selector.select_sol(worker_selector.adapt_sol_api(api_fixture()))
        self.assertTrue(all(v["selection_mode"] == "quality_only" for v in sol["views"].values()))


class ExactPublishedUpgradeTests(unittest.TestCase):
    def test_v420_stable_upgrade_repeat_and_exact_rollback(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            simulate_published_v420_install(target, "v4.2.0")
            user_file = target / "user-owned.txt"
            user_file.write_bytes(b"preserve user content\n")
            before = installation_hash(target)
            args = dict(project_root=ROOT, generated_at=FIXED_TIME + timedelta(days=1), allow_validation_sandbox=True, source_commit="6" * 40)
            dry = dry_run_install(target, **args)
            self.assertEqual(dry["effective_changes"], 16)
            self.assertEqual(installation_hash(target), before)
            applied = call_install(target, generated_at=args["generated_at"], source_commit=args["source_commit"])
            self.assertEqual(applied["status"], "UPGRADED")
            upgraded = installation_hash(target)
            repeat = call_install(target, source_commit=args["source_commit"])
            self.assertEqual(repeat["effective_changes"], 0)
            self.assertIsNone(repeat["backup"])
            self.assertEqual(installation_hash(target), upgraded)
            recovered = rollback(target, Path(applied["backup"]), project_root=ROOT, allow_validation_sandbox=True)
            self.assertEqual(recovered["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(installation_hash(target), before)

    def test_schema4_model_contract_conflict_has_zero_writes(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            call_install(target)
            path = target / selector.MANIFEST_RELATIVE
            manifest = json.loads(path.read_bytes())
            manifest["model_contract"]["models"]["luna"] = "gpt-5.6-luna"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            before = installation_hash(target)
            for action in (call_install, dry_run_install):
                with self.assertRaises(InstallerError):
                    action(target, **({"allow_validation_sandbox": True} if action is dry_run_install else {}))
                self.assertEqual(installation_hash(target), before)


if __name__ == "__main__":
    unittest.main()

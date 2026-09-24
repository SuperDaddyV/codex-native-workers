"""Explicit reference provenance and batch-index acquisition; no real network."""
import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from src import selector
from publication_fixtures import publication_bundle


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modeldial-gpt6"
NOW = datetime(2026, 9, 12, 23, tzinfo=selector.BJT)


def reference_api():
    payload = json.loads((FIXTURES / "api-complete-v1.1.json").read_text(encoding="utf-8"))
    for name in ("rankings", "overallRankings"):
        for row in payload.get(name, []):
            row["provider"], row["route"] = selector.BENCHMARK_PAIRS[1]
    return payload


def indexed_fixture():
    bundle = publication_bundle(reference_api())
    return bundle["api"], bundle["publication_index"], bundle["full_snapshot"]


class ReferenceRuntimeTests(unittest.TestCase):
    def test_reference_is_explicit_and_legacy_cli_contract_stays_strict(self):
        api = reference_api()
        with self.assertRaises(selector.SnapshotInvalid):
            selector.adapt_modeldial_api(api, now=NOW)
        snapshot = selector.adapt_modeldial_api(api, now=NOW, allow_reference=True)
        self.assertEqual(snapshot["benchmark_route"], "custom_endpoint")
        self.assertEqual(snapshot["evidence_scope"], "reference_only")
        self.assertNotIn("reference_costs", snapshot)
        with tempfile.TemporaryDirectory() as directory:
            profile = selector.ensure_worker_profile(publication_bundle(api), state_dir=directory, now=NOW)
            self.assertEqual(profile["luna"]["status"], "ready")
            self.assertEqual(profile["luna"]["benchmark_provider"], "cloudflare-reference")
            self.assertNotIn("reference_cost_comparison", profile["luna"])

    def test_mixed_or_unknown_routes_do_not_form_one_luna_candidate(self):
        for pair in (("codex", "official_login"), ("unknown", "custom_endpoint")):
            api = reference_api()
            row = next(row for row in api["rankings"] if row["model"] == selector.LUNA_MODEL)
            row["provider"], row["route"] = pair
            with self.subTest(pair=pair), self.assertRaises(selector.SnapshotInvalid):
                selector.adapt_modeldial_api(api, now=NOW, allow_reference=True)

    def test_full_snapshot_preserves_distinct_result_ids_under_one_protocol(self):
        full = json.loads((FIXTURES / "first-party-complete.json").read_text(encoding="utf-8"))
        for index, row in enumerate(full["entries"]):
            row["model_configuration"]["provider_id"], row["model_configuration"]["route_type"] = selector.BENCHMARK_PAIRS[1]
            row["source_evidence_group_id"] = f"result-{index}"
        full["batch_sha256"] = selector._sol_module().full_snapshot_hash(full)
        snapshot = selector.adapt_modeldial_snapshot(full, now=NOW, allow_reference=True)
        self.assertEqual(len(set(snapshot["evidence_ids"].values())), 5)
        self.assertEqual(snapshot["benchmark_route"], "custom_endpoint")
        self.assertNotIn("reference_costs", snapshot)

    def test_index_selects_matching_batch_not_first_row_or_latest_alias(self):
        api, index, full = indexed_fixture()
        record = index["snapshots"][0]
        unrelated = {**record, "batchId": "older-batch", "fullSnapshotUrl": "https://modeldial.com/old.json"}
        index["snapshots"].insert(0, unrelated)
        replies = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(index).encode(), selector.MODELDIAL_INDEX_URL), (json.dumps(full).encode(), record["fullSnapshotUrl"]), OSError("benchmark index offline")]
        with patch("src.selector._fetch_bytes", side_effect=replies) as fetch:
            data = selector.fetch_worker_data()
        self.assertEqual(fetch.call_args_list[2].args[0], record["fullSnapshotUrl"])
        self.assertEqual(data["full_snapshot_status"], "matched")
        self.assertEqual(data["full_snapshot"]["batch_id"], api["batch"]["id"])

    def test_missing_archive_rejects_api_without_fetching_older_full(self):
        api, index, _ = indexed_fixture()
        replies = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(index).encode(), selector.MODELDIAL_INDEX_URL), OSError("404")]
        with patch("src.selector._fetch_bytes", side_effect=replies) as fetch:
            data = selector.fetch_worker_data()
        self.assertEqual(fetch.call_count, 3)
        self.assertNotIn("full_snapshot", data)
        self.assertNotIn("luna_snapshot", data)
        self.assertNotIn("api", data)
        self.assertEqual(data["full_snapshot_status"], "unavailable_or_mismatched")

    def test_duplicate_or_mismatched_index_is_rejected_before_archive_fetch(self):
        api, index, _ = indexed_fixture()
        for mode in ("duplicate", "pricing", "hash", "count", "unsafe-url"):
            changed = copy.deepcopy(index)
            row = changed["snapshots"][0]
            if mode == "duplicate":
                changed["snapshots"].append(copy.deepcopy(row))
            elif mode == "unsafe-url":
                row["fullSnapshotUrl"] = "https://invalid.example/snapshot.json"
            else:
                key = {"pricing": "pricingSnapshotId", "hash": "sha256", "count": "entryCount"}[mode]
                row[key] = "mismatch"
            with self.subTest(mode=mode), self.assertRaises(selector.SnapshotInvalid):
                selector._matching_snapshot_record(api, changed)

    def test_full_metadata_mismatch_is_not_joined_to_api(self):
        api, index, full = indexed_fixture()
        full["batch_id"] = "previous-day"
        replies = [(json.dumps(api).encode(), selector.MODELDIAL_API_URL), (json.dumps(index).encode(), selector.MODELDIAL_INDEX_URL), (json.dumps(full).encode(), index["snapshots"][0]["fullSnapshotUrl"])]
        with patch("src.selector._fetch_bytes", side_effect=replies):
            data = selector.fetch_worker_data()
        self.assertNotIn("full_snapshot", data)
        self.assertNotIn("luna_snapshot", data)
        self.assertNotIn("api", data)

    def test_old_worker_policy_cache_is_reselected(self):
        with tempfile.TemporaryDirectory() as directory:
            first = selector.ensure_worker_profile(publication_bundle(reference_api()), state_dir=directory, now=NOW)
            first.pop("reference_policy_version")
            path = Path(directory) / "gpt6-v4" / "worker-profile.json"
            path.write_text(json.dumps(first), encoding="utf-8")
            next_profile = selector.ensure_worker_profile({}, state_dir=directory, now=NOW)
            self.assertEqual(next_profile["reference_policy_version"], 2)
            self.assertTrue(next_profile["luna"]["fallback"])
            self.assertEqual(next_profile["luna"]["benchmark_route"], "custom_endpoint")

    def test_cached_reference_cannot_be_relabeled_as_native_route(self):
        with tempfile.TemporaryDirectory() as directory:
            first = selector.ensure_worker_profile(publication_bundle(reference_api()), state_dir=directory, now=NOW)
            first["luna"]["benchmark_route"] = "official_login"
            path = Path(directory) / "gpt6-v4" / "worker-profile.json"
            path.write_text(json.dumps(first), encoding="utf-8")
            repaired = selector.ensure_worker_profile({}, state_dir=directory, now=NOW)
            self.assertEqual(repaired["luna"]["benchmark_route"], "custom_endpoint")
            self.assertTrue(repaired["luna"]["fallback"])


if __name__ == "__main__":
    unittest.main()

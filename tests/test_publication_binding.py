"""Publication rows and all four Sol views must be backed by exact archives."""
import copy
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from src import selector, worker_selector
from publication_fixtures import publication_bundle, transport, digest


NOW = datetime(2026, 9, 12, 23, tzinfo=selector.BJT)


def select(bundle):
    with tempfile.TemporaryDirectory() as directory:
        return selector.ensure_worker_profile(bundle, state_dir=directory, now=NOW)


class PublicationBindingTests(unittest.TestCase):
    def test_verified_publication_enables_both_families_and_all_views(self):
        bundle = publication_bundle()
        payloads, fetch = transport(bundle)
        with patch("src.selector._fetch_bytes", side_effect=fetch) as call:
            profile = select(selector.fetch_worker_data())
        self.assertEqual(call.call_count, 7)
        self.assertEqual(len(payloads), 7)
        self.assertEqual(profile["luna"]["selected_role"], "luna_xhigh")
        self.assertEqual(profile["sol"]["views"]["backend"]["selected_role"], "sol_high")
        self.assertEqual(profile["sol"]["views"]["backend"]["selection_mode"], "cost_optimized")
        self.assertTrue(all(v["status"] == "ready" for v in profile["sol"]["views"].values()))

    def test_backend_score_mismatch_cannot_downgrade_to_quality_only(self):
        for model in ("gpt-6-sol", "gpt-6-luna"):
            with self.subTest(model=model):
                bundle = publication_bundle()
                row = next(r for r in bundle["api"]["rankings"] if r["model"] == model and r["reasoningEffort"] == "low")
                row["score"] = row["backendScore"] = 100
                profile = select(bundle)
                if model.endswith("sol"):
                    self.assertEqual(profile["sol"]["views"]["backend"]["status"], "unavailable")
                    self.assertEqual(profile["sol"]["views"]["general"]["status"], "unavailable")
                    self.assertEqual(profile["sol"]["views"]["frontend"]["status"], "ready")
                    self.assertEqual(profile["luna"]["status"], "ready")
                else:
                    self.assertEqual(profile["luna"]["status"], "unavailable")
                    self.assertEqual(profile["sol"]["status"], "ready")

    def test_backend_identity_scale_and_latency_are_bound(self):
        for key, value in (("provider", "codex"), ("route", "official_login"), ("id", "other-row"), ("maxScore", 101), ("elapsedMs", 1)):
            with self.subTest(key=key):
                bundle = publication_bundle()
                row = next(r for r in bundle["api"]["rankings"] if r["model"] == "gpt-6-sol")
                row[key] = value
                self.assertEqual(select(bundle)["sol"]["views"]["backend"]["status"], "unavailable")

    def test_unknown_axis_batch_is_not_fetched_and_does_not_authorize_view(self):
        bundle = publication_bundle()
        bundle["api"]["overallBatch"]["sources"]["frontend"]["batchId"] = "unpublished-batch"
        _, fetch = transport(bundle)
        with patch("src.selector._fetch_bytes", side_effect=fetch) as call:
            profile = select(selector.fetch_worker_data())
        self.assertEqual(call.call_count, 6)
        views = profile["sol"]["views"]
        self.assertEqual([views[v]["status"] for v in ("general", "frontend", "reasoning", "backend")], ["unavailable", "unavailable", "ready", "ready"])

    def test_each_axis_mismatch_is_isolated_to_its_dependents(self):
        for source, field, view in (("frontend", "frontendScore", "frontend"), ("knowledge", "knowledgeScore", "reasoning")):
            for mode in ("api-score", "archive-body", "hash", "missing", "duplicate-index", "protocol"):
                with self.subTest(source=source, mode=mode):
                    bundle = publication_bundle()
                    raw = bundle["benchmark_snapshots"][source]
                    if mode == "api-score":
                        bundle["api"]["overallRankings"][0][field] += 1
                    elif mode == "archive-body":
                        next(iter(raw["axes"].values()))["entries"][0]["max_score"] = 101
                    elif mode == "hash":
                        raw["benchmark_sha256"] = "sha256:" + "0" * 64
                    elif mode == "missing":
                        del bundle["benchmark_snapshots"][source]
                    elif mode == "duplicate-index":
                        record = next(r for r in bundle["benchmark_index"]["snapshots"] if r["batch_id"] == raw["batch_id"])
                        bundle["benchmark_index"]["snapshots"].append(copy.deepcopy(record))
                    else:
                        next(iter(raw["axes"].values()))["status"] = "partial"
                        raw["benchmark_sha256"] = digest(raw, "benchmark_sha256")
                        bundle["api"]["overallBatch"]["sources"][source]["sha256"] = raw["benchmark_sha256"]
                        next(r for r in bundle["benchmark_index"]["snapshots"] if r["batch_id"] == raw["batch_id"])["benchmark_sha256"] = raw["benchmark_sha256"]
                    views = select(bundle)["sol"]["views"]
                    self.assertEqual(views[view]["status"], "unavailable")
                    self.assertEqual(views["general"]["status"], "unavailable")
                    self.assertEqual(views["backend"]["status"], "ready")
                    self.assertEqual(views["reasoning" if view == "frontend" else "frontend"]["status"], "ready")

    def test_overall_hash_scores_sources_and_weights_are_bound(self):
        for mode in ("api-score", "archive-body", "missing", "sources", "weights"):
            with self.subTest(mode=mode):
                bundle = publication_bundle()
                if mode == "api-score":
                    row = bundle["api"]["overallRankings"][0]
                    row["score"] = row["overallScore"] = 100
                elif mode == "archive-body":
                    bundle["benchmark_snapshots"]["overall"]["entries"][0]["overall_score"] = 100
                elif mode == "missing":
                    del bundle["benchmark_snapshots"]["overall"]
                elif mode == "sources":
                    bundle["api"]["overallBatch"]["sources"]["backend"]["batchId"] = "another"
                else:
                    bundle["api"]["weights"] = {"backend": 1, "frontend": 0, "knowledge": 0}
                views = select(bundle)["sol"]["views"]
                self.assertEqual(views["general"]["status"], "unavailable")
                self.assertTrue(all(views[v]["status"] == "ready" for v in ("backend", "frontend", "reasoning")))

    def test_raw_api_cannot_initialize_a_verified_cache(self):
        profile = select({"api": publication_bundle()["api"]})
        self.assertEqual([profile[f]["status"] for f in ("sol", "luna")], ["unavailable"] * 2)

    def test_old_candidate_cache_preserved_and_copied_cache_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = selector.ensure_worker_profile(publication_bundle(), state_dir=root, now=NOW)
            active = root / selector.CACHE_NAMESPACE
            old = root / "gpt6-v3"
            old.mkdir()
            for name in ("worker-profile.json", "worker-last-good.json"):
                record = json.loads((active / name).read_bytes())
                record.pop("publication_verification_version")
                record.pop("content_sha256")
                record["content_sha256"] = hashlib_digest(record)
                raw = json.dumps(record).encode()
                (old / name).write_bytes(raw)
                (active / name).write_bytes(raw)
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in old.iterdir()}
            rejected = selector.ensure_worker_profile({}, state_dir=root, now=NOW)
            self.assertEqual([rejected[f]["status"] for f in ("sol", "luna")], ["unavailable"] * 2)
            self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in old.iterdir()})
            self.assertEqual(valid["publication_verification_version"], 1)

    def test_cli_rejects_raw_api_without_writing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "api.json"
            path.write_text(json.dumps(publication_bundle()["api"]), encoding="utf-8")
            state = Path(directory) / "state"
            with redirect_stdout(StringIO()), patch("src.selector._fetch_bytes", side_effect=AssertionError("offline means no network")):
                result = selector.main(["--workers", "--snapshot", str(path), "--state-dir", str(state)])
            self.assertEqual(result, 3)
            self.assertFalse(state.exists())

    def test_bundle_cannot_supply_prevalidated_choices(self):
        bundle = publication_bundle()
        forged = selector._verified_worker_data(bundle, now=NOW)
        del bundle["publication_index"]
        bundle.update(forged)
        result = select(bundle)
        self.assertEqual([result[f]["status"] for f in ("sol", "luna")], ["unavailable"] * 2)

    def test_missing_comparable_cost_keeps_verified_backend_quality(self):
        bundle = publication_bundle()
        full = bundle["full_snapshot"]
        for row in full["entries"]:
            row["cost_coverage"] = "partial"
        full["batch_sha256"] = digest(full, "batch_sha256", sorted_keys=True)
        bundle["api"]["batch"]["sha256"] = full["batch_sha256"]
        bundle["publication_index"]["snapshots"][0]["sha256"] = full["batch_sha256"]
        backend = select(bundle)["sol"]["views"]["backend"]
        self.assertEqual(backend["status"], "ready")
        self.assertEqual(backend["selection_mode"], "quality_only")
        self.assertEqual(backend["selected_role"], "sol_max")

    def test_api_cost_claims_cannot_become_luna_cost_evidence(self):
        bundle = publication_bundle()
        for row in bundle["api"]["rankings"]:
            row.update(costCoverage="complete", costProtocolId=bundle["api"]["batch"]["scoreBaselineId"], pricingSnapshotId=bundle["api"]["batch"]["pricingSnapshotId"], estimatedReferenceCostUsd=0.001)
        self.assertNotIn("reference_cost_comparison", select(bundle)["luna"])

    def test_benchmark_index_transport_failure_keeps_verified_backend(self):
        bundle = publication_bundle()
        payloads, fetch = transport(bundle)
        payloads[selector.MODELDIAL_BENCHMARK_INDEX_URL] = OSError("offline")
        with patch("src.selector._fetch_bytes", side_effect=fetch) as call:
            result = select(selector.fetch_worker_data())
        self.assertEqual(call.call_count, 4)
        self.assertEqual(result["luna"]["status"], "ready")
        self.assertEqual(result["sol"]["views"]["backend"]["status"], "ready")
        self.assertTrue(all(result["sol"]["views"][v]["status"] == "unavailable" for v in ("general", "frontend", "reasoning")))

    def test_malformed_axis_sources_leave_verified_backend_available(self):
        for sources in (None, [], "invalid"):
            with self.subTest(sources=sources):
                bundle = publication_bundle()
                bundle["api"]["overallBatch"]["sources"] = sources
                result = select(bundle)
                self.assertEqual(result["luna"]["status"], "ready")
                self.assertEqual(result["sol"]["views"]["backend"]["status"], "ready")
                self.assertTrue(all(result["sol"]["views"][v]["status"] == "unavailable" for v in ("general", "frontend", "reasoning")))

    def test_ordered_hash_covers_unicode_and_rejects_sorted_serialization(self):
        payload = {"z": "中文", "a": 1}
        self.assertEqual(worker_selector.benchmark_snapshot_hash(payload, "benchmark_sha256"), digest(payload, "benchmark_sha256"))
        self.assertNotEqual(worker_selector.benchmark_snapshot_hash(payload, "benchmark_sha256"), digest(payload, "benchmark_sha256", sorted_keys=True))

    def test_verified_fallback_and_repeat_preserve_state(self):
        with tempfile.TemporaryDirectory() as directory:
            selector.ensure_worker_profile(publication_bundle(), state_dir=directory, now=NOW)
            next_day = selector.ensure_worker_profile({}, state_dir=directory, now=NOW + timedelta(days=1))
            self.assertTrue(all(next_day[f]["fallback"] for f in ("sol", "luna")))
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in Path(directory).rglob("*") if p.is_file()}
            self.assertEqual(next_day, selector.ensure_worker_profile({}, state_dir=directory, now=NOW + timedelta(days=1)))
            self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before})

    def test_benchmark_archive_paths_cannot_escape_inventory_root(self):
        for path in ("../other.json", "https://example.com/evil.json", "//modeldial.com/archive/a.json", "archive/%2e%2e/a.json", "archive/a.json?x=y"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                selector._benchmark_archive_url(path)


def hashlib_digest(record):
    import hashlib
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

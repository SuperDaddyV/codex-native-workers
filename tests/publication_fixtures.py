"""Synthetic, internally consistent publications; never native/live evidence."""
import copy
import hashlib
import json
from pathlib import Path

from src import selector


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/modeldial-gpt6"


def digest(payload, field, *, sorted_keys=False):
    body = {k: v for k, v in payload.items() if k != field}
    return "sha256:" + hashlib.sha256(json.dumps(body, sort_keys=sorted_keys, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def publication_bundle(api=None, *, include_luna=True):
    if api is None:
        api = json.loads((FIXTURES / "reference-api-v1.1.json").read_bytes())
        if include_luna:
            other = json.loads((FIXTURES / "api-complete-v1.1.json").read_bytes())
            for row in other["rankings"]:
                if row["model"] == "gpt-6-luna":
                    row.update(provider="cloudflare-reference", route="custom_endpoint")
                    api["rankings"].append(row)
    api = copy.deepcopy(api)
    for group in ("rankings", "overallRankings"):
        for row in api[group]:
            row["id"] = f"{row['provider']}:{row['model']}:{row['reasoningEffort']}"
    api.setdefault("weights", {"backend": 0.4, "frontend": 0.3, "knowledge": 0.3})
    batch = api["batch"]
    batch["entryCount"] = len(api["rankings"])
    full = {
        "schema_version": 1, "kind": "first_party_snapshot", "status": "complete",
        "batch_id": batch["id"], "published_at": batch["publishedAt"],
        "revision": batch["revision"], "question_pack_id": batch.get("questionPackId", "worker-pack-id-v1"),
        "question_pack_version": batch["questionPackVersion"], "grader_version": batch["graderVersion"],
        "evaluation_profile": batch["evaluationProfile"], "score_baseline_id": batch["scoreBaselineId"],
        "pricing_snapshot_id": batch["pricingSnapshotId"], "entry_count": batch["entryCount"],
        "provenance": {"public_official_snapshot": True}, "entries": [],
    }
    costs = {"low": 0.5, "medium": 0.7, "high": 1.0, "xhigh": 1.5, "max": 2.0}
    for row in api["rankings"]:
        full["entries"].append({
            "model_configuration_id": row["id"],
            "model_configuration": {"canonical_model_id": row["model"], "provider_id": row["provider"], "route_type": row["route"], "reasoning_effort": row["reasoningEffort"]},
            "advisor_eligible": True, "score_integrity": "first_party_controlled", "route_identity": "first_party_controlled",
            "source_evidence_group_id": "synthetic-" + row["id"], "score": row["score"], "max_score": row["maxScore"],
            "elapsed_ms": row["elapsedMs"], "cost_coverage": "complete", "estimated_api_cost_usd": costs[row["reasoningEffort"]],
        })
    full["batch_sha256"] = digest(full, "batch_sha256", sorted_keys=True)
    batch["sha256"] = full["batch_sha256"]
    record = {"batchId": batch["id"], **{k: v for k, v in batch.items() if k != "id"}, "fullSnapshotUrl": "https://modeldial.com/data/reference-snapshots/archive/synthetic-backend.json"}
    index = {"schemaVersion": "1.1", "snapshots": [record]}
    overall = api["overallBatch"]
    overall["sources"]["backend"] = {"batchId": batch["id"], "publishedAt": batch["publishedAt"], "sha256": batch["sha256"]}
    archives, records = {}, []
    for name, axis, field, raw_field in (("frontend", "frontend_v17", "frontendScore", "total_score"), ("knowledge", "hle_deep_20", "knowledgeScore", "score")):
        source = overall["sources"][name]
        raw = {"schema_version": 1, "kind": "benchmark_axes", "batch_id": source["batchId"], "published_at": source["publishedAt"], "revision": 1, "source_reference_batch_sha256": batch["sha256"], "axes": {axis: {
            "benchmark_ref": "synthetic-protocol-v1", "status": "complete", "score_scale": 100,
            "entries": [{"candidate_id": row["id"], "connection_id": row["provider"], "model_id": row["model"], "reasoning_effort": row["reasoningEffort"], raw_field: row[field], "max_score": row["maxScore"]} for row in api["overallRankings"]],
        }}}
        raw["benchmark_sha256"] = digest(raw, "benchmark_sha256")
        source["sha256"] = raw["benchmark_sha256"]
        records.append({key: raw[key] for key in ("batch_id", "published_at", "revision", "source_reference_batch_sha256", "benchmark_sha256")})
        records[-1].update(axes=[axis], path=f"archive/synthetic-{name}.json")
        archives[name] = raw
    overall["entryCount"] = len(api["overallRankings"])
    raw = {"schema_version": 1, "kind": "overall_capability_ranking", "batch_id": overall["id"], "published_at": overall["publishedAt"], "weights": api["weights"],
           "sources": {name: {"batch_id": source["batchId"], "published_at": source["publishedAt"], "sha256": source["sha256"]} for name, source in overall["sources"].items()}, "entry_count": overall["entryCount"], "entries": []}
    for row in api["overallRankings"]:
        raw["entries"].append({"candidate_id": row["id"], "connection_id": row["provider"], "model_id": row["model"], "reasoning_effort": row["reasoningEffort"], **{dest: row[src] for src, dest in (("backendScore", "backend_score"), ("frontendScore", "frontend_score"), ("knowledgeScore", "knowledge_score"), ("overallScore", "overall_score"))}})
    raw["overall_sha256"] = digest(raw, "overall_sha256")
    overall["sha256"] = raw["overall_sha256"]
    archives["overall"] = raw
    benchmark_index = {"schema_version": 1, "kind": "benchmark_axes", "snapshots": records, "overall": {key: raw[key] for key in ("batch_id", "published_at", "overall_sha256", "entry_count")}}
    benchmark_index["overall"]["path"] = "overall/archive/synthetic-overall.json"
    return {"api": api, "publication_index": index, "full_snapshot": full, "benchmark_index": benchmark_index, "benchmark_snapshots": archives}


def transport(bundle):
    payloads = {selector.MODELDIAL_API_URL: bundle["api"], selector.MODELDIAL_INDEX_URL: bundle["publication_index"], selector.MODELDIAL_BENCHMARK_INDEX_URL: bundle["benchmark_index"], bundle["publication_index"]["snapshots"][0]["fullSnapshotUrl"]: bundle["full_snapshot"]}
    for name, payload in bundle["benchmark_snapshots"].items():
        path = ("overall/" if name == "overall" else "") + f"archive/synthetic-{name}.json"
        payloads[f"https://modeldial.com/data/benchmark-snapshots/{path}"] = payload
    def fetch(url, **kwargs):
        value = payloads[url]
        if isinstance(value, Exception):
            raise value
        return json.dumps(value, ensure_ascii=False).encode(), url
    return payloads, fetch

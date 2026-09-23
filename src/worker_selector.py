"""Pure ModelDial API adapter and Sol effort selector.

The public API's overall, backend, frontend, and knowledge axes have distinct
provenance. This module keeps those groups separate and only optimizes on cost
when the normalized input carries explicit, complete coverage metadata.
"""

from __future__ import annotations

import math
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any


# Single active model/effort contract, shared by both selectors, installer and
# CLI capability probe. Historical fixtures and rollback payloads stay pinned.
VERSION = "v4.3.0"
SOL_MODEL = "gpt-6-sol"
LUNA_MODEL = "gpt-6-luna"
MODEL_BY_FAMILY = {"sol": SOL_MODEL, "luna": LUNA_MODEL}
WORKER_PROFILE_SCHEMA_VERSION = 3
REFERENCE_POLICY_VERSION = 2
CACHE_NAMESPACE = "gpt6-v3"
SOL_PROVIDER = "codex"
SOL_ROUTE = "official_login"
REFERENCE_PROVIDER = "cloudflare-reference"
REFERENCE_ROUTE = "custom_endpoint"
OFFICIAL_BENCHMARK = (SOL_PROVIDER, SOL_ROUTE)
REFERENCE_BENCHMARK = (REFERENCE_PROVIDER, REFERENCE_ROUTE)
BENCHMARK_IDENTITIES = (OFFICIAL_BENCHMARK, REFERENCE_BENCHMARK)
EVIDENCE_SCOPE = "reference_only"
SCHEMA_VERSION = "1.1"
EFFORTS = ("low", "medium", "high", "xhigh", "max")
VIEWS = ("general", "backend", "frontend", "reasoning")
ROLE_BY_EFFORT = {effort: f"sol_{effort}" for effort in EFFORTS}
_SHA256 = re.compile(r"sha256:[0-9a-f]{64}\Z")
_SCORE_FIELDS = {
    "general": ("overallRankings", "overallScore"),
    "backend": ("rankings", "score"),
    "frontend": ("overallRankings", "frontendScore"),
    "reasoning": ("overallRankings", "knowledgeScore"),
}


def cache_identity() -> dict[str, Any]:
    """Return a fresh, exact generation/axis/selection-policy cache binding."""
    return {
        "models": dict(MODEL_BY_FAMILY),
        "efforts": list(EFFORTS),
        "policy_version": REFERENCE_POLICY_VERSION,
        "luna_axis": ["rankings", "score", "backend"],
        "sol_axes": {key: list(value) for key, value in _SCORE_FIELDS.items()},
        "sol_quality_gap": 2.0,
    }


def full_snapshot_hash(payload: Mapping[str, Any]) -> str:
    """ModelDial's published canonical JSON hash (excluding batch_sha256)."""
    body = {key: value for key, value in payload.items() if key != "batch_sha256"}
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def require_full_snapshot_hash(payload: Mapping[str, Any]) -> None:
    if not isinstance(payload, Mapping) or payload.get("batch_sha256") != full_snapshot_hash(payload):
        raise ValueError("ModelDial full snapshot content hash mismatch")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _timestamp(value: Any, name: str) -> str:
    if not _text(value):
        raise ValueError(f"{name} must be a non-empty ISO 8601 timestamp")
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must include a UTC offset")
    return value


def _finite_number(value: Any, *, minimum: float | None = None) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        return None
    return number


def _positive_integer(value: Any, name: str, *, allow_zero: bool = False) -> int:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _sha256(value: Any, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be a sha256 digest")
    return value


def _required_text(mapping: Mapping[str, Any], key: str, name: str) -> str:
    value = mapping.get(key)
    if not _text(value):
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _allowed_benchmark(provider: Any, route: Any) -> bool:
    return (provider, route) in BENCHMARK_IDENTITIES


def _has_complete_effort_set(rows: Any, provider: str, route: str) -> bool:
    if not isinstance(rows, list):
        return False
    efforts: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        if (
            row.get("model") != SOL_MODEL
            or row.get("provider") != provider
            or row.get("route") != route
        ):
            continue
        effort = row.get("reasoningEffort")
        if effort not in EFFORTS:
            continue
        if effort in efforts:
            return False
        efforts.add(effort)
    return efforts == set(EFFORTS)


def _choose_api_benchmark(*row_groups: Any) -> tuple[str, str]:
    for provider, route in BENCHMARK_IDENTITIES:
        if any(_has_complete_effort_set(rows, provider, route) for rows in row_groups):
            return provider, route
    # Public reference rows are a supported benchmark input even when no
    # complete effort set exists; their incomplete views will fail closed.
    return REFERENCE_BENCHMARK


def _choose_full_snapshot_benchmark(entries: Any) -> tuple[str, str]:
    rows: list[dict[str, Any]] = []
    if isinstance(entries, list):
        for entry in entries:
            configuration = entry.get("model_configuration") if isinstance(entry, Mapping) else None
            if not isinstance(configuration, Mapping):
                continue
            rows.append({
                "model": configuration.get("canonical_model_id"),
                "provider": configuration.get("provider_id"),
                "route": configuration.get("route_type"),
                "reasoningEffort": configuration.get("reasoning_effort"),
            })
    for provider, route in BENCHMARK_IDENTITIES:
        if _has_complete_effort_set(rows, provider, route):
            return provider, route
    return REFERENCE_BENCHMARK


def _score_signature(items: Any) -> str | None:
    if not isinstance(items, list) or len(items) != len(EFFORTS):
        return None
    by_effort: dict[str, float | None] = {}
    for item in items:
        if not isinstance(item, Mapping):
            return None
        effort = item.get("effort")
        if effort not in EFFORTS or effort in by_effort:
            return None
        by_effort[effort] = _finite_number(item.get("score"), minimum=0.0)
    if set(by_effort) != set(EFFORTS) or any(value is None for value in by_effort.values()):
        return None
    return "|".join(f"{effort}:{by_effort[effort]!r}" for effort in EFFORTS)


def _normalize_source(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("ModelDial source must be an object")
    if value.get("kind") != "first_party_snapshot":
        raise ValueError("ModelDial source is not first-party")
    return {
        "name": _required_text(value, "name", "source.name"),
        "kind": "first_party_snapshot",
        "methodology_url": _required_text(value, "methodologyUrl", "source.methodologyUrl"),
        "license": _required_text(value, "license", "source.license"),
        "license_url": _required_text(value, "licenseUrl", "source.licenseUrl"),
    }


def _normalize_batch(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("ModelDial batch must be an object")
    return {
        "id": _required_text(value, "id", "batch.id"),
        "revision": _positive_integer(value.get("revision"), "batch.revision"),
        "published_at": _timestamp(value.get("publishedAt"), "batch.publishedAt"),
        "question_pack_id": (
            _required_text(value, "questionPackId", "batch.questionPackId")
            if value.get("questionPackId") is not None else None
        ),
        "question_pack_version": _required_text(value, "questionPackVersion", "batch.questionPackVersion"),
        "grader_version": _required_text(value, "graderVersion", "batch.graderVersion"),
        "evaluation_profile": _required_text(value, "evaluationProfile", "batch.evaluationProfile"),
        "score_baseline_id": _required_text(value, "scoreBaselineId", "batch.scoreBaselineId"),
        "pricing_snapshot_id": _required_text(value, "pricingSnapshotId", "batch.pricingSnapshotId"),
        "entry_count": _positive_integer(value.get("entryCount"), "batch.entryCount", allow_zero=True),
        "sha256": _sha256(value.get("sha256"), "batch.sha256"),
    }


def _normalize_overall_batch(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        return None
    try:
        sources = value.get("sources")
        if not isinstance(sources, Mapping):
            return None
        normalized_sources: dict[str, dict[str, str]] = {}
        for axis in ("backend", "frontend", "knowledge"):
            source = sources.get(axis)
            if not isinstance(source, Mapping):
                return None
            normalized_sources[axis] = {
                "batch_id": _required_text(source, "batchId", f"overallBatch.sources.{axis}.batchId"),
                "published_at": _timestamp(source.get("publishedAt"), f"overallBatch.sources.{axis}.publishedAt"),
                "sha256": _sha256(source.get("sha256"), f"overallBatch.sources.{axis}.sha256"),
            }
        return {
            "id": _required_text(value, "id", "overallBatch.id"),
            "published_at": _timestamp(value.get("publishedAt"), "overallBatch.publishedAt"),
            "sha256": _sha256(value.get("sha256"), "overallBatch.sha256"),
            "entry_count": _positive_integer(value.get("entryCount"), "overallBatch.entryCount"),
            "sources": normalized_sources,
        }
    except ValueError:
        return None


def _unavailable_view(
    reason: str,
    *,
    group_id: str | None = None,
    group_published_at: str | None = None,
    group_sha256: str | None = None,
    source_array: str | None = None,
    score_field: str | None = None,
    source_row_count: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "unavailable", "reason": reason}
    for key, value in (
        ("group_id", group_id),
        ("group_published_at", group_published_at),
        ("group_sha256", group_sha256),
        ("source_array", source_array),
        ("score_field", score_field),
        ("source_row_count", source_row_count),
    ):
        if value is not None:
            result[key] = value
    return result


def _candidate_matches(row: Mapping[str, Any], provider: str, route: str) -> bool:
    return (
        row.get("model") == SOL_MODEL
        and row.get("provider") == provider
        and row.get("route") == route
        and row.get("reasoningEffort") in EFFORTS
    )


def _build_api_view(
    rows: Any,
    *,
    group_id: str,
    group_published_at: str,
    group_sha256: str,
    source_array: str,
    score_field: str,
    source_row_count: int,
    provider: str,
    route: str,
    required_score_basis: str | None = None,
) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) != source_row_count:
        return _unavailable_view(
            "source_row_count_mismatch",
            group_id=group_id,
            group_published_at=group_published_at,
            group_sha256=group_sha256,
            source_array=source_array,
            score_field=score_field,
            source_row_count=source_row_count,
        )

    selected: dict[str, Mapping[str, Any]] = {}
    identifiers: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or not _candidate_matches(row, provider, route):
            continue
        effort = row.get("reasoningEffort")
        if effort in selected:
            return _unavailable_view(
                f"duplicate_effort:{effort}", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        row_id = row.get("id")
        if not _text(row_id) or row_id in identifiers:
            return _unavailable_view(
                "missing_or_duplicate_row_id", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        identifiers.add(row_id)
        selected[effort] = row

    if set(selected) != set(EFFORTS):
        missing = ",".join(effort for effort in EFFORTS if effort not in selected)
        return _unavailable_view(
            f"incomplete_efforts:{missing}", group_id=group_id,
            group_published_at=group_published_at, group_sha256=group_sha256,
            source_array=source_array, score_field=score_field,
            source_row_count=source_row_count,
        )

    items: list[dict[str, Any]] = []
    common_max_score: float | None = None
    for effort in EFFORTS:
        row = selected[effort]
        if required_score_basis is not None and row.get("scoreBasis") != required_score_basis:
            return _unavailable_view(
                f"score_basis_mismatch:{effort}", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        rank = _positive_integer(row.get("rank"), f"{source_array}.{effort}.rank") if _valid_positive_int(row.get("rank")) else None
        backend_rank = _positive_integer(row.get("backendRank"), f"{source_array}.{effort}.backendRank") if _valid_positive_int(row.get("backendRank")) else None
        if rank is None or backend_rank is None:
            return _unavailable_view(
                f"invalid_rank:{effort}", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        max_score = _finite_number(row.get("maxScore"), minimum=0.0)
        score = _finite_number(row.get(score_field), minimum=0.0)
        elapsed_ms = _finite_number(row.get("elapsedMs"), minimum=0.0)
        if (
            max_score is None or max_score <= 0.0 or score is None
            or score > max_score or elapsed_ms is None
        ):
            return _unavailable_view(
                f"invalid_score_or_elapsed:{effort}", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        if common_max_score is None:
            common_max_score = max_score
        elif max_score != common_max_score:
            return _unavailable_view(
                "max_score_mismatch", group_id=group_id,
                group_published_at=group_published_at, group_sha256=group_sha256,
                source_array=source_array, score_field=score_field,
                source_row_count=source_row_count,
            )
        if required_score_basis == "overall":
            raw_score = _finite_number(row.get("score"), minimum=0.0)
            if raw_score is None or raw_score != score:
                return _unavailable_view(
                    f"overall_score_identity_mismatch:{effort}", group_id=group_id,
                    group_published_at=group_published_at, group_sha256=group_sha256,
                    source_array=source_array, score_field=score_field,
                    source_row_count=source_row_count,
                )
        elif required_score_basis == "backend":
            backend_score = _finite_number(row.get("backendScore"), minimum=0.0)
            if backend_score is None or backend_score != score:
                return _unavailable_view(
                    f"backend_score_identity_mismatch:{effort}", group_id=group_id,
                    group_published_at=group_published_at, group_sha256=group_sha256,
                    source_array=source_array, score_field=score_field,
                    source_row_count=source_row_count,
                )
        observed_cost = _finite_number(row.get("estimatedReferenceCostUsd"), minimum=0.0)
        items.append({
            "effort": effort,
            "score": score,
            "max_score": max_score,
            "score_field": score_field,
            "score_basis": row.get("scoreBasis"),
            "score_group_id": group_id,
            "score_source_array": source_array,
            "provider": provider,
            "model": SOL_MODEL,
            "route": route,
            "row_id": row["id"],
            "rank": rank,
            "backend_rank": backend_rank,
            "elapsed_ms": elapsed_ms,
            # Retained as an observation only. The public v1.1 schema does not
            # attest complete matching cost coverage for any of its views.
            "estimated_reference_cost_usd": observed_cost,
        })

    return {
        "status": "ready",
        "group_id": group_id,
        "group_published_at": group_published_at,
        "group_sha256": group_sha256,
        "source_array": source_array,
        "score_field": score_field,
        "source_row_count": source_row_count,
        "items": items,
    }


def _valid_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def adapt_sol_api(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a ModelDial Public Radar API v1.1 response for Sol.

    This function performs no network, filesystem, or clock access. Unsupported
    schemas and malformed root provenance raise ``ValueError``. A missing or
    invalid individual axis is represented as an unavailable view so one axis
    cannot lend scores or costs to another.
    """

    if not isinstance(payload, Mapping):
        raise ValueError("ModelDial API response must be an object")
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("ModelDial API schemaVersion is unsupported")
    if payload.get("defaultRanking") != "overallRankings":
        raise ValueError("ModelDial API defaultRanking is unsupported")
    generated_at = _timestamp(payload.get("generatedAt"), "generatedAt")
    source = _normalize_source(payload.get("source"))
    batch = _normalize_batch(payload.get("batch"))

    overall_batch = _normalize_overall_batch(payload.get("overallBatch"))
    overall_rows = payload.get("overallRankings")
    if not isinstance(overall_rows, list):
        overall_issue = "overall_rankings_missing_or_invalid"
    elif overall_batch is None:
        overall_issue = "overall_batch_missing_or_invalid"
    elif len(overall_rows) != overall_batch["entry_count"]:
        overall_issue = "overall_entry_count_mismatch"
    else:
        overall_issue = None

    backend_rows = payload.get("rankings")
    if not isinstance(backend_rows, list):
        backend_issue = "rankings_missing_or_invalid"
    elif len(backend_rows) != batch["entry_count"]:
        backend_issue = "entry_count_mismatch"
    else:
        backend_issue = None

    benchmark_provider, benchmark_route = _choose_api_benchmark(overall_rows, backend_rows)

    views: dict[str, dict[str, Any]] = {}
    if overall_issue:
        for view_name in ("general", "frontend", "reasoning"):
            source_array, score_field = _SCORE_FIELDS[view_name]
            views[view_name] = _unavailable_view(
                overall_issue, source_array=source_array, score_field=score_field,
                source_row_count=len(overall_rows) if isinstance(overall_rows, list) else None,
            )
    else:
        assert overall_batch is not None and isinstance(overall_rows, list)
        for view_name, source_axis, score_basis in (
            ("general", None, "overall"),
            ("frontend", "frontend", None),
            ("reasoning", "knowledge", None),
        ):
            source_array, score_field = _SCORE_FIELDS[view_name]
            if source_axis is None:
                group_id = overall_batch["id"]
                published_at = overall_batch["published_at"]
                group_hash = overall_batch["sha256"]
            else:
                axis_source = overall_batch["sources"][source_axis]
                group_id = axis_source["batch_id"]
                published_at = axis_source["published_at"]
                group_hash = axis_source["sha256"]
            views[view_name] = _build_api_view(
                overall_rows,
                group_id=group_id,
                group_published_at=published_at,
                group_sha256=group_hash,
                source_array=source_array,
                score_field=score_field,
                source_row_count=overall_batch["entry_count"],
                provider=benchmark_provider,
                route=benchmark_route,
                required_score_basis=score_basis,
            )

    if backend_issue:
        views["backend"] = _unavailable_view(
            backend_issue, group_id=batch["id"],
            group_published_at=batch["published_at"], group_sha256=batch["sha256"],
            source_array="rankings", score_field="score",
            source_row_count=len(backend_rows) if isinstance(backend_rows, list) else None,
        )
    else:
        assert isinstance(backend_rows, list)
        views["backend"] = _build_api_view(
            backend_rows,
            group_id=batch["id"],
            group_published_at=batch["published_at"],
            group_sha256=batch["sha256"],
            source_array="rankings",
            score_field="score",
            source_row_count=batch["entry_count"],
            provider=benchmark_provider,
            route=benchmark_route,
            required_score_basis="backend",
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "source_mode": "api_v1.1",
        "source_url": "https://modeldial.com/api/v1/radar/latest.json",
        "generated_at": generated_at,
        "source": source,
        "batch": batch,
        "overall_batch": overall_batch,
        "target": {"model": SOL_MODEL, "provider": benchmark_provider, "route": benchmark_route},
        "benchmark_provider": benchmark_provider,
        "benchmark_route": benchmark_route,
        "evidence_scope": EVIDENCE_SCOPE,
        "views": views,
    }


def _full_snapshot_context(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("ModelDial full snapshot must be an object")
    require_full_snapshot_hash(payload)
    if payload.get("kind") != "first_party_snapshot" or payload.get("status") != "complete":
        raise ValueError("ModelDial full snapshot is not a complete first-party publication")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping) or provenance.get("public_official_snapshot") is not True:
        raise ValueError("ModelDial full snapshot lacks public first-party provenance")
    batch = {
        "id": _required_text(payload, "batch_id", "batch_id"),
        "published_at": _timestamp(payload.get("published_at"), "published_at"),
        "question_pack_id": _required_text(payload, "question_pack_id", "question_pack_id"),
        "question_pack_version": _required_text(payload, "question_pack_version", "question_pack_version"),
        "grader_version": _required_text(payload, "grader_version", "grader_version"),
        "evaluation_profile": _required_text(payload, "evaluation_profile", "evaluation_profile"),
        "score_baseline_id": _required_text(payload, "score_baseline_id", "score_baseline_id"),
        "pricing_snapshot_id": _required_text(payload, "pricing_snapshot_id", "pricing_snapshot_id"),
        "sha256": _sha256(payload.get("batch_sha256"), "batch_sha256"),
    }
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("ModelDial full snapshot entries must be a list")
    batch["entry_count"] = len(entries)
    return {"batch": batch, "entries": entries}


def _full_snapshot_sol_rows(
    context: Mapping[str, Any],
    provider: str,
    route: str,
) -> tuple[dict[str, dict[str, Any]], str | None, bool, str | None]:
    selected: dict[str, dict[str, Any]] = {}
    evidence_groups: set[str] = set()
    row_ids: set[str] = set()
    cost_complete = True
    for entry in context["entries"]:
        if not isinstance(entry, Mapping):
            continue
        configuration = entry.get("model_configuration")
        if not isinstance(configuration, Mapping):
            continue
        if (
            configuration.get("canonical_model_id") != SOL_MODEL
            or configuration.get("provider_id") != provider
            or configuration.get("route_type") != route
        ):
            continue
        effort = configuration.get("reasoning_effort")
        if effort not in EFFORTS:
            continue
        if effort in selected:
            return {}, None, False, "duplicate_effort"
        if (
            entry.get("advisor_eligible") is not True
            or entry.get("score_integrity") != "first_party_controlled"
            or entry.get("route_identity") != "first_party_controlled"
        ):
            return {}, None, False, f"untrusted_candidate:{effort}"
        evidence_group = entry.get("source_evidence_group_id")
        if not _text(evidence_group):
            return {}, None, False, f"missing_evidence_group:{effort}"
        evidence_groups.add(evidence_group)
        score = _finite_number(entry.get("score"), minimum=0.0)
        if score is None or score > 100.0:
            return {}, None, False, f"invalid_score:{effort}"
        cost = _finite_number(entry.get("estimated_api_cost_usd"), minimum=0.0)
        if entry.get("cost_coverage") != "complete" or cost is None:
            cost_complete = False
        elapsed_raw = entry.get("elapsed_ms", entry.get("elapsedMs"))
        elapsed_ms = _finite_number(elapsed_raw, minimum=0.0)
        row_id = entry.get("id")
        if not _text(row_id):
            row_id = entry.get("result_id")
        if not _text(row_id):
            row_id = f"{context['batch']['id']}:{SOL_MODEL}:{effort}"
        if row_id in row_ids:
            return {}, None, False, f"duplicate_row_id:{effort}"
        row_ids.add(row_id)
        selected[effort] = {
            "effort": effort,
            "score": score,
            "max_score": 100.0,
            "score_field": "score",
            "score_basis": "full_snapshot",
            "score_group_id": None,
            "source_evidence_group_id": evidence_group,
            "score_source_array": "entries",
            "provider": provider,
            "model": SOL_MODEL,
            "route": route,
            "row_id": row_id,
            "elapsed_ms": elapsed_ms,
            "estimated_reference_cost_usd": None,
            "verified_cost_usd": cost if entry.get("cost_coverage") == "complete" else None,
        }
    if set(selected) != set(EFFORTS):
        missing = ",".join(effort for effort in EFFORTS if effort not in selected)
        return {}, None, False, f"incomplete_efforts:{missing}"
    if provider == REFERENCE_PROVIDER:
        group_id = context["batch"]["id"]
    elif len(evidence_groups) == 1:
        # Retain the historical group ID used by complete official fixtures.
        group_id = next(iter(evidence_groups))
    else:
        group_id = context["batch"]["id"]
    for item in selected.values():
        item["score_group_id"] = group_id
    return selected, group_id, cost_complete, None


def adapt_sol_full_snapshot(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Adapt a complete public full snapshot as an independent Sol backend view."""

    context = _full_snapshot_context(payload)
    batch = context["batch"]
    benchmark_provider, benchmark_route = _choose_full_snapshot_benchmark(context["entries"])
    selected, group_id, cost_complete, failure_reason = _full_snapshot_sol_rows(
        context, benchmark_provider, benchmark_route
    )
    if benchmark_provider == SOL_PROVIDER and not selected:
        # A five-effort identity set is not enough when row integrity fails.
        # Try the permitted reference pair as a whole; never salvage rows from
        # both pairs into one view.
        benchmark_provider, benchmark_route = REFERENCE_BENCHMARK
        selected, group_id, cost_complete, failure_reason = _full_snapshot_sol_rows(
            context, benchmark_provider, benchmark_route
        )
    normalized_batch = {
        "id": batch["id"],
        "revision": None,
        "published_at": batch["published_at"],
        "question_pack_id": batch["question_pack_id"],
        "question_pack_version": batch["question_pack_version"],
        "grader_version": batch["grader_version"],
        "evaluation_profile": batch["evaluation_profile"],
        "score_baseline_id": batch["score_baseline_id"],
        "pricing_snapshot_id": batch["pricing_snapshot_id"],
        "entry_count": batch["entry_count"],
        "sha256": batch["sha256"],
    }
    source = {
        "name": "ModelDial Full Snapshot",
        "kind": "first_party_snapshot",
        "methodology_url": "https://modeldial.com/method",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
    }
    group_fields = {
        "group_id": group_id if selected and isinstance(group_id, str) else None,
        "group_published_at": batch["published_at"],
        "group_sha256": batch["sha256"],
        "source_array": "entries",
        "score_field": "score",
        "source_row_count": batch["entry_count"],
    }
    views: dict[str, dict[str, Any]] = {
        "general": _unavailable_view("full_snapshot_backend_only"),
        "backend": _unavailable_view(
            group_id=group_fields["group_id"],
            group_published_at=batch["published_at"],
            group_sha256=batch["sha256"],
            source_array="entries", score_field="score",
            source_row_count=batch["entry_count"],
            reason="full_snapshot_backend_only",
        ),
        "frontend": _unavailable_view("full_snapshot_backend_only"),
        "reasoning": _unavailable_view("full_snapshot_backend_only"),
    }
    verified_group_id = group_id if selected and isinstance(group_id, str) else None
    if verified_group_id is not None:
        items = [selected[effort] for effort in EFFORTS]
        backend: dict[str, Any] = {
            "status": "ready",
            **group_fields,
            "items": items,
        }
        if cost_complete:
            protocol = "|".join((
                batch["question_pack_id"], batch["question_pack_version"],
                batch["grader_version"], batch["evaluation_profile"],
                batch["score_baseline_id"],
            ))
            backend["cost_coverage"] = {
                "status": "complete",
                "protocol_id": protocol,
                "pricing_snapshot_id": batch["pricing_snapshot_id"],
                "source_group_id": verified_group_id,
                "source_array": "entries",
                "cost_source_group_id": verified_group_id,
                "cost_source_array": "entries",
                "cost_field": "verified_cost_usd",
                "evidence_group_id": verified_group_id,
                "benchmark_provider": benchmark_provider,
                "benchmark_route": benchmark_route,
                "batch_id": batch["id"],
                "batch_sha256": batch["sha256"],
                "entry_count": batch["entry_count"],
                "score_signature": _score_signature(items),
            }
        views["backend"] = backend
    else:
        views["backend"] = _unavailable_view(
            failure_reason or "full_snapshot_sol_rows_unavailable",
            group_published_at=batch["published_at"], group_sha256=batch["sha256"],
            source_array="entries", score_field="score", source_row_count=batch["entry_count"],
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "source_mode": "full_snapshot",
        "source_url": "https://modeldial.com/data/reference-snapshots/latest.json",
        "generated_at": batch["published_at"],
        "source": source,
        "batch": normalized_batch,
        "overall_batch": None,
        "evidence_group_id": verified_group_id,
        "target": {"model": SOL_MODEL, "provider": benchmark_provider, "route": benchmark_route},
        "benchmark_provider": benchmark_provider,
        "benchmark_route": benchmark_route,
        "evidence_scope": EVIDENCE_SCOPE,
        "views": views,
    }


def enrich_sol_backend_costs(
    snapshot: Mapping[str, Any], full_snapshot: Mapping[str, Any]
) -> dict[str, Any]:
    """Attach full-snapshot costs only to matching API backend rows.

    A bad or mismatched optional full snapshot leaves the valid API score view
    usable in quality-only mode. This never copies costs into aggregate axes.
    """

    root = _normalize_root(snapshot)
    if root["source_mode"] != "api_v1.1":
        raise ValueError("cost enrichment requires a normalized ModelDial API snapshot")
    normalized_views = {
        name: _validate_view(root, name, root["views"].get(name))
        for name in VIEWS
    }
    for view in normalized_views.values():
        view.pop("cost_coverage", None)
        for item in view.get("items", []):
            item["verified_cost_usd"] = None
    result = dict(root)
    result["views"] = normalized_views
    try:
        full = adapt_sol_full_snapshot(full_snapshot)
        full_root = _normalize_root(full)
        full_view = _validate_view(full_root, "backend", full_root["views"].get("backend"))
    except (ValueError, TypeError, KeyError):
        return result
    if (
        root["target"]["provider"], root["target"]["route"]
    ) != (
        full_root["target"]["provider"], full_root["target"]["route"]
    ):
        return result
    api_batch = root["batch"]
    full_batch = full_root["batch"]
    matching_fields = (
        "id", "published_at", "question_pack_version", "grader_version",
        "evaluation_profile", "score_baseline_id", "pricing_snapshot_id",
        "entry_count", "sha256",
    )
    if api_batch.get("question_pack_id") is not None:
        matching_fields += ("question_pack_id",)
    if any(full_batch.get(field) != api_batch.get(field) for field in matching_fields):
        return result
    api_view = normalized_views["backend"]
    coverage = full_view.get("cost_coverage")
    if (
        api_view.get("status") != "ready"
        or full_view.get("status") != "ready"
        or not isinstance(coverage, Mapping)
        or coverage.get("status") != "complete"
        or not _cost_coverage_is_complete(full_root, full_view, full_view.get("items", []))
    ):
        return result
    api_items = {item["effort"]: item for item in api_view["items"]}
    full_items = {item["effort"]: item for item in full_view["items"]}
    if set(api_items) != set(EFFORTS) or set(full_items) != set(EFFORTS):
        return result
    for effort in EFFORTS:
        if api_items[effort]["score"] != full_items[effort]["score"]:
            return result
        cost = _finite_number(full_items[effort].get("verified_cost_usd"), minimum=0.0)
        if cost is None:
            return result
    for effort in EFFORTS:
        api_items[effort]["verified_cost_usd"] = full_items[effort]["verified_cost_usd"]
    score_signature = _score_signature(api_view["items"])
    if score_signature is None or score_signature != coverage.get("score_signature"):
        return result
    api_view["cost_coverage"] = {
        "status": "complete",
        "protocol_id": coverage["protocol_id"],
        "pricing_snapshot_id": coverage["pricing_snapshot_id"],
        "source_group_id": api_view["group_id"],
        "source_array": api_view["source_array"],
        "cost_source_group_id": full_view["group_id"],
        "cost_source_array": "entries",
        "cost_field": "verified_cost_usd",
        "evidence_group_id": coverage.get("evidence_group_id"),
        "benchmark_provider": root["target"]["provider"],
        "benchmark_route": root["target"]["route"],
        "batch_id": full_batch["id"],
        "batch_sha256": full_batch["sha256"],
        "entry_count": full_batch["entry_count"],
        "score_signature": score_signature,
    }
    return result


def _normalize_supported(supported_efforts: Iterable[str] | None) -> tuple[str, ...]:
    if supported_efforts is None:
        return EFFORTS
    if isinstance(supported_efforts, (str, bytes)):
        raise ValueError("supported_efforts must be an iterable of effort names")
    try:
        requested = set(supported_efforts)
    except TypeError as exc:
        raise ValueError("supported_efforts must be iterable") from exc
    unknown = requested.difference(EFFORTS)
    if unknown:
        raise ValueError(f"unsupported Sol efforts: {', '.join(sorted(map(str, unknown)))}")
    return tuple(effort for effort in EFFORTS if effort in requested)


def _normalize_root(snapshot: Any) -> dict[str, Any]:
    if not isinstance(snapshot, Mapping):
        raise ValueError("Sol snapshot must be an object")
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Sol snapshot schema_version is unsupported")
    source_mode = snapshot.get("source_mode")
    if source_mode not in ("api_v1.1", "full_snapshot"):
        raise ValueError("Sol snapshot source_mode is unsupported")
    generated_at = _timestamp(snapshot.get("generated_at"), "generated_at")
    source = snapshot.get("source")
    if not isinstance(source, Mapping) or source.get("kind") != "first_party_snapshot":
        raise ValueError("Sol snapshot source provenance is invalid")
    normalized_source = {
        key: _required_text(source, key, f"source.{key}")
        for key in ("name", "kind", "methodology_url", "license", "license_url")
    }
    batch = snapshot.get("batch")
    if not isinstance(batch, Mapping):
        raise ValueError("Sol snapshot batch is invalid")
    raw_revision = batch.get("revision")
    if source_mode == "full_snapshot" and raw_revision is None:
        revision = None
    else:
        revision = _positive_integer(raw_revision, "batch.revision")
    raw_pricing_id = batch.get("pricing_snapshot_id")
    if source_mode == "full_snapshot" and raw_pricing_id is None:
        pricing_id = None
    else:
        pricing_id = _required_text(batch, "pricing_snapshot_id", "batch.pricing_snapshot_id")
    raw_question_pack_id = batch.get("question_pack_id")
    if source_mode == "full_snapshot" and raw_question_pack_id is None:
        question_pack_id = _required_text(batch, "question_pack_id", "batch.question_pack_id")
    elif raw_question_pack_id is None:
        question_pack_id = None
    else:
        question_pack_id = _required_text(batch, "question_pack_id", "batch.question_pack_id")
    normalized_batch = {
        "id": _required_text(batch, "id", "batch.id"),
        "revision": revision,
        "published_at": _timestamp(batch.get("published_at"), "batch.published_at"),
        "question_pack_id": question_pack_id,
        "question_pack_version": _required_text(batch, "question_pack_version", "batch.question_pack_version"),
        "grader_version": _required_text(batch, "grader_version", "batch.grader_version"),
        "evaluation_profile": _required_text(batch, "evaluation_profile", "batch.evaluation_profile"),
        "score_baseline_id": _required_text(batch, "score_baseline_id", "batch.score_baseline_id"),
        "pricing_snapshot_id": pricing_id,
        "entry_count": _positive_integer(batch.get("entry_count"), "batch.entry_count", allow_zero=True),
        "sha256": _sha256(batch.get("sha256"), "batch.sha256"),
    }

    raw_overall = snapshot.get("overall_batch")
    overall: dict[str, Any] | None
    if raw_overall is None:
        overall = None
    elif not isinstance(raw_overall, Mapping):
        raise ValueError("Sol snapshot overall_batch is invalid")
    else:
        sources = raw_overall.get("sources")
        if not isinstance(sources, Mapping):
            raise ValueError("Sol snapshot overall_batch.sources is invalid")
        normalized_sources: dict[str, dict[str, str]] = {}
        for axis in ("backend", "frontend", "knowledge"):
            item = sources.get(axis)
            if not isinstance(item, Mapping):
                raise ValueError(f"Sol snapshot overall source {axis} is invalid")
            normalized_sources[axis] = {
                "batch_id": _required_text(item, "batch_id", f"overall_batch.sources.{axis}.batch_id"),
                "published_at": _timestamp(item.get("published_at"), f"overall_batch.sources.{axis}.published_at"),
                "sha256": _sha256(item.get("sha256"), f"overall_batch.sources.{axis}.sha256"),
            }
        overall = {
            "id": _required_text(raw_overall, "id", "overall_batch.id"),
            "published_at": _timestamp(raw_overall.get("published_at"), "overall_batch.published_at"),
            "sha256": _sha256(raw_overall.get("sha256"), "overall_batch.sha256"),
            "entry_count": _positive_integer(raw_overall.get("entry_count"), "overall_batch.entry_count"),
            "sources": normalized_sources,
        }

    target = snapshot.get("target")
    if not isinstance(target, Mapping) or target.get("model") != SOL_MODEL:
        raise ValueError("Sol snapshot target identity is invalid")
    benchmark_provider = target.get("provider")
    benchmark_route = target.get("route")
    if not _allowed_benchmark(benchmark_provider, benchmark_route):
        raise ValueError("Sol snapshot benchmark identity is unsupported")
    if (
        snapshot.get("benchmark_provider", benchmark_provider) != benchmark_provider
        or snapshot.get("benchmark_route", benchmark_route) != benchmark_route
    ):
        raise ValueError("Sol snapshot benchmark provenance is inconsistent")
    evidence_scope = snapshot.get("evidence_scope", EVIDENCE_SCOPE)
    if evidence_scope != EVIDENCE_SCOPE:
        raise ValueError("Sol snapshot evidence_scope is unsupported")
    views = snapshot.get("views")
    if not isinstance(views, Mapping):
        raise ValueError("Sol snapshot views must be an object")
    evidence_group_id = snapshot.get("evidence_group_id")
    if evidence_group_id is not None and not _text(evidence_group_id):
        raise ValueError("Sol snapshot evidence_group_id is invalid")
    if source_mode == "api_v1.1" and evidence_group_id is not None:
        raise ValueError("API Sol snapshots cannot carry a full-snapshot evidence group")
    source_url = snapshot.get("source_url")
    if source_url is not None and not _text(source_url):
        raise ValueError("Sol snapshot source_url is invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        "source_mode": source_mode,
        "source_url": source_url,
        "generated_at": generated_at,
        "source": normalized_source,
        "batch": normalized_batch,
        "overall_batch": overall,
        "evidence_group_id": evidence_group_id,
        "target": {"model": SOL_MODEL, "provider": benchmark_provider, "route": benchmark_route},
        "benchmark_provider": benchmark_provider,
        "benchmark_route": benchmark_route,
        "evidence_scope": evidence_scope,
        "views": views,
    }


def _view_expected_group(root: Mapping[str, Any], view_name: str) -> tuple[str, str, str, int] | None:
    if view_name == "backend":
        batch = root["batch"]
        if root["source_mode"] == "full_snapshot":
            group_id = root.get("evidence_group_id")
            if not _text(group_id):
                return None
            return group_id, batch["published_at"], batch["sha256"], batch["entry_count"]
        return batch["id"], batch["published_at"], batch["sha256"], batch["entry_count"]
    overall = root["overall_batch"]
    if overall is None:
        return None
    if view_name == "general":
        return overall["id"], overall["published_at"], overall["sha256"], overall["entry_count"]
    axis = "frontend" if view_name == "frontend" else "knowledge"
    source = overall["sources"][axis]
    return source["batch_id"], source["published_at"], source["sha256"], overall["entry_count"]


def _validate_view(root: Mapping[str, Any], view_name: str, raw: Any) -> dict[str, Any]:
    source_array, score_field = _SCORE_FIELDS[view_name]
    if view_name == "backend" and root["source_mode"] == "full_snapshot":
        source_array = "entries"
    expected = _view_expected_group(root, view_name)
    if not isinstance(raw, Mapping):
        return _unavailable_view("view_missing_or_invalid", source_array=source_array, score_field=score_field)
    if raw.get("status") == "unavailable":
        reason = raw.get("reason")
        return _unavailable_view(
            reason if _text(reason) else "view_unavailable",
            group_id=raw.get("group_id") if _text(raw.get("group_id")) else None,
            group_published_at=raw.get("group_published_at") if isinstance(raw.get("group_published_at"), str) else None,
            group_sha256=raw.get("group_sha256") if isinstance(raw.get("group_sha256"), str) else None,
            source_array=raw.get("source_array") if isinstance(raw.get("source_array"), str) else source_array,
            score_field=raw.get("score_field") if isinstance(raw.get("score_field"), str) else score_field,
            source_row_count=raw.get("source_row_count") if _valid_positive_int(raw.get("source_row_count")) else None,
        )
    if raw.get("status") != "ready" or expected is None:
        return _unavailable_view("view_provenance_missing", source_array=source_array, score_field=score_field)
    expected_group, expected_published, expected_sha, expected_count = expected
    group_id = raw.get("group_id")
    group_published = raw.get("group_published_at")
    group_sha = raw.get("group_sha256")
    if (
        group_id != expected_group
        or group_published != expected_published
        or group_sha != expected_sha
        or raw.get("source_array") != source_array
        or raw.get("score_field") != score_field
        or raw.get("source_row_count") != expected_count
    ):
        return _unavailable_view(
            "group_identity_mismatch", group_id=group_id if _text(group_id) else None,
            group_published_at=group_published if isinstance(group_published, str) else None,
            group_sha256=group_sha if isinstance(group_sha, str) else None,
            source_array=source_array, score_field=score_field,
            source_row_count=raw.get("source_row_count") if _valid_positive_int(raw.get("source_row_count")) else None,
        )
    items = raw.get("items")
    if not isinstance(items, list) or len(items) != len(EFFORTS):
        return _unavailable_view(
            "incomplete_efforts", group_id=expected_group,
            group_published_at=expected_published, group_sha256=expected_sha,
            source_array=source_array, score_field=score_field, source_row_count=expected_count,
        )

    by_effort: dict[str, Mapping[str, Any]] = {}
    row_ids: set[str] = set()
    max_score_reference: float | None = None
    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            return _unavailable_view(
                "invalid_effort_row", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        effort = item.get("effort")
        row_id = item.get("row_id")
        if effort not in EFFORTS or effort in by_effort or not _text(row_id) or row_id in row_ids:
            return _unavailable_view(
                "duplicate_or_invalid_effort_identity", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        if (
            item.get("provider"), item.get("model"), item.get("route")
        ) != (
            root["target"]["provider"], SOL_MODEL, root["target"]["route"]
        ):
            return _unavailable_view(
                "candidate_runtime_identity_mismatch", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        source_evidence_group_id = item.get("source_evidence_group_id")
        if root["source_mode"] == "full_snapshot" and not _text(source_evidence_group_id):
            return _unavailable_view(
                "missing_source_evidence_group", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        if (
            item.get("score_group_id") != expected_group
            or item.get("score_source_array") != source_array
            or item.get("score_field") != score_field
        ):
            return _unavailable_view(
                "candidate_group_identity_mismatch", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        score = _finite_number(item.get("score"), minimum=0.0)
        max_score = _finite_number(item.get("max_score"), minimum=0.0)
        elapsed_ms = _finite_number(item.get("elapsed_ms"), minimum=0.0)
        if score is None or max_score is None or max_score <= 0.0 or score > max_score:
            return _unavailable_view(
                "invalid_score_or_elapsed", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        if max_score_reference is None:
            max_score_reference = max_score
        elif max_score_reference != max_score:
            return _unavailable_view(
                "max_score_mismatch", group_id=expected_group,
                group_published_at=expected_published, group_sha256=expected_sha,
                source_array=source_array, score_field=score_field, source_row_count=expected_count,
            )
        row_ids.add(row_id)
        by_effort[effort] = item
        normalized_items.append({
            "effort": effort,
            "score": score,
            "max_score": max_score,
            "score_field": score_field,
            "score_group_id": item.get("score_group_id"),
            "score_source_array": source_array,
            "provider": root["target"]["provider"],
            "model": SOL_MODEL,
            "route": root["target"]["route"],
            "row_id": row_id,
            "elapsed_ms": elapsed_ms,
            "estimated_reference_cost_usd": _finite_number(
                item.get("estimated_reference_cost_usd"), minimum=0.0
            ),
            "verified_cost_usd": _finite_number(item.get("verified_cost_usd"), minimum=0.0),
        })
        if root["source_mode"] == "full_snapshot":
            normalized_items[-1]["source_evidence_group_id"] = source_evidence_group_id
    if set(by_effort) != set(EFFORTS):
        return _unavailable_view(
            "incomplete_efforts", group_id=expected_group,
            group_published_at=expected_published, group_sha256=expected_sha,
            source_array=source_array, score_field=score_field, source_row_count=expected_count,
        )
    normalized = {
        "status": "ready",
        "group_id": expected_group,
        "group_published_at": expected_published,
        "group_sha256": expected_sha,
        "source_array": source_array,
        "score_field": score_field,
        "source_row_count": expected_count,
        "items": sorted(normalized_items, key=lambda item: EFFORTS.index(item["effort"])),
    }
    coverage = raw.get("cost_coverage")
    if isinstance(coverage, Mapping):
        normalized["cost_coverage"] = dict(coverage)
    return normalized


def _cost_coverage_is_complete(root: Mapping[str, Any], view: Mapping[str, Any], band: list[Mapping[str, Any]]) -> bool:
    coverage = view.get("cost_coverage")
    if not isinstance(coverage, Mapping) or coverage.get("status") != "complete":
        return False
    required_text = (
        "protocol_id", "pricing_snapshot_id", "source_group_id", "source_array",
        "cost_source_group_id", "cost_source_array", "evidence_group_id", "cost_field",
        "benchmark_provider", "benchmark_route", "batch_id", "batch_sha256",
        "score_signature",
    )
    if (
        any(not _text(coverage.get(field)) for field in required_text)
        or not _valid_positive_int(coverage.get("entry_count"))
    ):
        return False
    batch = root["batch"]
    protocol = coverage["protocol_id"].split("|")
    expected_protocol = [batch[key] for key in (
        "question_pack_version", "grader_version", "evaluation_profile", "score_baseline_id",
    )]
    if (
        coverage["pricing_snapshot_id"] != batch["pricing_snapshot_id"]
        or len(protocol) != 5 or not protocol[0] or protocol[1:] != expected_protocol
        or (batch.get("question_pack_id") is not None and protocol[0] != batch["question_pack_id"])
        or coverage["batch_id"] != batch["id"]
        or coverage["batch_sha256"] != batch["sha256"]
        or coverage["entry_count"] != batch["entry_count"]
        or coverage["benchmark_provider"] != root["target"]["provider"]
        or coverage["benchmark_route"] != root["target"]["route"]
        or coverage["cost_source_array"] != "entries"
        or coverage["cost_field"] != "verified_cost_usd"
        or view.get("score_field") != "score"
    ):
        return False
    if (
        coverage.get("source_group_id") != view.get("group_id")
        or coverage.get("source_array") != view.get("source_array")
        or coverage.get("cost_source_group_id") != coverage.get("evidence_group_id")
        or coverage.get("cost_field") != "verified_cost_usd"
        or (
            root["source_mode"] == "full_snapshot"
            and coverage.get("cost_source_group_id") != view.get("group_id")
        )
        or _score_signature(view.get("items")) != coverage.get("score_signature")
    ):
        return False
    for item in band:
        cost = _cost_value(item, coverage)
        if (
            cost is None
            or item.get("score_group_id") != coverage.get("source_group_id")
            or item.get("score_source_array") != coverage.get("source_array")
        ):
            return False
    return True


def _cost_value(item: Mapping[str, Any], coverage: Mapping[str, Any]) -> float | None:
    return _finite_number(item.get(coverage.get("cost_field")), minimum=0.0)


def _selection_for_view(
    root: Mapping[str, Any],
    view_name: str,
    view: Mapping[str, Any],
    *,
    supported: tuple[str, ...],
    quality_gap: float,
) -> dict[str, Any]:
    benchmark_metadata = {
        "benchmark_provider": root["target"]["provider"],
        "benchmark_route": root["target"]["route"],
        "evidence_scope": root["evidence_scope"],
    }
    if view.get("status") != "ready":
        result = {
            "status": "unavailable",
            "reason": view.get("reason", "view_unavailable"),
            **benchmark_metadata,
        }
        for key in ("group_id", "source_array", "score_field"):
            if key in view:
                result[key] = view[key]
        return result
    items = {item["effort"]: item for item in view["items"]}
    source_winner = min(EFFORTS, key=lambda effort: (-items[effort]["score"], EFFORTS.index(effort)))
    supported_items = [items[effort] for effort in supported if effort in items]
    if not supported_items:
        return {
            "status": "unavailable",
            "reason": "no_supported_efforts",
            "group_id": view["group_id"],
            "source_array": view["source_array"],
            "score_field": view["score_field"],
            **benchmark_metadata,
        }
    supported_best_score = max(item["score"] for item in supported_items)
    band = [item for item in supported_items if item["score"] >= supported_best_score - quality_gap]
    if _cost_coverage_is_complete(root, view, band):
        coverage = view["cost_coverage"]
        costs = {item["effort"]: _cost_value(item, coverage) for item in band}
        lowest_cost = min(cost for cost in costs.values() if cost is not None)
        lowest_cost_items = [item for item in band if costs[item["effort"]] == lowest_cost]
        if len(lowest_cost_items) > 1 and any(item["elapsed_ms"] is None for item in lowest_cost_items):
            # If latency is missing for any cheapest-cost tie, skip latency for
            # the whole tie and preserve cost priority before score/effort.
            chosen = min(
                lowest_cost_items,
                key=lambda item: (-item["score"], EFFORTS.index(item["effort"])),
            )
            selection_mode = "cost_optimized"
        else:
            chosen = min(
                band,
                key=lambda item: (
                    costs[item["effort"]],
                    item["elapsed_ms"] if item["elapsed_ms"] is not None else math.inf,
                    -item["score"],
                    EFFORTS.index(item["effort"]),
                ),
            )
            selection_mode = "cost_optimized"
    else:
        chosen = min(
            supported_items,
            key=lambda item: (-item["score"], EFFORTS.index(item["effort"])),
        )
        selection_mode = "quality_only"

    source_metadata: dict[str, Any] = {
        "name": root["source"]["name"],
        "source_url": root.get("source_url"),
        "kind": root["source"]["kind"],
        "license": root["source"]["license"],
        "generated_at": root["generated_at"],
        **benchmark_metadata,
        "group_id": view["group_id"],
        "group_published_at": view["group_published_at"],
        "group_sha256": view["group_sha256"],
        "source_array": view["source_array"],
        "score_field": view["score_field"],
    }
    if selection_mode == "cost_optimized":
        coverage = view["cost_coverage"]
        source_metadata["cost_coverage"] = {
            field: coverage[field]
            for field in ("protocol_id", "pricing_snapshot_id", "source_group_id", "source_array", "cost_field")
        }
        if _text(coverage.get("evidence_group_id")):
            source_metadata["cost_coverage"]["evidence_group_id"] = coverage["evidence_group_id"]
    return {
        "status": "ready",
        "selected_role": ROLE_BY_EFFORT[chosen["effort"]],
        "selected_effort": chosen["effort"],
        "selected_score": chosen["score"],
        "source_winner_effort": source_winner,
        "source_winner_score": items[source_winner]["score"],
        "best_supported_effort": min(
            supported_items,
            key=lambda item: (-item["score"], EFFORTS.index(item["effort"])),
        )["effort"],
        "capability_degraded": source_winner not in supported,
        "selection_mode": selection_mode,
        "quality_gap": quality_gap,
        "quality_band_efforts": [item["effort"] for item in band],
        "group_id": view["group_id"],
        "source_array": view["source_array"],
        "score_field": view["score_field"],
        **benchmark_metadata,
        "source_metadata": source_metadata,
    }


def select_sol(
    snapshot: Mapping[str, Any],
    *,
    supported_efforts: Iterable[str] | None = None,
    quality_gap: float = 2.0,
) -> dict[str, Any]:
    """Revalidate and select Sol independently for each source view.

    Quality remains the deciding signal unless every candidate in the local
    quality band has finite cost plus matching explicit complete protocol,
    pricing, source-group, and source-array coverage. Latency is an optional
    tie-break among equal-cost choices.
    """

    normalized_root = _normalize_root(snapshot)
    supported = _normalize_supported(supported_efforts)
    gap = _finite_number(quality_gap, minimum=0.0)
    if gap is None or gap > 100.0:
        raise ValueError("quality_gap must be a finite number from 0 through 100")
    raw_views = normalized_root["views"]
    normalized_views: dict[str, dict[str, Any]] = {}
    for view_name in VIEWS:
        normalized_views[view_name] = _validate_view(
            normalized_root, view_name, raw_views.get(view_name)
        )
    selections = {
        view_name: _selection_for_view(
            normalized_root, view_name, normalized_views[view_name],
            supported=supported, quality_gap=gap,
        )
        for view_name in VIEWS
    }
    general = selections["general"]
    ready = any(view.get("status") == "ready" for view in selections.values())
    result: dict[str, Any] = {
        "status": "ready" if ready else "unavailable",
        "source_mode": normalized_root["source_mode"],
        "benchmark_provider": normalized_root["target"]["provider"],
        "benchmark_route": normalized_root["target"]["route"],
        "evidence_scope": normalized_root["evidence_scope"],
        "views": selections,
        "quality_gap": gap,
    }
    for key in (
        "selected_role", "selected_effort", "selected_score", "source_winner_effort",
        "source_winner_score", "capability_degraded", "selection_mode", "source_metadata",
    ):
        result[key] = general.get(key) if general.get("status") == "ready" else None
    return result

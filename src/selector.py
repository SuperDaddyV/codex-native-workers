"""Daily ModelDial selection for native Sol/Luna workers and legacy Luna roles."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import platform
import re
import time
import tomllib
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


REFERENCE_MODEL = "gpt-5.6-sol"
LUNA_MODEL = "gpt-5.6-luna"
EFFORTS = ("low", "medium", "high", "xhigh", "max")
METADATA_SCHEMA_VERSION = 1
STATUS_SCHEMA_VERSION = 2
REFERENCE_COST_METRIC = "modeldial_estimated_reference_cost_usd"
USER_AGENT = "codex-native-workers/4.2.0"
ROLE_BY_EFFORT = {effort: f"luna_{effort}" for effort in EFFORTS}
BJT = timezone(timedelta(hours=8), name="BJT")
UTC = timezone.utc
MODELDIAL_API_URL = "https://modeldial.com/api/v1/radar/latest.json"
MODELDIAL_SNAPSHOT_URL = "https://modeldial.com/data/reference-snapshots/latest.json"
MODELDIAL_INDEX_URL = "https://modeldial.com/api/v1/radar/index.json"
MODELDIAL_ALLOWED_HOSTS = frozenset({"modeldial.com", "reference.modeldial.com"})
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
API_CLOCK_SKEW = timedelta(minutes=10)
NO_PROFILE_STATUS = "NO_LUNA_PROFILE_AVAILABLE"
LOCK_TIMEOUT_SECONDS = 30.0
MANIFEST_RELATIVE = Path("sol-luna-v4/install-manifest.json")
AGENTS_BEGIN = "<!-- BEGIN SOL_LUNA_V4 -->"
AGENTS_END = "<!-- END SOL_LUNA_V4 -->"
CONFIG_BEGIN = "# BEGIN SOL_LUNA_V4_CONFIG"
CONFIG_END = "# END SOL_LUNA_V4_CONFIG"
STABLE_AGENT_FILES = tuple(f"luna-{effort}.toml" for effort in EFFORTS)
STABLE_SKILL_FILES = (
    "sol-luna-status/SKILL.md",
    "sol-luna-upgrade/SKILL.md",
)
WORKER_AGENT_FILES = STABLE_AGENT_FILES + tuple(f"sol-{effort}.toml" for effort in EFFORTS)
WORKER_SKILL_FILES = STABLE_SKILL_FILES + ("sol-luna-delegate/SKILL.md",)
WORKER_PROFILE_SCHEMA_VERSION = 2
REFERENCE_POLICY_VERSION = 1
BENCHMARK_PAIRS = (("codex", "official_login"), ("cloudflare-reference", "custom_endpoint"))


def _sol_module():
    # Both source imports and the installed, sibling-file layout are supported.
    if __package__:
        from . import worker_selector
    else:
        import worker_selector
    return worker_selector


def _matching_snapshot_record(api: Mapping[str, Any], index: Any) -> Mapping[str, Any]:
    if not isinstance(index, Mapping) or index.get("schemaVersion") not in ("1.0", "1.1"):
        raise SnapshotInvalid("unsupported publication index")
    batch = api.get("batch")
    records = index.get("snapshots")
    if not isinstance(batch, Mapping) or not isinstance(records, list):
        raise SnapshotInvalid("invalid publication index")
    matches = [row for row in records if isinstance(row, Mapping) and row.get("batchId") == batch.get("id")]
    if len(matches) != 1:
        raise SnapshotInvalid("publication index has no unique matching batch")
    record = matches[0]
    fields = ("revision", "publishedAt", "questionPackVersion", "graderVersion", "evaluationProfile", "scoreBaselineId", "pricingSnapshotId", "entryCount", "sha256")
    if any(record.get(key) is None or type(record[key]) is not type(batch.get(key)) or record[key] != batch[key] for key in fields):
        raise SnapshotInvalid("publication index metadata mismatch")
    _validated_modeldial_url(record.get("fullSnapshotUrl"))
    return record


def _require_matching_full(record: Mapping[str, Any], payload: Any) -> None:
    fields = {"batchId": "batch_id", "publishedAt": "published_at", "questionPackVersion": "question_pack_version", "graderVersion": "grader_version", "evaluationProfile": "evaluation_profile", "scoreBaselineId": "score_baseline_id", "pricingSnapshotId": "pricing_snapshot_id", "sha256": "batch_sha256"}
    if not isinstance(payload, Mapping) or any(payload.get(dest) != record[key] for key, dest in fields.items()):
        raise SnapshotInvalid("complete snapshot metadata mismatch")
    if not isinstance(payload.get("entries"), list) or len(payload["entries"]) != record["entryCount"]:
        raise SnapshotInvalid("complete snapshot count mismatch")


def fetch_worker_data(*, timeout: float = 15.0) -> dict[str, Any]:
    """One refresh round; never combine an API identity with another snapshot."""
    result: dict[str, Any] = {}
    try:
        body, _ = _fetch_bytes(MODELDIAL_API_URL, expected_type="application/json", timeout=timeout)
        payload = json.loads(body.decode("utf-8"))
        if isinstance(payload, Mapping):
            result["api"] = payload
            try:
                result["luna_snapshot"] = adapt_modeldial_api(payload, allow_reference=True)
            except (SnapshotInvalid, ValueError, TypeError):
                pass
    except (OSError, UnicodeError, json.JSONDecodeError, SnapshotInvalid):
        pass
    api = result.get("api")
    record = None
    try:
        if isinstance(api, Mapping) and api.get("schemaVersion") in ("1.0", "1.1"):
            body, _ = _fetch_bytes(MODELDIAL_INDEX_URL, expected_type="application/json", timeout=timeout)
            record = _matching_snapshot_record(api, json.loads(body.decode("utf-8")))
            snapshot_url = record["fullSnapshotUrl"]
        else:
            snapshot_url = MODELDIAL_SNAPSHOT_URL
        body, url = _fetch_bytes(snapshot_url, expected_type="application/json", timeout=timeout)
        payload = json.loads(body.decode("utf-8"))
        if record is not None:
            _require_matching_full(record, payload)
        result["full_snapshot"] = payload
        result["full_snapshot_status"] = "matched" if record is not None else "independent_fallback"
        if "luna_snapshot" not in result:
            # A complete fallback is validated under its own identity. It is not
            # labelled as the newer API publication or used for overall Sol costs.
            result["luna_snapshot"] = adapt_modeldial_snapshot(payload, source_url=url, allow_reference=True)
    except (OSError, UnicodeError, json.JSONDecodeError, SnapshotInvalid, TypeError):
        result["full_snapshot_status"] = "unavailable_or_mismatched"
    return result


def _worker_record_valid(value: Any) -> bool:
    if not isinstance(value, Mapping) or value.get("worker_profile_schema_version") != 2:
        return False
    if value.get("reference_policy_version") != REFERENCE_POLICY_VERSION:
        return False
    if _profile_date(value) is None:
        return False
    for family in ("luna", "sol"):
        supported = value.get(f"supported_{family}")
        if not isinstance(supported, list) or not supported or any(effort not in EFFORTS for effort in supported) or len(set(supported)) != len(supported):
            return False
        item = value.get(family)
        if not isinstance(item, Mapping) or item.get("status") not in ("ready", "unavailable"):
            return False
        if item["status"] == "ready":
            pair = (item.get("benchmark_provider"), item.get("benchmark_route"))
            if item.get("evidence_scope") != "reference_only" or (pair not in BENCHMARK_PAIRS and not (family == "luna" and pair == ("not_recorded", "not_recorded"))):
                return False
            if family == "sol" and item.get("allowed_roles") != [f"sol_{effort}" for effort in supported]:
                return False
            records = [item] if family == "luna" else list(item.get("views", {}).values()) if isinstance(item.get("views"), Mapping) else []
            if not records or not any(isinstance(row, Mapping) and row.get("status") == "ready" for row in records):
                return False
            for row in records:
                if not isinstance(row, Mapping):
                    return False
                if row.get("status") == "unavailable":
                    continue
                effort = row.get("selected_effort")
                if row.get("status") != "ready" or effort not in supported or row.get("selected_role") != f"{family}_{effort}":
                    return False
    return True


def ensure_worker_profile(
    live_data: Mapping[str, Any] | None = None, *, state_dir: str | Path,
    now: datetime | None = None, supported_sol: Iterable[str] | None = None,
    supported_luna: Iterable[str] | None = None,
    live_fetcher: Callable[[], Mapping[str, Any]] | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """Cache one family-isolated daily choice without migrating legacy state."""
    current = _aware_bjt(now)
    root = Path(state_dir)
    daily = root / "worker-profile.json"
    lkg_path = root / "worker-last-good.json"
    supported_sol = _normalize_supported(supported_sol)
    supported_luna = _normalize_supported(supported_luna)
    with _selector_lock(root):
        existing = _read_json_safely(daily)
        if not refresh and _worker_record_valid(existing) and _profile_date(existing) == current.date().isoformat():
            # A changed explicit capability set requires re-selection, never a
            # silently unsupported cached native role.
            if existing.get("supported_sol") == list(supported_sol) and existing.get("supported_luna") == list(supported_luna):
                return dict(existing)
        if live_data is None and live_fetcher is not None:
            try:
                live_data = live_fetcher()
            except (OSError, ValueError, UnicodeError):
                live_data = None
        data = live_data if isinstance(live_data, Mapping) else {}
        if "schemaVersion" in data:
            data = {"api": data}
        previous = _read_json_safely(lkg_path)
        previous = previous if isinstance(previous, Mapping) else {}
        cache = dict(previous)
        result: dict[str, Any] = {
            "worker_profile_schema_version": WORKER_PROFILE_SCHEMA_VERSION,
            "reference_policy_version": REFERENCE_POLICY_VERSION,
            "selection_date_bjt": current.date().isoformat(),
            "selected_at_bjt": current.isoformat(),
            "supported_sol": list(supported_sol), "supported_luna": list(supported_luna),
            "luna": {"status": "unavailable"}, "sol": {"status": "unavailable", "views": {}},
        }
        luna_candidates = []
        if data.get("luna_snapshot") is not None:
            luna_candidates.append((data["luna_snapshot"], False))
        elif isinstance(data.get("api"), Mapping):
            try:
                luna_candidates.append((adapt_modeldial_api(data["api"], now=current, allow_reference=True), False))
            except (SnapshotInvalid, ValueError, TypeError):
                pass
        if not luna_candidates and isinstance(data.get("full_snapshot"), Mapping):
            try:
                luna_candidates.append((adapt_modeldial_snapshot(data["full_snapshot"], now=current, allow_reference=True), False))
            except (SnapshotInvalid, ValueError, TypeError):
                pass
        if previous.get("luna") is not None:
            luna_candidates.append((previous["luna"], True))
        legacy = _read_json_safely(root / "last-good-profile.json")
        if isinstance(legacy, Mapping):
            luna_candidates.append((legacy.get("snapshot"), True))
        for snapshot, fallback in luna_candidates:
            try:
                valid = validate_snapshot(snapshot)
                choice = select_snapshot(valid, supported_efforts=supported_luna, now=current, fallback=fallback)
            except (SnapshotInvalid, ValueError, TypeError, KeyError):
                continue
            result["luna"] = {"status": "ready", **{key: value for key, value in choice.items() if key != "source_url"}}
            result["luna"].update({"evidence_scope": "reference_only", "benchmark_provider": valid.get("benchmark_provider", "not_recorded"), "benchmark_route": valid.get("benchmark_route", "not_recorded")})
            cache["luna"] = valid
            break
        sol = _sol_module()
        sol_candidates = []
        if isinstance(data.get("api"), Mapping):
            try:
                adapted = sol.adapt_sol_api(data["api"])
                if isinstance(data.get("full_snapshot"), Mapping):
                    adapted = sol.enrich_sol_backend_costs(adapted, data["full_snapshot"])
                sol_candidates.append((adapted, False))
            except (ValueError, TypeError, KeyError):
                pass
        if isinstance(data.get("full_snapshot"), Mapping):
            try:
                sol_candidates.append((sol.adapt_sol_full_snapshot(data["full_snapshot"]), False))
            except (ValueError, TypeError, KeyError):
                pass
        if previous.get("sol") is not None:
            sol_candidates.append((previous["sol"], True))
        for snapshot, fallback in sol_candidates:
            try:
                if not isinstance(snapshot, Mapping):
                    raise ValueError("invalid Sol snapshot")
                timestamps = [snapshot.get("generated_at")]
                batch = snapshot.get("batch")
                if isinstance(batch, Mapping):
                    timestamps.append(batch.get("published_at"))
                overall = snapshot.get("overall_batch")
                if isinstance(overall, Mapping):
                    timestamps.append(overall.get("published_at"))
                    sources = overall.get("sources")
                    if isinstance(sources, Mapping):
                        timestamps.extend(row.get("published_at") for row in sources.values() if isinstance(row, Mapping))
                for timestamp in timestamps:
                    if timestamp is not None and datetime.fromisoformat(_parse_published_at(timestamp).replace("Z", "+00:00")) > current.astimezone(UTC) + API_CLOCK_SKEW:
                        raise ValueError("future Sol publication")
                choice = sol.select_sol(snapshot, supported_efforts=supported_sol, quality_gap=2.0)
                views = choice.get("views", {})
                if not isinstance(views, Mapping) or not any(isinstance(row, Mapping) and row.get("selected_role") for row in views.values()):
                    if not fallback and isinstance(views, Mapping):
                        result["sol"] = {**choice, "status": "unavailable", "fallback": False}
                    continue
            except (ValueError, TypeError, KeyError):
                continue
            result["sol"] = {
                **choice, "status": "ready", "fallback": fallback,
                "allowed_roles": [f"sol_{effort}" for effort in supported_sol],
                "source_generated_at": snapshot.get("generated_at"),
            }
            cache["sol"] = snapshot
            break
        if cache != previous:
            _write_json(lkg_path, cache)
        _write_json(daily, result)
        return result


class SnapshotInvalid(ValueError):
    """Raised when a published snapshot cannot be compared safely."""


class SelectionUnavailable(RuntimeError):
    """Raised when neither a valid live snapshot nor a valid LKG exists."""


def _aware_bjt(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(BJT)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    return now.astimezone(BJT)


def _parse_published_at(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SnapshotInvalid("published_at must be a non-empty ISO 8601 string")
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SnapshotInvalid("published_at must be valid ISO 8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SnapshotInvalid("published_at must include a UTC offset")
    return value


def _finite_cost(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        return None
    return normalized


def _validated_reference_costs(payload: Mapping[str, Any]) -> tuple[str, dict] | None:
    pricing_snapshot_id = payload.get("pricing_snapshot_id")
    reference_costs = payload.get("reference_costs")
    if not isinstance(pricing_snapshot_id, str) or not pricing_snapshot_id.strip():
        return None
    if not isinstance(reference_costs, Mapping):
        return None
    if (
        reference_costs.get("metric") != REFERENCE_COST_METRIC
        or reference_costs.get("provider") != "codex"
        or reference_costs.get("route") != "official_login"
    ):
        return None
    raw_by_effort = reference_costs.get("by_effort")
    if not isinstance(raw_by_effort, Mapping):
        return None
    by_effort = {}
    for effort in EFFORTS:
        pair = raw_by_effort.get(effort)
        if not isinstance(pair, Mapping):
            continue
        luna_cost = _finite_cost(pair.get("luna_cost_usd"))
        sol_cost = _finite_cost(pair.get("sol_cost_usd"))
        if luna_cost is None or sol_cost is None or sol_cost <= 0 or luna_cost >= sol_cost:
            continue
        by_effort[effort] = {
            "luna_cost_usd": luna_cost,
            "sol_cost_usd": sol_cost,
        }
    if not by_effort:
        return None
    return pricing_snapshot_id, {
        "metric": REFERENCE_COST_METRIC,
        "provider": "codex",
        "route": "official_login",
        "by_effort": by_effort,
    }


def validate_snapshot(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one complete snapshot and return its canonical normalized form."""

    if not isinstance(payload, Mapping):
        raise SnapshotInvalid("snapshot must be an object")
    if (
        "metadata_schema_version" in payload
        and payload.get("metadata_schema_version") != METADATA_SCHEMA_VERSION
    ):
        raise SnapshotInvalid("metadata_schema_version is unsupported")

    snapshot_id = payload.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.strip():
        raise SnapshotInvalid("snapshot_id must be a non-empty string")

    published_at = _parse_published_at(payload.get("published_at"))
    scores: dict[str, float] = {}
    canonical_scores = payload.get("scores")
    if isinstance(canonical_scores, Mapping):
        for effort in EFFORTS:
            score = canonical_scores.get(effort)
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                raise SnapshotInvalid(f"score must be numeric for: {effort}")
            normalized_score = float(score)
            if not math.isfinite(normalized_score):
                raise SnapshotInvalid(f"score must be finite for: {effort}")
            scores[effort] = normalized_score
    else:
        rows = payload.get("rows")
        if not isinstance(rows, list):
            raise SnapshotInvalid("rows must be a list")
        for row in rows:
            if not isinstance(row, Mapping) or row.get("model") != LUNA_MODEL:
                continue
            effort = row.get("effort")
            if effort not in EFFORTS:
                continue
            if effort in scores:
                raise SnapshotInvalid(f"duplicate Luna row: {effort}")
            score = row.get("score")
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                raise SnapshotInvalid(f"score must be numeric for: {effort}")
            normalized_score = float(score)
            if not math.isfinite(normalized_score):
                raise SnapshotInvalid(f"score must be finite for: {effort}")
            scores[effort] = normalized_score

    missing = [effort for effort in EFFORTS if effort not in scores]
    if missing:
        raise SnapshotInvalid(f"missing canonical Luna rows: {', '.join(missing)}")
    if payload.get("evidence_scope") == "reference_only" and any(score < 0 or score > 100 for score in scores.values()):
        raise SnapshotInvalid("benchmark scores must be in the published 0-100 range")

    normalized = {
        "metadata_schema_version": METADATA_SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "published_at": published_at,
        "scores": scores,
    }
    for key in ("source_mode", "source_url", "snapshot_hash"):
        if isinstance(payload.get(key), str) and payload[key]:
            normalized[key] = payload[key]
    if "benchmark_provider" in payload or "benchmark_route" in payload:
        pair = (payload.get("benchmark_provider"), payload.get("benchmark_route"))
        if pair not in BENCHMARK_PAIRS or payload.get("evidence_scope") != "reference_only":
            raise SnapshotInvalid("benchmark provenance is invalid")
        normalized.update({"benchmark_provider": pair[0], "benchmark_route": pair[1], "evidence_scope": "reference_only"})
        evidence_ids = payload.get("evidence_ids")
        if evidence_ids is not None:
            if not isinstance(evidence_ids, Mapping) or set(evidence_ids) != set(EFFORTS) or any(not isinstance(value, str) or not value.strip() for value in evidence_ids.values()):
                raise SnapshotInvalid("benchmark evidence ids are incomplete")
            normalized["evidence_ids"] = dict(evidence_ids)
    reference_costs = _validated_reference_costs(payload)
    if reference_costs is not None and normalized.get("benchmark_provider", "codex") == "codex":
        normalized["pricing_snapshot_id"], normalized["reference_costs"] = reference_costs
    return normalized


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SnapshotInvalid(f"ModelDial snapshot lacks {key}")
    return value


def _reference_cost_metadata(
    pricing_snapshot_id: Any,
    candidates: Mapping[tuple[str, str], list[float | None]],
) -> dict[str, Any]:
    if not isinstance(pricing_snapshot_id, str) or not pricing_snapshot_id.strip():
        return {}
    by_effort = {}
    for effort in EFFORTS:
        luna = candidates.get((LUNA_MODEL, effort), [])
        sol = candidates.get((REFERENCE_MODEL, effort), [])
        if len(luna) != 1 or len(sol) != 1 or luna[0] is None or sol[0] is None:
            continue
        if 0 <= luna[0] < sol[0]:
            by_effort[effort] = {
                "luna_cost_usd": luna[0],
                "sol_cost_usd": sol[0],
            }
    if not by_effort:
        return {}
    return {
        "pricing_snapshot_id": pricing_snapshot_id,
        "reference_costs": {
            "metric": REFERENCE_COST_METRIC,
            "provider": "codex",
            "route": "official_login",
            "by_effort": by_effort,
        },
    }


def _luna_benchmark_pair(rows: list, *, full: bool = False) -> tuple[str, str]:
    for pair in BENCHMARK_PAIRS:
        efforts = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            config = row.get("model_configuration") if full else row
            if not isinstance(config, Mapping):
                continue
            if config.get("canonical_model_id" if full else "model") != LUNA_MODEL:
                continue
            if (config.get("provider_id" if full else "provider"), config.get("route_type" if full else "route")) != pair:
                continue
            effort = config.get("reasoning_effort" if full else "reasoningEffort")
            if effort in EFFORTS:
                efforts.append(effort)
        if len(efforts) == len(EFFORTS) and set(efforts) == set(EFFORTS):
            return pair
    raise SnapshotInvalid("no complete permitted Luna benchmark source")


def adapt_modeldial_snapshot(
    payload: Mapping[str, Any],
    *,
    source_url: str = MODELDIAL_SNAPSHOT_URL,
    source_mode: str = "live_json",
    now: datetime | None = None,
    allow_reference: bool = False,
) -> dict[str, Any]:
    """Validate a first-party ModelDial publication and map it to selector rows."""

    if not isinstance(payload, Mapping):
        raise SnapshotInvalid("ModelDial snapshot must be an object")
    if payload.get("kind") != "first_party_snapshot" or payload.get("status") != "complete":
        raise SnapshotInvalid("ModelDial snapshot is not a complete publication")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping) or provenance.get("public_official_snapshot") is not True:
        raise SnapshotInvalid("ModelDial snapshot lacks first-party provenance")

    batch_id = _required_text(payload, "batch_id")
    published_at = _parse_published_at(payload.get("published_at"))
    published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    current = datetime.now(UTC) if now is None else now
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if published > current.astimezone(UTC):
        raise SnapshotInvalid("ModelDial snapshot publication time is in the future")

    for key in (
        "question_pack_id",
        "question_pack_version",
        "grader_version",
        "evaluation_profile",
        "score_baseline_id",
        "batch_sha256",
    ):
        _required_text(payload, key)

    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise SnapshotInvalid("ModelDial entries must be a list")

    rows = []
    evidence_groups = set()
    evidence_ids = {}
    pair = _luna_benchmark_pair(entries, full=True) if allow_reference else BENCHMARK_PAIRS[0]
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        configuration = entry.get("model_configuration")
        if not isinstance(configuration, Mapping):
            continue
        if configuration.get("canonical_model_id") != LUNA_MODEL:
            continue
        effort = configuration.get("reasoning_effort")
        if effort not in EFFORTS:
            continue
        if (
            configuration.get("provider_id") != pair[0]
            or configuration.get("route_type") != pair[1]
        ):
            continue
        if entry.get("advisor_eligible") is not True:
            raise SnapshotInvalid(f"ModelDial Luna row is not advisor eligible: {effort}")
        if entry.get("score_integrity") != "first_party_controlled":
            raise SnapshotInvalid(f"ModelDial Luna row lacks score integrity: {effort}")
        if entry.get("route_identity") != "first_party_controlled":
            raise SnapshotInvalid(f"ModelDial Luna row lacks route integrity: {effort}")
        evidence_group = entry.get("source_evidence_group_id")
        if not isinstance(evidence_group, str) or not evidence_group:
            raise SnapshotInvalid(f"ModelDial Luna row lacks evidence group: {effort}")
        evidence_groups.add(evidence_group)
        evidence_ids[effort] = evidence_group
        rows.append({"model": LUNA_MODEL, "effort": effort, "score": entry.get("score")})

    if not allow_reference and len(evidence_groups) != 1:
        raise SnapshotInvalid("ModelDial Luna rows do not share one evidence group")

    adapted = {
        "snapshot_id": batch_id,
        "published_at": published_at,
        "rows": rows,
        "source_mode": source_mode,
        "source_url": source_url,
        "snapshot_hash": payload["batch_sha256"],
    }
    if allow_reference:
        adapted.update({"benchmark_provider": pair[0], "benchmark_route": pair[1], "evidence_scope": "reference_only", "evidence_ids": evidence_ids})
    cost_candidates: dict[tuple[str, str], list[float | None]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        configuration = entry.get("model_configuration")
        if not isinstance(configuration, Mapping):
            continue
        model = configuration.get("canonical_model_id")
        effort = configuration.get("reasoning_effort")
        if model not in (LUNA_MODEL, REFERENCE_MODEL) or effort not in EFFORTS:
            continue
        if (
            configuration.get("provider_id") != "codex"
            or configuration.get("route_type") != "official_login"
            or entry.get("advisor_eligible") is not True
            or entry.get("score_integrity") != "first_party_controlled"
            or entry.get("route_identity") != "first_party_controlled"
            or entry.get("cost_coverage") != "complete"
            or entry.get("source_evidence_group_id") not in evidence_groups
        ):
            continue
        cost = _finite_cost(entry.get("estimated_api_cost_usd"))
        cost_candidates.setdefault((model, effort), []).append(cost)
    if pair == BENCHMARK_PAIRS[0]:
        adapted.update(_reference_cost_metadata(payload.get("pricing_snapshot_id"), cost_candidates))
    return validate_snapshot(adapted)


def adapt_modeldial_api(
    payload: Mapping[str, Any],
    *,
    source_url: str = MODELDIAL_API_URL,
    now: datetime | None = None,
    allow_reference: bool = False,
) -> dict[str, Any]:
    """Validate ModelDial API v1 and map its Luna rows to the selector contract."""

    if not isinstance(payload, Mapping):
        raise SnapshotInvalid("API_SCHEMA_INVALID: response must be an object")
    schema_version = payload.get("schemaVersion")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise SnapshotInvalid("API_SCHEMA_INVALID: schemaVersion is missing or malformed")
    if schema_version not in {"1.0", "1.1"}:
        raise SnapshotInvalid("API_SCHEMA_UNSUPPORTED: schemaVersion is not supported")
    if schema_version == "1.1" and payload.get("defaultRanking") != "overallRankings":
        raise SnapshotInvalid("ModelDial API v1.1 default ranking is invalid")

    source = payload.get("source")
    if not isinstance(source, Mapping) or source.get("kind") != "first_party_snapshot":
        raise SnapshotInvalid("ModelDial API lacks first-party provenance")

    batch = payload.get("batch")
    if not isinstance(batch, Mapping):
        raise SnapshotInvalid("ModelDial API batch must be an object")
    batch_id = batch.get("id")
    if not isinstance(batch_id, str) or not batch_id.strip():
        raise SnapshotInvalid("ModelDial API batch id is invalid")
    revision = batch.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise SnapshotInvalid("ModelDial API batch revision is invalid")

    published_at = _parse_published_at(batch.get("publishedAt"))
    published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    current = datetime.now(UTC) if now is None else now
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if published > current.astimezone(UTC) + API_CLOCK_SKEW:
        raise SnapshotInvalid("ModelDial API publication time is in the future")

    for key in (
        "questionPackVersion",
        "graderVersion",
        "evaluationProfile",
        "scoreBaselineId",
    ):
        value = batch.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SnapshotInvalid(f"ModelDial API batch lacks {key}")

    rankings = payload.get("rankings")
    if not isinstance(rankings, list):
        raise SnapshotInvalid("ModelDial API rankings must be a list")
    entry_count = batch.get("entryCount")
    if (
        isinstance(entry_count, bool)
        or not isinstance(entry_count, int)
        or entry_count != len(rankings)
    ):
        raise SnapshotInvalid("ModelDial API entryCount does not match rankings")
    batch_hash = batch.get("sha256")
    if not isinstance(batch_hash, str) or re.fullmatch(
        r"sha256:[0-9a-f]{64}", batch_hash
    ) is None:
        raise SnapshotInvalid("ModelDial API batch sha256 is invalid")

    rows = []
    cost_candidates: dict[tuple[str, str], list[float | None]] = {}
    pair = _luna_benchmark_pair(rankings) if allow_reference else BENCHMARK_PAIRS[0]
    for ranking in rankings:
        if not isinstance(ranking, Mapping):
            continue
        if ranking.get("provider") != pair[0] or ranking.get("route") != pair[1]:
            continue
        model = ranking.get("model")
        effort = ranking.get("reasoningEffort")
        if model not in (LUNA_MODEL, REFERENCE_MODEL) or effort not in EFFORTS:
            continue
        score = ranking.get("score")
        if schema_version == "1.1":
            backend_score = ranking.get("backendScore")
            if (
                ranking.get("scoreBasis") != "backend"
                or isinstance(score, bool)
                or not isinstance(score, (int, float))
                or isinstance(backend_score, bool)
                or not isinstance(backend_score, (int, float))
                or not math.isfinite(float(score))
                or not math.isfinite(float(backend_score))
                or float(score) != float(backend_score)
            ):
                raise SnapshotInvalid("ModelDial API v1.1 backend score identity is invalid")
        if model == LUNA_MODEL:
            rows.append({"model": LUNA_MODEL, "effort": effort, "score": score})
        cost = _finite_cost(ranking.get("estimatedReferenceCostUsd"))
        cost_candidates.setdefault((model, effort), []).append(cost)

    adapted = {
        "snapshot_id": batch_id,
        "published_at": published_at,
        "rows": rows,
        "source_mode": "modeldial_api_v1",
        "source_url": source_url,
        "snapshot_hash": batch_hash,
    }
    if allow_reference:
        adapted.update({"benchmark_provider": pair[0], "benchmark_route": pair[1], "evidence_scope": "reference_only"})
    if pair == BENCHMARK_PAIRS[0]:
        adapted.update(_reference_cost_metadata(batch.get("pricingSnapshotId"), cost_candidates))
    return validate_snapshot(adapted)


def _validated_modeldial_url(url: str) -> urllib.parse.ParseResult:
    try:
        parsed = urllib.parse.urlparse(url)
        scheme = parsed.scheme.lower()
        hostname = parsed.hostname
    except ValueError as exc:
        raise SnapshotInvalid("ModelDial URL is malformed") from exc
    if scheme != "https" or hostname not in MODELDIAL_ALLOWED_HOSTS:
        raise SnapshotInvalid("ModelDial URL is outside the HTTPS allowlist")
    try:
        username = parsed.username
        password = parsed.password
        port = parsed.port
    except ValueError as exc:
        raise SnapshotInvalid("ModelDial URL is malformed") from exc
    if username or password or port not in (None, 443):
        raise SnapshotInvalid("credentials and non-standard ports are forbidden")
    return parsed


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validated_modeldial_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch_bytes(url: str, *, expected_type: str, timeout: float) -> tuple[bytes, str]:
    _validated_modeldial_url(url)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": expected_type,
            "User-Agent": USER_AGENT,
        },
        method="GET",
    )
    response = urllib.request.build_opener(_SafeRedirectHandler()).open(
        request, timeout=timeout
    )
    with response:
        final_url = response.geturl()
        _validated_modeldial_url(final_url)
        content_type = response.headers.get_content_type()
        if content_type != expected_type:
            raise SnapshotInvalid(f"ModelDial endpoint did not return {expected_type}")
        body = response.read(MAX_SNAPSHOT_BYTES + 1)
        if len(body) > MAX_SNAPSHOT_BYTES:
            raise SnapshotInvalid("ModelDial snapshot exceeds the size limit")
    return body, final_url


def fetch_modeldial_snapshot(*, timeout: float = 15.0) -> dict[str, Any]:
    """Fetch ModelDial API v1, falling back to the official full snapshot."""

    try:
        body, final_url = _fetch_bytes(
            MODELDIAL_API_URL, expected_type="application/json", timeout=timeout
        )
        payload = json.loads(body.decode("utf-8"))
        return adapt_modeldial_api(payload, source_url=final_url)
    except (OSError, UnicodeError, json.JSONDecodeError, SnapshotInvalid):
        pass

    try:
        body, final_url = _fetch_bytes(
            MODELDIAL_SNAPSHOT_URL, expected_type="application/json", timeout=timeout
        )
        payload = json.loads(body.decode("utf-8"))
        return adapt_modeldial_snapshot(payload, source_url=final_url)
    except (OSError, UnicodeError, json.JSONDecodeError, SnapshotInvalid) as exc:
        raise SnapshotInvalid("both first-party ModelDial JSON sources failed") from exc


def _normalize_supported(supported_efforts: Iterable[str] | None) -> tuple[str, ...]:
    if supported_efforts is None:
        return EFFORTS
    requested = set(supported_efforts)
    unknown = requested.difference(EFFORTS)
    if unknown:
        raise SelectionUnavailable(
            f"unsupported local effort names: {', '.join(sorted(unknown))}"
        )
    supported = tuple(effort for effort in EFFORTS if effort in requested)
    if not supported:
        raise SelectionUnavailable("no locally supported Luna effort")
    return supported


def _winner(scores: Mapping[str, float], efforts: Iterable[str]) -> str:
    rank = {effort: index for index, effort in enumerate(EFFORTS)}
    return min(efforts, key=lambda effort: (-scores[effort], rank[effort]))


def select_snapshot(
    payload: Mapping[str, Any],
    *,
    supported_efforts: Iterable[str] | None = None,
    now: datetime | None = None,
    fallback: bool = False,
) -> dict[str, Any]:
    """Select the source winner and best locally supported stable Luna role."""

    snapshot = validate_snapshot(payload)
    supported = _normalize_supported(supported_efforts)
    source_effort = _winner(snapshot["scores"], EFFORTS)
    selected_effort = _winner(snapshot["scores"], supported)
    selected_at = _aware_bjt(now)

    profile = {
        "metadata_schema_version": METADATA_SCHEMA_VERSION,
        "source_winner_effort": source_effort,
        "source_winner_score": snapshot["scores"][source_effort],
        "selected_effort": selected_effort,
        "selected_score": snapshot["scores"][selected_effort],
        "selected_role": ROLE_BY_EFFORT[selected_effort],
        "capability_degraded": selected_effort != source_effort,
        "snapshot_id": snapshot["snapshot_id"],
        "published_at": snapshot["published_at"],
        "selected_at_bjt": selected_at.isoformat(),
        "selection_date_bjt": selected_at.date().isoformat(),
        "fallback": fallback,
    }
    for key in ("source_mode", "source_url", "snapshot_hash", "benchmark_provider", "benchmark_route", "evidence_scope", "evidence_ids"):
        if key in snapshot:
            profile[key] = snapshot[key]
    reference_costs = snapshot.get("reference_costs")
    if isinstance(reference_costs, Mapping):
        pair = reference_costs.get("by_effort", {}).get(selected_effort)
        if isinstance(pair, Mapping):
            luna_cost = pair["luna_cost_usd"]
            sol_cost = pair["sol_cost_usd"]
            profile["pricing_snapshot_id"] = snapshot["pricing_snapshot_id"]
            profile["reference_cost_comparison"] = {
                "metric": REFERENCE_COST_METRIC,
                "effort": selected_effort,
                "provider": "codex",
                "route": "official_login",
                "luna_cost_usd": luna_cost,
                "sol_cost_usd": sol_cost,
                "reduction_pct": round((1 - luna_cost / sol_cost) * 100, 1),
            }
    return profile


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _same_bjt_day(profile: Any, now: datetime) -> bool:
    if not _daily_profile_is_valid(profile):
        return False
    return _profile_date(profile) == now.date().isoformat()


@contextlib.contextmanager
def _selector_lock(state_root: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
    """Serialize one state-root selection without a daemon or external dependency."""

    state_root.mkdir(parents=True, exist_ok=True)
    lock_path = state_root / "selector.lock"
    deadline = time.monotonic() + timeout
    with lock_path.open("a+b") as handle:
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(b"\0")
            handle.flush()
        acquired = False
        try:
            while not acquired:
                try:
                    handle.seek(0)
                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise SelectionUnavailable("selector state lock timed out") from exc
                    time.sleep(0.05)
            yield
        finally:
            if acquired:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def ensure_daily_profile(
    live_snapshot: Mapping[str, Any] | None,
    *,
    state_dir: str | Path,
    supported_efforts: Iterable[str] | None = None,
    now: datetime | None = None,
    live_fetcher: Callable[[], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return today's profile, selecting once or falling back to the LKG."""

    selected_at = _aware_bjt(now)
    state_root = Path(state_dir)
    profile_path = state_root / "daily-profile.json"
    lkg_path = state_root / "last-good-profile.json"

    with _selector_lock(state_root):
        if profile_path.is_file():
            try:
                existing = _read_json(profile_path)
            except (OSError, json.JSONDecodeError):
                existing = None
            if _same_bjt_day(existing, selected_at):
                return dict(existing)

        if live_snapshot is None and live_fetcher is not None:
            try:
                live_snapshot = live_fetcher()
            except (OSError, SnapshotInvalid):
                live_snapshot = None

        if live_snapshot is not None:
            try:
                normalized_snapshot = validate_snapshot(live_snapshot)
                profile = select_snapshot(
                    normalized_snapshot,
                    supported_efforts=supported_efforts,
                    now=selected_at,
                    fallback=False,
                )
            except SnapshotInvalid:
                profile = None
            else:
                _write_json(lkg_path, {"snapshot": normalized_snapshot})
                _write_json(profile_path, profile)
                return profile

        try:
            lkg_record = _read_json(lkg_path)
            lkg_snapshot = lkg_record["snapshot"]
            profile = select_snapshot(
                lkg_snapshot,
                supported_efforts=supported_efforts,
                now=selected_at,
                fallback=True,
            )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, SnapshotInvalid) as exc:
            raise SelectionUnavailable(NO_PROFILE_STATUS) from exc

        _write_json(profile_path, profile)
        return profile


def _load_optional_snapshot(path: str | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    try:
        payload = _read_json(Path(path))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, Mapping):
        return None
    if payload.get("kind") == "first_party_snapshot":
        try:
            return adapt_modeldial_snapshot(payload, source_url=str(Path(path)))
        except SnapshotInvalid:
            return None
    if "schemaVersion" in payload:
        try:
            return adapt_modeldial_api(payload, source_url=str(Path(path)))
        except SnapshotInvalid:
            return None
    return payload


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json_safely(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _read_daily_profile(path: Path) -> tuple[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "MISSING", None
    except (OSError, UnicodeError):
        return "READ_FAILED", None

    try:
        return "OK", json.loads(text)
    except json.JSONDecodeError:
        return "INVALID_CONTENT", None


def _owned_block(path: Path, begin: str, end: str) -> bytes | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if text.count(begin) != 1 or text.count(end) != 1:
        return None
    start = text.index(begin)
    try:
        finish = text.index(end, start) + len(end)
    except ValueError:
        return None
    if finish < len(text) and text[finish] == "\r":
        finish += 1
    if finish < len(text) and text[finish] == "\n":
        finish += 1
    return text[start:finish].encode("utf-8")


def _owned_hash(manifest: Mapping[str, Any] | None, relative: str) -> str | None:
    if not isinstance(manifest, Mapping):
        return None
    value = manifest.get("owned_files", {}).get(relative)
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping) and isinstance(value.get("sha256"), str):
        return value["sha256"]
    return None


def _owned_skill_hash(manifest: Mapping[str, Any] | None, relative: str) -> str | None:
    if not isinstance(manifest, Mapping):
        return None
    value = manifest.get("owned_skill_files", {}).get(relative)
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping) and isinstance(value.get("sha256"), str):
        return value["sha256"]
    return None


def _block_hash(manifest: Mapping[str, Any] | None, filename: str) -> str | None:
    if not isinstance(manifest, Mapping):
        return None
    value = manifest.get("owned_blocks", {}).get(filename)
    return value.get("sha256") if isinstance(value, Mapping) else None


def _safe_identifier(value: Any, *, default: str = "Not available") -> str:
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._:+-]{1,200}", value):
        return value
    return default


def _profile_date(profile: Mapping[str, Any]) -> str | None:
    selection_date = profile.get("selection_date_bjt")
    if isinstance(selection_date, str):
        try:
            return datetime.fromisoformat(selection_date).date().isoformat()
        except ValueError:
            pass
    selected_at = profile.get("selected_at_bjt")
    if not isinstance(selected_at, str):
        return None
    try:
        parsed = datetime.fromisoformat(selected_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(BJT).date().isoformat()


def _daily_profile_is_valid(profile: Any) -> bool:
    if not isinstance(profile, Mapping):
        return False
    effort = profile.get("selected_effort")
    if effort not in EFFORTS or profile.get("selected_role") != ROLE_BY_EFFORT[effort]:
        return False
    if profile.get("source_winner_effort") not in EFFORTS:
        return False
    if not isinstance(profile.get("fallback"), bool) or not isinstance(
        profile.get("capability_degraded"), bool
    ):
        return False
    selected_at = profile.get("selected_at_bjt")
    if not isinstance(selected_at, str):
        return False
    try:
        parsed = datetime.fromisoformat(selected_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return False
    selected_date = parsed.astimezone(BJT).date().isoformat()
    selection_date = profile.get("selection_date_bjt")
    if selection_date is not None:
        if not isinstance(selection_date, str):
            return False
        try:
            normalized_date = datetime.fromisoformat(selection_date).date().isoformat()
        except ValueError:
            return False
        if normalized_date != selected_date:
            return False
    return True


def _project_override_present(project_root: Path) -> bool:
    override = project_root / "AGENTS.override.md"
    try:
        if override.is_file() and override.read_text(encoding="utf-8").strip():
            return True
    except (OSError, UnicodeError):
        return True
    agents = project_root / ".codex" / "agents"
    try:
        if agents.is_dir() and any((agents / name).exists() for name in WORKER_AGENT_FILES):
            return True
    except OSError:
        return True
    config = project_root / ".codex" / "config.toml"
    try:
        if config.is_file():
            value = tomllib.loads(config.read_text(encoding="utf-8"))
            if isinstance(value.get("agents"), Mapping):
                return True
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return True
    return False


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if not isinstance(value, str):
        return value
    forbidden = (
        r"(?i)bearer",
        r"(?i)token=",
        r"(?i)api_key=",
        r"(?i)sk-",
        r"(?i)ghp_",
        r"(?i)https?://",
        r"(?i)(?:^|\s)[a-z]:[\\/]",
        r"^\\\\",
    )
    return "Redacted" if any(re.search(pattern, value) for pattern in forbidden) else value


def read_status(
    *,
    codex_home: str | Path | None,
    state_dir: str | Path,
    project_dir: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Read installed health without network, selector locks, writes, or Luna probes."""

    current = _aware_bjt(now)
    home = (
        Path(codex_home).resolve(strict=False)
        if codex_home is not None
        else (Path.home() / ".codex").resolve(strict=False)
    )
    state_root = Path(state_dir).resolve(strict=False)
    project_root = (
        Path(project_dir).resolve(strict=False) if project_dir is not None else None
    )
    misconfigured = []
    unavailable = []
    degraded = []

    manifest_path = home / MANIFEST_RELATIVE
    manifest: Mapping[str, Any] | None = None
    if not manifest_path.is_file():
        manifest_status = "Missing"
        misconfigured.append("MANIFEST_MISSING")
    else:
        candidate = _read_json_safely(manifest_path)
        schema_version = (
            candidate.get("schema_version")
            if isinstance(candidate, Mapping)
            else None
        )
        if (
            not isinstance(candidate, Mapping)
            or type(schema_version) is not int
            or schema_version not in {1, 2, 3}
            or not isinstance(candidate.get("version"), str)
            or not isinstance(candidate.get("owned_files"), Mapping)
            or not isinstance(candidate.get("owned_blocks"), Mapping)
            or (
                schema_version in {2, 3}
                and (
                    not isinstance(candidate.get("owned_skill_files"), Mapping)
                    or not isinstance(candidate.get("skills_root"), str)
                    or not candidate["skills_root"].strip()
                )
            )
        ):
            manifest_status = "Invalid"
            misconfigured.append("MANIFEST_INVALID")
        else:
            manifest = candidate
            manifest_status = "Ready"

    selector_path = home / "sol-luna-v4" / "selector.py"
    selector_status = "Ready"
    try:
        selector_bytes = selector_path.read_bytes() if selector_path.is_file() else None
    except OSError:
        selector_bytes = None
    if (
        selector_bytes is None
        or _owned_hash(manifest, "sol-luna-v4/selector.py")
        != _sha256_bytes(selector_bytes)
    ):
        selector_status = "Ownership mismatch" if selector_bytes is not None else "Missing"
        misconfigured.append("SELECTOR_OWNERSHIP_MISMATCH")
    if manifest and manifest.get("schema_version") == 3:
        module_path = home / "sol-luna-v4" / "worker_selector.py"
        try:
            module_bytes = module_path.read_bytes()
        except OSError:
            module_bytes = None
        if module_bytes is None or _owned_hash(manifest, "sol-luna-v4/worker_selector.py") != _sha256_bytes(module_bytes):
            selector_status = "Ownership mismatch" if module_bytes is not None else "Missing"
            misconfigured.append("WORKER_MODULE_OWNERSHIP_MISMATCH")

    policy_path = home / "AGENTS.md"
    policy_block = _owned_block(policy_path, AGENTS_BEGIN, AGENTS_END)
    if not policy_path.is_file() or policy_block is None:
        global_policy_status = "Missing"
        misconfigured.append("GLOBAL_POLICY_MISSING")
    elif _block_hash(manifest, "AGENTS.md") != _sha256_bytes(policy_block):
        global_policy_status = "Ownership mismatch"
        misconfigured.append("GLOBAL_POLICY_OWNERSHIP_MISMATCH")
    else:
        global_policy_status = "Ready"
    override_path = home / "AGENTS.override.md"
    try:
        global_override = (
            override_path.is_file()
            and bool(override_path.read_text(encoding="utf-8").strip())
        )
    except (OSError, UnicodeError):
        global_override = True
    if global_override:
        misconfigured.append("GLOBAL_AGENTS_OVERRIDE_PRESENT")

    config_path = home / "config.toml"
    config: Mapping[str, Any] | None = None
    config_block = _owned_block(config_path, CONFIG_BEGIN, CONFIG_END)
    if not config_path.is_file():
        config_status = "Missing"
        misconfigured.append("CONFIG_MISSING")
    else:
        try:
            parsed_config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            parsed_config = None
        if not isinstance(parsed_config, Mapping):
            config_status = "Invalid"
            misconfigured.append("CONFIG_INVALID")
        elif config_block is None or _block_hash(manifest, "config.toml") != _sha256_bytes(
            config_block
        ):
            config_status = "Ownership mismatch"
            misconfigured.append("CONFIG_OWNERSHIP_MISMATCH")
            config = parsed_config
        else:
            config_status = "Ready"
            config = parsed_config

    agents_config = config.get("agents") if isinstance(config, Mapping) else None
    max_parallel: int | str = "Invalid"
    if isinstance(agents_config, Mapping):
        if agents_config.get("enabled") is not True:
            misconfigured.append("AGENTS_DISABLED")
        configured_max = agents_config.get("max_concurrent_threads_per_session")
        if isinstance(configured_max, bool) or not isinstance(configured_max, int) or configured_max != (6 if manifest and manifest.get("schema_version") == 3 else 3):
            misconfigured.append("MAX_PARALLEL_INVALID")
        else:
            max_parallel = configured_max
    elif config is not None:
        misconfigured.extend(["AGENTS_DISABLED", "MAX_PARALLEL_INVALID"])

    agents_ready = 0
    missing_agents = False
    invalid_agents = False
    ownership_agents = False
    expected_agents = WORKER_AGENT_FILES if manifest and manifest.get("schema_version") == 3 else STABLE_AGENT_FILES
    if manifest and manifest.get("schema_version") == 3:
        owned_agents = {key for key in manifest["owned_files"] if key.startswith("agents/")}
        if owned_agents != {f"agents/{name}" for name in expected_agents}:
            misconfigured.append("AGENT_INVENTORY_INVALID")
        expected_files = {f"agents/{name}" for name in expected_agents} | {
            "sol-luna-v4/selector.py", "sol-luna-v4/worker_selector.py",
        }
        if set(manifest["owned_files"]) != expected_files:
            misconfigured.append("PAYLOAD_INVENTORY_INVALID")
    for filename in expected_agents:
        family, effort = filename.removesuffix(".toml").split("-", 1)
        relative = f"agents/{filename}"
        path = home / relative
        if not path.is_file():
            missing_agents = True
            continue
        try:
            data = path.read_bytes()
            payload = tomllib.loads(data.decode("utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            invalid_agents = True
            continue
        leaf = payload.get("agents")
        if (
            payload.get("model") != (LUNA_MODEL if family == "luna" else REFERENCE_MODEL)
            or payload.get("name") != f"{family}_{effort}"
            or payload.get("model_reasoning_effort") != effort
            or not isinstance(leaf, Mapping)
            or leaf.get("enabled") is not False
        ):
            invalid_agents = True
            continue
        if _owned_hash(manifest, relative) != _sha256_bytes(data):
            ownership_agents = True
            continue
        agents_ready += 1
    if missing_agents:
        misconfigured.append("AGENT_SET_INCOMPLETE")
    if invalid_agents:
        misconfigured.extend(
            [
                "AGENT_PAYLOAD_INVALID",
                (
                    "LEAF_CONFIG_INVALID"
                    if manifest and manifest.get("schema_version") == 3
                    else "NATIVE_LEAF_INVALID"
                ),
            ]
        )
    if ownership_agents:
        misconfigured.append("AGENT_OWNERSHIP_MISMATCH")
    leaf_config = "Ready" if agents_ready == len(expected_agents) else "Invalid"

    skills_ready = 0
    skills_expected = 0
    skills_status = "Not managed"
    if manifest and manifest.get("schema_version") in {2, 3}:
        expected_skills = WORKER_SKILL_FILES if manifest["schema_version"] == 3 else STABLE_SKILL_FILES
        skills_expected = len(expected_skills)
        skills_status = "Ready"
        if set(manifest.get("owned_skill_files", {})) != set(expected_skills):
            skills_status = "Invalid"
            misconfigured.append("SKILL_INVENTORY_INVALID")
        raw_skills_root = manifest.get("skills_root")
        try:
            candidate_root = Path(raw_skills_root).expanduser()
            skills_root = (
                candidate_root.resolve(strict=False)
                if candidate_root.is_absolute()
                else None
            )
        except (TypeError, OSError):
            skills_root = None
        if skills_root is None:
            skills_status = "Invalid"
            misconfigured.append("SKILLS_ROOT_INVALID")
        else:
            for relative in expected_skills:
                path = skills_root.joinpath(*Path(relative).parts)
                try:
                    data = path.read_bytes() if path.is_file() else None
                except OSError:
                    data = None
                if data is None:
                    skills_status = "Missing"
                    misconfigured.append("SKILL_SET_INCOMPLETE")
                    continue
                if _owned_skill_hash(manifest, relative) != _sha256_bytes(data):
                    skills_status = "Ownership mismatch"
                    misconfigured.append("SKILL_OWNERSHIP_MISMATCH")
                    continue
                skills_ready += 1

    project_override_status = "Not checked"
    if project_root is not None:
        if _project_override_present(project_root):
            project_override_status = "Override present"
            misconfigured.append("PROJECT_OVERRIDE_PRESENT")
        else:
            project_override_status = "Clear"

    profile_path = state_root / "daily-profile.json"
    selection_initialized = False
    profile: Mapping[str, Any] | None = None
    profile_read_status, candidate_profile = _read_daily_profile(profile_path)
    if profile_read_status == "READ_FAILED":
        misconfigured.append("DAILY_PROFILE_READ_FAILED")
    elif profile_read_status == "INVALID_CONTENT":
        unavailable.append("DAILY_PROFILE_INVALID")
    elif profile_read_status == "OK":
        if not isinstance(candidate_profile, Mapping):
            unavailable.append("DAILY_PROFILE_INVALID")
        else:
            profile_date = _profile_date(candidate_profile)
            if profile_date is None:
                unavailable.append("DAILY_PROFILE_INVALID")
            elif profile_date == current.date().isoformat():
                if not _daily_profile_is_valid(candidate_profile):
                    unavailable.append("DAILY_PROFILE_INVALID")
                else:
                    selection_initialized = True
                    profile = candidate_profile
                    if agents_ready != len(expected_agents):
                        unavailable.append("DAILY_ROLE_UNAVAILABLE")
                    if profile.get("fallback"):
                        degraded.append("LKG_FALLBACK_ACTIVE")
                    if profile.get("capability_degraded"):
                        degraded.append("CAPABILITY_DEGRADED")

    worker_profile = None
    if manifest and manifest.get("schema_version") == 3:
        worker_read, raw_worker = _read_daily_profile(state_root / "worker-profile.json")
        if worker_read == "READ_FAILED":
            misconfigured.append("WORKER_PROFILE_READ_FAILED")
        elif worker_read == "INVALID_CONTENT" or (worker_read == "OK" and not _worker_record_valid(raw_worker)):
            unavailable.append("WORKER_PROFILE_INVALID")
        elif worker_read == "OK" and _profile_date(raw_worker) == current.date().isoformat():
            worker_profile = raw_worker
            # A current Worker profile is authoritative for schema 3. An unused
            # legacy daily file must not contaminate independent family health.
            misconfigured = [reason for reason in misconfigured if reason != "DAILY_PROFILE_READ_FAILED"]
            unavailable = [reason for reason in unavailable if reason not in ("DAILY_PROFILE_INVALID", "DAILY_ROLE_UNAVAILABLE")]
            degraded = [reason for reason in degraded if reason not in ("LKG_FALLBACK_ACTIVE", "CAPABILITY_DEGRADED")]
            profile = None
            luna_choice = raw_worker["luna"]
            if luna_choice["status"] == "ready":
                profile = luna_choice
            selection_initialized = any(raw_worker[name]["status"] == "ready" for name in ("sol", "luna"))
            for name in ("sol", "luna"):
                choice = raw_worker[name]
                if choice["status"] == "unavailable":
                    degraded.append(f"{name.upper()}_SELECTION_UNAVAILABLE")
                elif choice.get("fallback"):
                    degraded.append("LKG_FALLBACK_ACTIVE")
                if choice.get("capability_degraded"):
                    degraded.append("CAPABILITY_DEGRADED")
            if not selection_initialized:
                unavailable.append("NO_WORKER_PROFILE_AVAILABLE")

    if misconfigured:
        health = "Misconfigured"
        reason_codes = misconfigured + unavailable + degraded
    elif unavailable:
        health = "Unavailable"
        reason_codes = unavailable + degraded
    elif degraded:
        health = "Degraded"
        reason_codes = degraded
    elif selection_initialized:
        health = "Healthy"
        reason_codes = ["OK"]
    else:
        health = "Healthy"
        reason_codes = ["TODAY_SELECTION_NOT_INITIALIZED"]

    comparison = profile.get("reference_cost_comparison") if profile else None
    reduction = None
    if isinstance(comparison, Mapping):
        value = comparison.get("reduction_pct")
        if (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(float(value))
            and 0 <= float(value) <= 100
        ):
            reduction = float(value)

    source_labels = {
        "modeldial_api_v1": "ModelDial API v1",
        "live_json": "ModelDial Full Snapshot",
    }
    raw_source = profile.get("source_mode") if profile else None
    source_mode = source_labels.get(raw_source, "Not initialized")
    source_commit = manifest.get("source_commit") if manifest else None
    verified_commit_sha = (
        source_commit
        if isinstance(source_commit, str)
        and re.fullmatch(r"[0-9a-fA-F]{40}", source_commit)
        else "Not available"
    )
    installed_version = _safe_identifier(
        manifest.get("version") if manifest else None,
        default="Not available",
    )
    diagnostic = {
        "diagnostic_schema_version": 4 if manifest and manifest.get("schema_version") == 3 else STATUS_SCHEMA_VERSION,
        "generated_at_utc": current.astimezone(UTC).isoformat(),
        "os": _safe_identifier(platform.system(), default="Unknown"),
        "architecture": _safe_identifier(platform.machine(), default="Unknown"),
        "codex_version": "Not checked",
        "python_version": _safe_identifier(platform.python_version(), default="Unknown"),
        "installed_version": installed_version,
        "verified_commit_sha": verified_commit_sha,
        "manifest_status": manifest_status,
        "global_policy_status": global_policy_status,
        "selector_status": selector_status,
        "agents_ready": agents_ready,
        "agents_expected": len(expected_agents),
        "skills_ready": skills_ready,
        "skills_expected": skills_expected,
        "skills_status": skills_status,
        "config_status": config_status,
        "max_parallel": max_parallel,
        "today_bjt": current.date().isoformat(),
        "selection_initialized": selection_initialized,
        "selected_role": profile.get("selected_role", "Not selected") if profile else "Not selected",
        "selected_effort": profile.get("selected_effort", "Not selected") if profile else "Not selected",
        "source_mode": source_mode,
        "fallback": profile.get("fallback", "N/A") if profile else "N/A",
        "capability_degraded": profile.get("capability_degraded", "N/A") if profile else "N/A",
        "snapshot_id": _safe_identifier(profile.get("snapshot_id") if profile else None),
        "pricing_snapshot_id": _safe_identifier(
            profile.get("pricing_snapshot_id") if profile else None
        ),
        "reference_cost_metadata_available": reduction is not None,
        "reference_cost_reduction_pct": reduction if reduction is not None else "Not available",
        "project_override_status": project_override_status,
        "health": health,
        "reason_codes": list(dict.fromkeys(reason_codes)),
        "locations": {
            "codex_home": "<CODEX_HOME>",
            "state_dir": "<STATE_DIR>",
            "project_root": "<PROJECT_ROOT>" if project_root is not None else "Not checked",
        },
    }
    if manifest and manifest.get("schema_version") == 3:
        # Read-only configuration evidence is distinct from native runtime proof.
        diagnostic.update({
            "coordinator_model": "User selected; not observed",
            "leaf_config": leaf_config,
            "native_delegation": "Not checked",
            "native_tool_isolation": "Not checked",
            "native_delegation_guard": "Not checked",
            "runtime_max_parallel": "Not checked",
            "workers": {"luna": {"status": "Not initialized"}, "sol": {"status": "Not initialized", "views": {}}},
        })
        if worker_profile:
            whitelist = ("status", "selected_role", "selected_effort", "selection_mode", "fallback", "capability_degraded", "source_winner_effort", "quality_gap", "benchmark_provider", "benchmark_route", "evidence_scope")
            def safe_choice(row):
                result = {key: row[key] for key in whitelist if key in row}
                source = row.get("source_metadata")
                if isinstance(source, Mapping):
                    result["source_metadata"] = {
                        key: source[key] for key in ("name", "kind", "generated_at", "group_id", "group_published_at", "source_array", "score_field")
                        if key in source and isinstance(source[key], str)
                    }
                elif isinstance(row.get("snapshot_id"), str):
                    result["source_metadata"] = {
                        key: row[key] for key in ("snapshot_id", "published_at", "source_mode")
                        if key in row and isinstance(row[key], str)
                    }
                return result
            diagnostic["workers"]["luna"] = safe_choice(worker_profile["luna"])
            diagnostic["workers"]["sol"] = safe_choice(worker_profile["sol"])
            diagnostic["workers"]["sol"]["views"] = {
                view: safe_choice(row) for view, row in worker_profile["sol"].get("views", {}).items()
                if view in ("general", "backend", "frontend", "reasoning")
            }
    else:
        # Preserve the historical schema-1/2 diagnostic field contract.
        diagnostic["native_leaf"] = leaf_config
    return _sanitize_value(diagnostic)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", help="Path to one published snapshot JSON file")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch the verified first-party ModelDial JSON source",
    )
    parser.add_argument("--state-dir", default=".var", help="Repo-local state directory")
    parser.add_argument(
        "--ensure-daily",
        action="store_true",
        help="Ensure one valid profile for the current Beijing calendar day",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--print-role",
        action="store_true",
        help="Print only the selected native custom-agent role",
    )
    output.add_argument(
        "--print-selection",
        action="store_true",
        help="Print only receipt-safe structured selection metadata",
    )
    output.add_argument(
        "--status-json",
        action="store_true",
        help="Print one read-only, sanitized Sol/Luna diagnostic snapshot",
    )
    parser.add_argument("--workers", action="store_true", help="Select both Worker families with isolated daily state")
    parser.add_argument("--refresh-workers", action="store_true", help="Explicitly refresh Worker choices for subsequent delegations")
    parser.add_argument("--sol-supported", default=",".join(EFFORTS), help="Locally supported Sol efforts")
    parser.add_argument("--codex-home", help="Installed CODEX_HOME to inspect read-only")
    parser.add_argument("--project-dir", help="Optional project root to inspect read-only")
    parser.add_argument(
        "--supported",
        default=",".join(EFFORTS),
        help="Comma-separated locally supported efforts",
    )
    args = parser.parse_args(argv)
    if args.status_json:
        diagnostic = read_status(
            codex_home=args.codex_home,
            state_dir=args.state_dir,
            project_dir=args.project_dir,
        )
        print(json.dumps(diagnostic, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.live and args.snapshot:
        parser.error("--live and --snapshot are mutually exclusive")
    supported = tuple(item.strip() for item in args.supported.split(",") if item.strip())
    if args.refresh_workers and not args.workers:
        parser.error("--refresh-workers requires --workers")

    if args.workers:
        if args.print_role:
            parser.error("--workers requires structured output, not --print-role")
        try:
            data = _read_json(Path(args.snapshot)) if args.snapshot else None
            profile = ensure_worker_profile(
                data, state_dir=args.state_dir, supported_luna=supported,
                supported_sol=tuple(x.strip() for x in args.sol_supported.split(",") if x.strip()),
                live_fetcher=fetch_worker_data if args.snapshot is None else None,
                refresh=args.refresh_workers,
            )
        except (OSError, ValueError, UnicodeError, SelectionUnavailable):
            print("NO_WORKER_PROFILE_AVAILABLE")
            return 3
        print(json.dumps(profile, ensure_ascii=False, sort_keys=True))
        return 0 if any(profile[name]["status"] == "ready" for name in ("sol", "luna")) else 3

    live_snapshot = None if args.live else _load_optional_snapshot(args.snapshot)
    should_fetch = args.live or (args.ensure_daily and args.snapshot is None)
    live_fetcher = fetch_modeldial_snapshot if should_fetch else None

    try:
        profile = ensure_daily_profile(
            live_snapshot,
            state_dir=args.state_dir,
            supported_efforts=supported,
            live_fetcher=live_fetcher,
        )
    except (SelectionUnavailable, ValueError):
        print(NO_PROFILE_STATUS)
        return 3

    if args.print_role:
        print(profile["selected_role"])
    elif args.print_selection:
        selection = {
            key: profile[key]
            for key in (
                "selected_role",
                "selected_effort",
                "fallback",
                "capability_degraded",
                "source_winner_effort",
            )
        }
        if "reference_cost_comparison" in profile:
            selection["reference_cost_comparison"] = profile[
                "reference_cost_comparison"
            ]
        print(json.dumps(selection, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(profile, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import json
import unittest
from pathlib import Path

from src.worker_selector import (
    adapt_sol_api,
    adapt_sol_full_snapshot,
    enrich_sol_backend_costs,
    select_sol,
)


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modeldial"


def load_fixture(name):
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_api_fixture_maps_four_independent_views_and_groups():
    adapted = adapt_sol_api(load_fixture("worker-api-v1.1.json"))
    assert set(adapted["views"]) == {"general", "backend", "frontend", "reasoning"}
    assert all(view["status"] == "ready" for view in adapted["views"].values())
    assert adapted["views"]["general"]["score_field"] == "overallScore"
    assert adapted["views"]["backend"]["score_field"] == "score"
    assert adapted["views"]["frontend"]["score_field"] == "frontendScore"
    assert adapted["views"]["reasoning"]["score_field"] == "knowledgeScore"
    groups = {view["group_id"] for view in adapted["views"].values()}
    assert len(groups) == 4


def test_reference_api_identity_is_preserved_through_root_items_and_selection():
    adapted = adapt_sol_api(load_fixture("reference-api-v1.1.json"))
    assert adapted["target"] == {
        "model": "gpt-5.6-sol",
        "provider": "cloudflare-reference",
        "route": "custom_endpoint",
    }
    assert adapted["benchmark_provider"] == "cloudflare-reference"
    assert adapted["benchmark_route"] == "custom_endpoint"
    assert adapted["evidence_scope"] == "reference_only"
    assert all(view["status"] == "ready" for view in adapted["views"].values())
    assert all(
        (item["provider"], item["route"]) == ("cloudflare-reference", "custom_endpoint")
        for view in adapted["views"].values()
        for item in view["items"]
    )
    selected = select_sol(adapted)
    assert selected["benchmark_provider"] == "cloudflare-reference"
    assert selected["benchmark_route"] == "custom_endpoint"
    assert selected["evidence_scope"] == "reference_only"
    assert selected["views"]["backend"]["source_metadata"]["benchmark_provider"] == "cloudflare-reference"


def test_official_pair_is_preferred_only_when_complete_and_pair_is_snapshot_wide():
    payload = load_fixture("reference-api-v1.1.json")
    official = load_fixture("worker-api-v1.1.json")
    for name in ("overallRankings", "rankings"):
        partial_official = [row for row in official[name] if row["reasoningEffort"] != "low"]
        payload[name].extend(partial_official)
    payload["batch"]["entryCount"] = len(payload["rankings"])
    payload["overallBatch"]["entryCount"] = len(payload["overallRankings"])
    payload["batch"]["id"] = "mixed-reference-and-partial-official"
    payload["overallBatch"]["id"] = "mixed-reference-and-partial-official-overall"
    adapted = adapt_sol_api(payload)
    assert adapted["target"]["provider"] == "cloudflare-reference"
    assert all(view["status"] == "ready" for view in adapted["views"].values())

    payload = load_fixture("worker-api-v1.1.json")
    reference = load_fixture("reference-api-v1.1.json")
    payload["rankings"] = reference["rankings"]
    adapted = adapt_sol_api(payload)
    assert adapted["target"]["provider"] == "codex"
    assert adapted["views"]["general"]["status"] == "ready"
    assert adapted["views"]["backend"]["status"] == "unavailable"

    full = load_fixture("reference-full-snapshot.json")
    official_full = load_fixture("worker-cost-covered.json")
    official_full["entries"][0]["score_integrity"] = "untrusted"
    full["entries"].extend(official_full["entries"])
    adapted_full = adapt_sol_full_snapshot(full)
    assert adapted_full["target"]["provider"] == "cloudflare-reference"
    assert adapted_full["views"]["backend"]["status"] == "ready"


def test_rows_from_two_pairs_are_not_merged_to_fill_five_efforts():
    payload = load_fixture("worker-api-v1.1.json")
    for row in payload["rankings"][:2]:
        row["provider"] = "cloudflare-reference"
        row["route"] = "custom_endpoint"
        row["id"] = row["id"].replace("codex:", "cloudflare-reference:")
    adapted = adapt_sol_api(payload)
    assert adapted["target"]["provider"] == "codex"
    assert adapted["views"]["backend"]["status"] == "unavailable"
    assert adapted["views"]["backend"]["reason"].startswith("incomplete_efforts:")


def test_unlisted_provider_or_route_is_rejected_for_that_view():
    for field, value in (("provider", "unlisted-provider"), ("route", "unlisted-route")):
        payload = load_fixture("reference-api-v1.1.json")
        for row in payload["rankings"]:
            row[field] = value
        adapted = adapt_sol_api(payload)
        assert adapted["views"]["backend"]["status"] == "unavailable"
        assert adapted["views"]["general"]["status"] == "ready"


def test_wrong_route_is_unavailable_without_invalidating_other_views():
    payload = load_fixture("worker-api-v1.1.json")
    for row in payload["rankings"]:
        row["route"] = "custom_endpoint"
    adapted = adapt_sol_api(payload)
    assert adapted["views"]["backend"]["status"] == "unavailable"
    assert adapted["views"]["general"]["status"] == "ready"


def test_partial_axis_and_nonfinite_or_boolean_scores_fail_only_that_view():
    payload = load_fixture("worker-api-v1.1.json")
    payload["overallRankings"][0]["frontendScore"] = float("nan")
    adapted = adapt_sol_api(payload)
    assert adapted["views"]["frontend"]["status"] == "unavailable"
    assert adapted["views"]["reasoning"]["status"] == "ready"

    payload = load_fixture("worker-api-v1.1.json")
    payload["overallRankings"][0]["overallScore"] = True
    adapted = adapt_sol_api(payload)
    assert adapted["views"]["general"]["status"] == "unavailable"


def test_missing_effort_makes_only_its_view_unavailable():
    payload = load_fixture("worker-api-v1.1.json")
    payload["rankings"] = [
        row for row in payload["rankings"] if row["reasoningEffort"] != "low"
    ]
    payload["batch"]["entryCount"] = len(payload["rankings"])
    adapted = adapt_sol_api(payload)
    assert adapted["views"]["backend"]["status"] == "unavailable"
    assert adapted["views"]["general"]["status"] == "ready"


def test_source_winner_and_deterministic_quality_tie_order():
    payload = load_fixture("worker-api-v1.1.json")
    for row in payload["rankings"]:
        if row["reasoningEffort"] in ("high", "max"):
            row["score"] = row["backendScore"] = 93
    selected = select_sol(adapt_sol_api(payload))["views"]["backend"]
    assert selected["selected_effort"] == "high"
    assert selected["source_winner_effort"] == "high"
    assert selected["selection_mode"] == "quality_only"
    assert selected["capability_degraded"] is False


def test_supported_efforts_report_missing_source_winner_as_capability_degraded():
    selected = select_sol(
        adapt_sol_api(load_fixture("worker-api-v1.1.json")),
        supported_efforts=("low", "medium"),
    )["views"]["backend"]
    assert selected["selected_effort"] == "medium"
    assert selected["source_winner_effort"] == "max"
    assert selected["capability_degraded"] is True


def test_uncovered_api_estimates_never_enable_cost_optimization():
    selected = select_sol(adapt_sol_api(load_fixture("worker-api-v1.1.json")))["views"]["backend"]
    assert selected["selected_effort"] == "max"
    assert selected["selection_mode"] == "quality_only"
    assert selected["capability_degraded"] is False


def test_full_snapshot_uses_nested_model_configuration_and_integrity_gates():
    payload = load_fixture("worker-cost-covered.json")
    adapted = adapt_sol_full_snapshot(payload)
    backend = adapted["views"]["backend"]
    assert adapted["target"]["provider"] == "codex"
    assert adapted["target"]["route"] == "official_login"
    assert adapted["evidence_scope"] == "reference_only"
    assert backend["status"] == "ready"
    assert backend["group_id"] == "worker-cost-evidence-001"
    assert backend["items"][0]["row_id"].startswith("cloudflare-reference:")

    payload["entries"][0]["advisor_eligible"] = False
    adapted = adapt_sol_full_snapshot(payload)
    assert adapted["views"]["backend"]["status"] == "unavailable"


def test_reference_full_snapshot_accepts_and_preserves_per_row_evidence_ids():
    payload = load_fixture("reference-full-snapshot.json")
    adapted = adapt_sol_full_snapshot(payload)
    backend = adapted["views"]["backend"]
    assert adapted["target"]["provider"] == "cloudflare-reference"
    assert adapted["target"]["route"] == "custom_endpoint"
    assert backend["status"] == "ready"
    assert backend["group_id"] == payload["batch_id"]
    for item in backend["items"]:
        source_row = next(
            entry for entry in payload["entries"]
            if entry["model_configuration"]["reasoning_effort"] == item["effort"]
        )
        assert item["score_group_id"] == payload["batch_id"]
        assert item["source_evidence_group_id"] == source_row["source_evidence_group_id"]
        assert (item["provider"], item["route"]) == ("cloudflare-reference", "custom_endpoint")


def test_full_snapshot_unknown_route_and_invalid_evidence_fail_closed():
    payload = load_fixture("reference-full-snapshot.json")
    payload["entries"][0]["model_configuration"]["route_type"] = "unlisted-route"
    adapted = adapt_sol_full_snapshot(payload)
    assert adapted["views"]["backend"]["status"] == "unavailable"

    payload = load_fixture("reference-full-snapshot.json")
    payload["entries"][-1]["source_evidence_group_id"] = " "
    adapted = adapt_sol_full_snapshot(payload)
    assert adapted["views"]["backend"]["status"] == "unavailable"
    assert adapted["views"]["backend"]["reason"].startswith("missing_evidence_group:")


def test_complete_matching_costs_optimize_inside_inclusive_two_point_band():
    api = adapt_sol_api(load_fixture("worker-api-v1.1.json"))
    full = load_fixture("worker-cost-covered.json")
    enriched = enrich_sol_backend_costs(api, full)
    selected = select_sol(enriched)["views"]["backend"]
    assert selected["quality_band_efforts"] == ["high", "max"]
    assert selected["selected_effort"] == "high"
    assert selected["selection_mode"] == "cost_optimized"
    assert selected["capability_degraded"] is False


def test_cost_batch_mismatch_fails_soft_to_quality_only():
    api = adapt_sol_api(load_fixture("worker-api-v1.1.json"))
    full = load_fixture("worker-cost-covered.json")
    full["pricing_snapshot_id"] = "other-pricing"
    enriched = enrich_sol_backend_costs(api, full)
    selected = select_sol(enriched)["views"]["backend"]
    assert selected["selected_effort"] == "max"
    assert selected["selection_mode"] == "quality_only"


def test_reference_cost_enrichment_requires_exact_pair_batch_hash_count_and_scores():
    api = adapt_sol_api(load_fixture("reference-api-v1.1.json"))
    matching_full = load_fixture("reference-full-snapshot.json")
    selected = select_sol(enrich_sol_backend_costs(api, matching_full))["views"]["backend"]
    assert selected["selection_mode"] == "cost_optimized"
    assert selected["benchmark_provider"] == "cloudflare-reference"
    assert selected["benchmark_route"] == "custom_endpoint"
    assert selected["evidence_scope"] == "reference_only"

    for field, value in (
        ("batch_id", "another-batch"),
        ("batch_sha256", "sha256:" + "f" * 64),
        ("question_pack_version", "another-question-pack-version"),
        ("pricing_snapshot_id", "another-pricing-snapshot"),
    ):
        full = load_fixture("reference-full-snapshot.json")
        full[field] = value
        result = enrich_sol_backend_costs(api, full)
        selected = select_sol(result)["views"]["backend"]
        assert selected["selection_mode"] == "quality_only"

    full = load_fixture("reference-full-snapshot.json")
    full["entries"].append({"id": "unrelated-entry"})
    selected = select_sol(enrich_sol_backend_costs(api, full))["views"]["backend"]
    assert selected["selection_mode"] == "quality_only"

    full = load_fixture("reference-full-snapshot.json")
    full["entries"][0]["score"] += 1
    selected = select_sol(enrich_sol_backend_costs(api, full))["views"]["backend"]
    assert selected["selection_mode"] == "quality_only"

    # Same batch metadata cannot transfer costs across the native official pair.
    official_full = load_fixture("worker-cost-covered.json")
    selected = select_sol(enrich_sol_backend_costs(api, official_full))["views"]["backend"]
    assert selected["selection_mode"] == "quality_only"


def test_reference_cost_keeps_quality_score_and_capability_degradation():
    api = adapt_sol_api(load_fixture("reference-api-v1.1.json"))
    full = load_fixture("reference-full-snapshot.json")
    enriched = enrich_sol_backend_costs(api, full)
    selected = select_sol(
        enriched,
        supported_efforts=("low", "medium", "high", "xhigh"),
    )["views"]["backend"]
    assert selected["selection_mode"] == "cost_optimized"
    assert selected["selected_effort"] == "xhigh"
    assert selected["selected_score"] == 92
    assert selected["source_winner_effort"] == "max"
    assert selected["capability_degraded"] is True


def test_missing_latency_skips_latency_for_cheapest_tie_and_preserves_cost_priority():
    api_payload = load_fixture("worker-api-v1.1.json")
    full = load_fixture("worker-cost-covered.json")
    for row in api_payload["rankings"]:
        if row["reasoningEffort"] == "xhigh":
            row["score"] = row["backendScore"] = 93
    for entry in full["entries"]:
        effort = entry["model_configuration"]["reasoning_effort"]
        if effort == "xhigh":
            entry["score"] = 93
            entry["estimated_api_cost_usd"] = 1.0
        elif effort == "high":
            entry["estimated_api_cost_usd"] = 1.0
        elif effort == "max":
            entry["estimated_api_cost_usd"] = 2.0
    enriched = enrich_sol_backend_costs(adapt_sol_api(api_payload), full)
    for item in enriched["views"]["backend"]["items"]:
        if item["effort"] == "xhigh":
            item["elapsed_ms"] = None
    selected = select_sol(enriched)["views"]["backend"]
    assert selected["quality_band_efforts"] == ["high", "xhigh", "max"]
    assert selected["selected_effort"] == "high"
    assert selected["selection_mode"] == "cost_optimized"


def test_cost_and_latency_ties_use_score_then_effort_deterministically():
    api_payload = load_fixture("worker-api-v1.1.json")
    for row in api_payload["rankings"]:
        if row["reasoningEffort"] in ("high", "max"):
            row["elapsedMs"] = 400
    api = adapt_sol_api(api_payload)
    full = load_fixture("worker-cost-covered.json")
    by_effort = {entry["model_configuration"]["reasoning_effort"]: entry for entry in full["entries"]}
    by_effort["high"]["estimated_api_cost_usd"] = 1.0
    by_effort["max"]["estimated_api_cost_usd"] = 1.0
    by_effort["high"]["elapsed_ms"] = by_effort["max"]["elapsed_ms"] = 400
    enriched = enrich_sol_backend_costs(api, full)
    selected = select_sol(enriched)["views"]["backend"]
    assert selected["selected_effort"] == "max"  # Higher score breaks the exact latency tie.

    for row in full["entries"]:
        effort = row["model_configuration"]["reasoning_effort"]
        if effort in ("high", "max"):
            row["score"] = 93
            row["estimated_api_cost_usd"] = 1.0
            row["elapsed_ms"] = 400
        elif effort == "xhigh":
            row["score"] = 90
    api_payload = load_fixture("worker-api-v1.1.json")
    for row in api_payload["rankings"]:
        if row["reasoningEffort"] in ("high", "max"):
            row["score"] = row["backendScore"] = 93
            row["elapsedMs"] = 400
        elif row["reasoningEffort"] == "xhigh":
            row["score"] = row["backendScore"] = 90
    tied = select_sol(enrich_sol_backend_costs(adapt_sol_api(api_payload), full))["views"]["backend"]
    assert tied["selected_effort"] == "high"  # Lower effort wins equal score and latency.


class WorkerSelectorTests(unittest.TestCase):
    def test_cached_cost_metadata_must_still_match_protocol_and_pricing(self):
        for field, value in (
            ("pricing_snapshot_id", "unrelated-pricing"),
            ("protocol_id", "other|protocol|with|five|fields"),
            ("cost_source_array", "overallRankings"),
            ("benchmark_provider", "cloudflare-reference"),
            ("benchmark_route", "custom_endpoint"),
            ("batch_id", "unrelated-batch"),
            ("batch_sha256", "sha256:" + "f" * 64),
            ("entry_count", 4),
            ("score_signature", "stale-score-signature"),
        ):
            with self.subTest(field=field):
                snapshot = adapt_sol_full_snapshot(load_fixture("worker-cost-covered.json"))
                snapshot["views"]["backend"]["cost_coverage"][field] = value
                self.assertEqual(select_sol(snapshot)["views"]["backend"]["selection_mode"], "quality_only")
        snapshot = enrich_sol_backend_costs(
            adapt_sol_api(load_fixture("worker-api-v1.1.json")),
            load_fixture("worker-cost-covered.json"),
        )
        snapshot["views"]["backend"]["items"][0]["score"] += 0.25
        self.assertEqual(select_sol(snapshot)["views"]["backend"]["selection_mode"], "quality_only")

    """Run the regression cases with the repository's stdlib unittest gate."""

    def test_api_fixture_maps_four_independent_views_and_groups(self):
        test_api_fixture_maps_four_independent_views_and_groups()

    def test_reference_api_identity_is_preserved_through_root_items_and_selection(self):
        test_reference_api_identity_is_preserved_through_root_items_and_selection()

    def test_official_pair_is_preferred_only_when_complete_and_pair_is_snapshot_wide(self):
        test_official_pair_is_preferred_only_when_complete_and_pair_is_snapshot_wide()

    def test_rows_from_two_pairs_are_not_merged_to_fill_five_efforts(self):
        test_rows_from_two_pairs_are_not_merged_to_fill_five_efforts()

    def test_unlisted_provider_or_route_is_rejected_for_that_view(self):
        test_unlisted_provider_or_route_is_rejected_for_that_view()

    def test_wrong_route_is_unavailable_without_invalidating_other_views(self):
        test_wrong_route_is_unavailable_without_invalidating_other_views()

    def test_partial_axis_and_nonfinite_or_boolean_scores_fail_only_that_view(self):
        test_partial_axis_and_nonfinite_or_boolean_scores_fail_only_that_view()

    def test_missing_effort_makes_only_its_view_unavailable(self):
        test_missing_effort_makes_only_its_view_unavailable()

    def test_source_winner_and_deterministic_quality_tie_order(self):
        test_source_winner_and_deterministic_quality_tie_order()

    def test_supported_efforts_report_missing_source_winner_as_capability_degraded(self):
        test_supported_efforts_report_missing_source_winner_as_capability_degraded()

    def test_uncovered_api_estimates_never_enable_cost_optimization(self):
        test_uncovered_api_estimates_never_enable_cost_optimization()

    def test_full_snapshot_uses_nested_model_configuration_and_integrity_gates(self):
        test_full_snapshot_uses_nested_model_configuration_and_integrity_gates()

    def test_reference_full_snapshot_accepts_and_preserves_per_row_evidence_ids(self):
        test_reference_full_snapshot_accepts_and_preserves_per_row_evidence_ids()

    def test_full_snapshot_unknown_route_and_invalid_evidence_fail_closed(self):
        test_full_snapshot_unknown_route_and_invalid_evidence_fail_closed()

    def test_complete_matching_costs_optimize_inside_inclusive_two_point_band(self):
        test_complete_matching_costs_optimize_inside_inclusive_two_point_band()

    def test_cost_batch_mismatch_fails_soft_to_quality_only(self):
        test_cost_batch_mismatch_fails_soft_to_quality_only()

    def test_reference_cost_enrichment_requires_exact_pair_batch_hash_count_and_scores(self):
        test_reference_cost_enrichment_requires_exact_pair_batch_hash_count_and_scores()

    def test_reference_cost_keeps_quality_score_and_capability_degradation(self):
        test_reference_cost_keeps_quality_score_and_capability_degradation()

    def test_missing_latency_skips_latency_for_cheapest_tie_and_preserves_cost_priority(self):
        test_missing_latency_skips_latency_for_cheapest_tie_and_preserves_cost_priority()

    def test_cost_and_latency_ties_use_score_then_effort_deterministically(self):
        test_cost_and_latency_ties_use_score_then_effort_deterministically()

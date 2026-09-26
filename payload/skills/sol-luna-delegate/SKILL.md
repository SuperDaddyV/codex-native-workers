---
name: sol-luna-delegate
description: Select and route a daily Codex Native Workers Sol/Luna profile before worthwhile bounded delegation.
---

# Sol/Luna delegation

This product is named Codex Native Workers; the legacy Sol/Luna wording and `sol-luna-delegate` Skill name remain supported. Use this Skill before delegating a worthwhile, independent, bounded task. The Coordinator keeps planning, scope, ambiguity resolution, and acceptance. `Sol` identifies a worker family; the user's session still chooses the Coordinator model. After planning, keep small or Coordinator-owned work with the Coordinator.

## Select once

Run the rendered `<SELECTOR_COMMAND>` exactly once for the whole delegation workflow, before spawning the first worker. It runs `selector.py --ensure-daily --print-selection --workers`. Reuse that result for every child; do not reselect, fetch per child, or make a separate network request. If the command fails, the date is not today's Beijing date, or the routing contract is invalid, retain the work and report the failure. Reference `status: unavailable` alone does not disable an explicit basic route.

For a new recovery workflow explicitly requested by the user after an earlier workflow failed with both families unavailable, first preserve the existing `gpt6-v4/worker-profile.json` and `worker-last-good.json` bytes with their SHA-256 hashes in the task's evidence directory. If the user reports that the blocking condition has changed, append `--refresh-workers` to the single rendered invocation above. This replaces the normal invocation; do not run both. Reuse its one result for all children. Never refresh to chase another effort, retry within a failed workflow, bypass an invalid source, or import repository-local caches into installed authority. All generation, publication and hash checks still apply.

The receipt-safe worker profile has this shape:

```json
{
  "worker_profile_schema_version": 3,
  "reference_policy_version": 2,
  "publication_verification_version": 1,
  "selection_date_bjt": "YYYY-MM-DD",
  "luna": {"status": "ready|unavailable", "selected_role": "luna_<effort>", "...": "..."},
  "sol": {
    "status": "ready|unavailable",
    "allowed_roles": ["sol_<effort>"],
    "views": {
      "general": {"status": "ready|unavailable", "selected_role": "sol_<effort>", "...": "..."},
      "backend": {"status": "ready|unavailable", "selected_role": "sol_<effort>", "...": "..."},
      "frontend": {"status": "ready|unavailable", "selected_role": "sol_<effort>", "...": "..."},
      "reasoning": {"status": "ready|unavailable", "selected_role": "sol_<effort>", "...": "..."}
    }
  }
}
```

Require schema version 3, `publication_verification_version = 1`, and a current `selection_date_bjt`. Also require `routing.policy_version = 1`. Reference results above remain evidence; route using `routing.luna` or `routing.sol.views.<view>`:

- `mode: live`: verified Radar data supplied `selected_role` and `selected_effort`.
- `mode: cached`: a qualified same-generation snapshot supplied them; disclose cached use and the reference date.
- `mode: basic`, `evidence_scope: no_benchmark`: no verified reference exists for this route. There is no selected role or fixed default effort. Choose from that route's `allowed_roles` by the bounded task's difficulty, using the guidance below. State once: "基础模式：未采用雷达优化，按任务选择档位。" (or its English equivalent). Do not claim reference quality, cost optimization or savings.

Every route carries `model`, `allowed_roles` and `host_check_required: true`. Intersect returned roles with intact installed agent definitions and the actual host-advertised exact model/effort. These lists are configuration candidates, not account or runtime proof. If none match, retain the work. Missing/malformed routing or unexpected modes are not permission to infer a basic route. Never alter reference status, import caches, guess an unlisted role or pass a direct model/reasoning override.

For live/cached routes, use the returned `selected_role` as the default native custom agent `agent_type`. A task-specific risk or evidence need may justify another Sol role, but only from the route's `allowed_roles`, with an explicit reason. Basic mode permits task-specific choices for either family from its own returned list. A basic route is not a failed spawn: if an actual invocation fails, retain the work and report it; do not silently try another effort or family.

In basic mode, prefer low/medium for mechanical or straightforward bounded tasks, high for meaningful implementation and diagnosis, and xhigh/max only for a stated difficult constraint or evidence need. Compare the actual task, verification burden and available roles; this is not a fixed Sol or Luna default and higher effort is not automatically better. The Coordinator owns architecture, ambiguous scope and final acceptance.

Require `reference_policy_version = 2`. Public benchmark choices are `reference_only`: retain `benchmark_provider` and `benchmark_route` as reported. A Cloudflare reference route does not change the native execution route or establish local model availability, tool restrictions, quota savings, or equivalent performance. Use the recommendation for bounded work and verify its actual result. Missing comparable cost means quality-only selection. The `reasoning` view uses the publisher's Knowledge & Reasoning score.

## Route and bound the work

Prefer Luna for well-specified routine implementation, extraction, tests, and repetitive edits. Choose Sol for bounded work needing more difficult diagnosis, synthesis, or cross-module reasoning; keep architecture and final acceptance with the Coordinator. Choose the family from task needs before checking availability; availability alone is not a reason to transfer work between families.

The task determines the Sol view: use `general` by default, or `backend`, `frontend`, or `reasoning` when that work clearly fits. Use the requested view's explicit route, including basic mode when returned. Never silently substitute an unavailable/unsupported view; keep the task or explicitly choose the available `general` view. Do not automatically switch worker family or retry with another model/effort. Luna has one daily reference recommendation without Sol views; its basic role is chosen per task.

Send only the information needed for the bounded task: Goal, Scope, Constraints, Acceptance Criteria, and Verification. Prefer 0–3 workers. Expand to 4–6 only when each task is ready and independent, write sets do not overlap, and the current runtime supports that concurrency; the project setting of six is only a configured ceiling. There is no fixed Sol quota. Profiles set `[agents] enabled = false`; each child is assigned a leaf role and must not spawn or delegate. The package does not guarantee host-enforced tool/invocation isolation; strict recursive isolation scenarios remain unsupported until independently verified. The Coordinator reviews every result.

Require exact `model` identities `gpt-6-sol` / `gpt-6-luna` and the returned `cache_identity` GPT-6 model, five-effort, axis and policy-2 contract. Active state is isolated under `gpt6-v4`; GPT-5.6 Daily/LKG cannot authorize delegation. Before spawning, confirm the host-advertised custom role pins that exact model/effort. If Desktop still advertises old roles, retain work and request a host reload; do not override model/effort or use an old worker. Shell CLI support does not prove Desktop role loading. No valid same-generation data/cache means an explicit basic route, subject to the installed and host role intersection. Installation, role integrity and account failures still prevent affected delegation.

The `gpt6-v4` namespace rejects pre-verification GPT-6 Daily/LKG records as well as GPT-5.6 state. Keep old `gpt6-v3` state as historical evidence; never copy it into active state. Missing or mismatched publication evidence disables the affected reference view and its dependent general reference. A qualified intact cached view is preferred before basic routing; general scores are never assembled from mixed batches. Do not substitute an unverified quality-only result. Basic decisions never become LKG benchmark evidence. Same-day workflows reuse one result; the next Daily selection automatically prefers verified live data again, then qualified cache. An explicitly requested recovery workflow may refresh once after changed conditions, never to chase effort.

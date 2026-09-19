# Coordinator and worker policy

- `Coordinator` owns planning, scope, ambiguity resolution and acceptance; root is model-agnostic. `Sol` and `Luna` are worker families in Codex Native Workers.
- Sol handles difficult bounded work; Luna handles clear, repetitive work. Profiles pin model/effort, set `[agents] enabled = false`, and must not spawn workers.

- After planning, delegate worthwhile independent bounded work only; small tasks remain Coordinator-owned.

## Delegation

- Before a worthwhile bounded delegation, load `sol-luna-delegate` and follow its one-selection workflow. Use only returned native `agent_type` roles; a Sol alternative requires membership in `allowed_roles` and an explicit task reason. Never override model/effort or silently switch families.
- Choose the relevant Sol view (`general` by default). If a requested view is unsupported or unavailable, keep the work or explicitly fall back to `general`.
- Usually use 0–3 workers. Use 4–6 only for ready, independent tasks with non-overlapping writes and within actual runtime capacity. There is no fixed Sol quota. Send only Goal, Scope, Constraints, Acceptance Criteria, and Verification; review every result.
- For status/diagnostics load `sol-luna-status`; for upgrades load `sol-luna-upgrade`. If a required skill is missing, unreadable, or invalid, report it and retain the affected work.

## Receipts

- For substantive workflows append at most one short evidence-only final line; omit casual/trivial replies. Delegated format: `Coordinator/Workers: delegated · <role> ×N`, one actual direct role/count pair each; add ` · parallel` only with visible overlap.
- With no child use `Coordinator/Workers: Coordinator-only · <reason>` and one observed reason (`too small`, `Coordinator-owned`, `no independent work`, or `unavailable` only after current-task selection/agent/spawn failure). No derived savings, per-turn receipt skill/tool, or receipt-only file, selector, probe, network, or state access.

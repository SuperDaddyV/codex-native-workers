# Repository development rules

This repository develops Codex Native Workers (Coordinator / Sol / Luna). Runtime delegation
follows the inherited, currently installed Global policy and its Daily selector;
repository-local candidate profiles and `.var/` state are not installed authority.
The Coordinator owns scope, architecture and final acceptance. Worker execution
must remain bounded; do not delegate again from a Worker.

- Read the active baseline in `PLANS.md` before implementation. Preserve existing
  uncommitted work and historical evidence; no previous PASS is current acceptance.
- Keep implementation, tests and documentation inside this repository. Real
  CODEX_HOME or user Skill installation/repair, credentials, Git mutations and
  publication require their own explicit authorization.
- Use native custom agents, not a custom orchestration engine. During development,
  obey the running host's actual capacity; candidate concurrency is not runtime proof.
- Keep the installed Global block within its byte budget. Put conditional workflow
  in the three Skills, deterministic selection in code and development rules here.
- Preserve strict versioned inventories, user-owned content, full prevalidation of
  rollback, and isolated state. Never relax integrity checks to obtain PASS.
- Validate changes with focused regressions and the full standard-library test
  suite. Keep source, fake-home, installed and native evidence separate. State
  missing live data and unrun native checks explicitly; final acceptance belongs
  to the Coordinator.

The v4.2 product contract in PLANS.md separates core product acceptance from host
tool isolation, invocation enforcement and measured capacity. Keep historical
failures; do not claim strong recursive isolation or six-worker support without
native evidence. A host capability failure stops checks that depend on it, not
independent core checks under the approved product contract.

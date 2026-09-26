# Installation and troubleshooting

[简体中文](INSTALLATION.zh-CN.md) · [Home](README.md)

**v4.3.0 is unpublished; current Stable remains v4.2.0.** This page describes the v4.3.0 candidate. Start with the [homepage prompt](README.md#install-or-upgrade), then follow [NATIVE_WORKERS_SETUP.md](NATIVE_WORKERS_SETUP.md) from the verified release commit.

## Identify the environment

| Environment | Checks |
| --- | --- |
| Windows Desktop | Use a local Desktop task with PowerShell, `python` and Git. A separate CLI installation is not required. |
| Windows CLI | Use the PowerShell environment that runs Codex; also check `codex --version`. |
| macOS Desktop | Use a local Desktop task with `python3` and Git. App and terminal PATH values may differ. |
| macOS CLI | Use the terminal that runs Codex; check `python3`, Git and `codex --version`. |
| Linux / WSL / remote host | Install on the task's execution host. WSL and Windows have separate homes, dependencies and login state. |

Python must be 3.11+ with `tomllib`. Check the command installed Skills will actually invoke:

```text
Windows: python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
macOS/Linux: python3 -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
All environments: git --version
CLI only: codex --version
```

Windows `py` can help diagnose Python but does not prove `python` works. macOS needs no extra `python` alias. Desktop and CLI role loading must also be verified separately. [Official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

## Installation steps

1. Verify the Stable Release, immutable tag and exact commit; never install directly from a moving branch.
2. Resolve the actual `CODEX_HOME` and `<SKILLS_ROOT>`; upgrades retain manifest-recorded roots.
3. Gather prerequisite/network issues, resolve actionable failures, then inspect dry-run changes.
4. Apply transactionally, keep the backup and verify hashes. A matching repeat is `IDEMPOTENT_PASS`: zero writes and no new backup.
5. Reload, then verify installation and useful Sol/Luna work separately. Preserve the coordinator, unrelated content and old caches.

Default roots are `.codex` and `.agents/skills` under the user's home, but must not override the actual environment or existing manifest. Quote paths for the shell. The installer records source through `--source-commit`; Source code archives are not one-click installers.

## Let Codex resolve setup problems

Send this in the same task:

```text
Continue from the failed checkpoint. Inspect this client's Python, Git, roots, permissions and network.
Within existing authorization, locate installed tools, correct task-local commands/quoting and reacquire failed temporary downloads. Recheck only the affected steps.
For dependencies, persistent PATH changes, login or a restart, explain the precise action and reason. Execute actions you can perform when already authorized.
Do not repeatedly reinstall, overwrite ownership conflicts, disable TLS or change proxies/certificates to force a pass.
Continue through separate installation and runtime verification. If blocked, report attempts, one minimal user action and a resume prompt.
```

Codex can run `scripts/install_assist.py check/plan/report` with `--client desktop` or `--client cli` and the actual `--codex-home`. `recover` executes only the inspected, authorized repair plan and rechecks afterward. [Detailed commands](NATIVE_WORKERS_SETUP.md#assistance-and-recovery)

| Problem | What Codex should do |
| --- | --- |
| Python / Git missing | Locate existing installations and inspect the app PATH first. Prepare an official install only when needed, obtain missing authorization, then verify it. |
| Desktop cannot find `codex` | Use the Desktop workflow; do not require CLI installation solely for this reason. |
| GitHub connection / download failure | Keep valid source and installation state, retry within a bounded budget, and distinguish network, authentication, certificate and source-identity errors. |
| ModelDial reset / archive 404 / hash mismatch | Separate installation and data selection. Prefer qualified cache, then explicit task-based basic routing after host-role checks; never join unrelated batches. |
| `OWNERSHIP_CONFLICT`, manifest / TOML / hash error | Inspect the conflict and propose a reviewable repair preserving user content. Never delete a manifest or forge hashes. |
| `AGENTS.override.md` / agent-name conflict | Identify the blocker and reconcile existing instructions; do not delete automatically. |
| Skill-root mismatch | Check the manifest against the actual client; do not redirect into another home. |
| Unloaded roles / old models | Verify installation identity, fully quit and restart the relevant client, then start a new task if needed. |
| Only Luna / no workers | Check whether delegation is worthwhile; do not force workers into small tasks. |

After a temporary PATH fix, also verify dependencies in the normally launched client. Otherwise report the remaining restart or persistent repair rather than success.

## What success means

- **Installed:** 10/10 agents, 3/3 Skills, passing ownership/configuration checks, and a recorded backup.
- **Runtime verified:** the actual host loads GPT-6 roles, both families perform useful work, and the coordinator reviews results. Report live, cached or basic routing; basic acceptance does not verify live Radar.
- **Unverified:** retain `Not checked` / `NOT RUN`. `Today Selection not initialized` is normal before the first selection.

Three-platform automated tests are not native installation proof on all platforms or a measured user success rate. [Validation records](RUNTIME_TESTS.md) state coverage separately. Strong recursive isolation, six-worker capacity and quota savings are not guaranteed.

Basic routing reports `Degraded` with `BASIC_ROUTING_ACTIVE` reasons and chooses effort per task. Check the specific reasons: configuration errors and unavailable native roles still require repair; basic mode does not hide them.

## Rollback, uninstall and support

Ask Codex to roll back using the exact transaction backup, or uninstall under the same version's contract with both original roots explicit. Recovery does not accept `--source-commit`; successful rollback consumes its backup. Do not manually delete agents, Skills or the manifest.

In a [Bug Report](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=bug-report.yml), include OS, client, version, brief error, attempts and the failed checkpoint. Do not upload credentials, private paths or the entire `CODEX_HOME`. [Previous versions](VERSIONS.md)

# Codex Native Workers

Let Codex share the work: you choose the coordinator, GPT-6 Sol handles demanding subtasks, and GPT-6 Luna handles clear, repeatable work.

[简体中文](README.zh-CN.md) · [Install & troubleshoot](INSTALLATION.md) · [Changes](CHANGELOG.md) · [Get help](https://github.com/SuperDaddyV/codex-native-workers/issues/new/choose)

[![Validation](https://github.com/SuperDaddyV/codex-native-workers/actions/workflows/validate.yml/badge.svg?branch=master)](https://github.com/SuperDaddyV/codex-native-workers/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/SuperDaddyV/codex-native-workers)](LICENSE)

> **v4.3.0 · GPT-6** — [Release](https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.3.0) · [Previous versions](VERSIONS.md)

## What it does

| Role | Responsibility |
| --- | --- |
| Coordinator | Understands the request, plans, integrates results and accepts the final work. You choose the model; Astra is one option. |
| GPT-6 Sol | Difficult but bounded diagnosis, implementation and cross-module work. |
| GPT-6 Luna | Clear edits, extraction, focused checks and repetitive work. |

Small tasks stay with the coordinator. Larger tasks usually use 0–3 workers; only independent work runs in parallel. There is no fixed Sol quota.

Verified public ModelDial data guides daily reasoning-effort choices. If unavailable, the project uses qualified cached data; without that, basic mode lets the coordinator choose an available role for each task and clearly reports that Radar optimization was not used. The coordinator reviews the results. Benchmark scores and reference costs do not establish local performance or guarantee quota savings.

Installation adds 10 worker profiles, 3 Skills and at most 2 KiB of global rules. It preserves your coordinator settings, unrelated configuration and old caches, with transaction backups, rollback and uninstall support.

## Install or upgrade

For **Codex Desktop and Codex CLI on Windows and macOS**; Linux also has automated tests. Use a Codex task that can run local commands, Python 3.11+, Git and an account with access to the required models. Desktop installation does not require a separate CLI installation. Windows uses `python`; macOS/Linux use `python3`. Treat WSL, remote hosts and the local machine as separate environments.

Open a local task in the Codex environment you intend to use, then paste:

```text
Install or upgrade Codex Native Workers v4.3.0 for this Codex environment.
Verify https://api.github.com/repos/SuperDaddyV/codex-native-workers/releases/tags/v4.3.0
is a published Stable release, resolve its immutable tag to an exact commit, and follow NATIVE_WORKERS_SETUP.md from that commit.
Identify Windows/macOS/Linux, Desktop or CLI, the actual CODEX_HOME and user Skill root.
Diagnose dependencies, connectivity, permissions and the existing installation. Fix issues within the installation authorization, recheck and continue; do not merely list problems.
For new system dependencies, persistent environment changes or a required login, explain the exact action and why it is needed. Do not request authorization already given.
Preserve my coordinator, unrelated files and old state. Run dry-run, then the transactional installer; never bypass source or ownership checks.
Use the installed Skills to verify installation and actual worker use separately. If blocked, report attempts, the smallest next action and a resume prompt.
```

The same prompt handles new installs and upgrades. Let the same task investigate failures instead of overwriting configuration by hand. [Detailed setup and recovery](INSTALLATION.md) · [Installation contract](NATIVE_WORKERS_SETUP.md)

## Daily use

Ask Codex for work as usual. It decides whether delegation is worthwhile. Seeing only Luna—or no worker—can be normal.

- **Status:** ask “Check Sol/Luna status.” to use `sol-luna-status`.
- **Upgrade:** ask “Upgrade Codex Native Workers” to use `sol-luna-upgrade`.
- **Delegation:** `sol-luna-delegate` selects and routes bounded work; you do not need to memorize role names.

Substantive tasks end with a short account of actual work, for example:

```text
Coordinator/Workers: delegated · sol_high ×1 · luna_high ×1 · parallel
```

Efforts may change daily. `parallel` means execution actually overlapped in that task.

## Check that it works

Check installation and execution separately:

1. **Installation:** 10/10 agents, 3/3 Skills, and passing file/configuration checks.
2. **Execution:** Sol and Luna each complete useful work in a real task, and the coordinator reviews it.

`Today Selection not initialized` is normal before the first selection. `Not checked` means the corresponding check did not run. Healthy configuration is not runtime acceptance. A Radar outage can use basic mode; unavailable or mismatched native roles stay with the coordinator. Fully quit and restart the relevant client if roles have not loaded.

## Common questions

- **Will it save quota?** There is no guarantee. It provides task routing and dynamic effort selection; assess results on your own work.
- **How many workers can run together?** Usually 0–3. Using 4–6 depends on independent tasks and the host; six-worker capacity is unverified.
- **Can workers create more workers?** The project forbids it, but does not guarantee host-enforced recursive isolation.
- **What if installation fails?** Have Codex follow the [recovery steps](INSTALLATION.md#let-codex-resolve-setup-problems). Network, account or system permissions may need one specific user action.
- **Can I undo installation?** Ask Codex to roll back using the transaction backup, or uninstall safely. Do not delete managed files manually.

## More information

[Previous versions](VERSIONS.md) · [Architecture](ARCHITECTURE.md) · [Validation](RUNTIME_TESTS.md) · [Security](SECURITY.md) · [GitHub Releases](https://github.com/SuperDaddyV/codex-native-workers/releases)

Include OS, client, version and the brief error when requesting help. Never upload credentials, private paths or the entire `CODEX_HOME`. [Bug Report](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=bug-report.yml) · [Compatibility Report](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=compatibility-report.yml) · [Feature request](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=feature-feedback.yml)

Independent community project, not affiliated with or endorsed by OpenAI or ModelDial. [MIT License](LICENSE); ModelDial data is used under [CC BY 4.0](https://modeldial.com/data-license). See [fixture attribution](fixtures/modeldial/README.md).

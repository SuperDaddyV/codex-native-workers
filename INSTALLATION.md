# Installation help — Codex Native Workers

[简体中文](INSTALLATION.zh-CN.md) · [Choose a version](README.md#choose-your-version)

Use the complete installation prompt in the README. This guide explains checks
and recovery; it is not a replacement installer or permission to run from `master`.
The [v4.3.0 Stable contract](NATIVE_WORKERS_SETUP.md) governs current installation.
Execute the copy in the verified Release commit. Previous versions retain their
own immutable contracts; do not use a v4.1.4 contract with v4.3.0 source.

## 1. Choose the current Stable target

| Starting point | Action |
| --- | --- |
| New user | Use the **v4.3.0 Stable** prompt in the README. It adds Sol and Luna worker families and keeps your Coordinator choice. |
| Existing v4.1.4 or v4.2.0-rc1 user | Run that same prompt to upgrade the existing installation with preserved user content. |
| Already on v4.3.0 | A matching installation needs no rewrite or new backup. Check status if needed. |
| Deliberately need an old version | Use its immutable contract under README's Previous versions section; do not downgrade automatically. |

GitHub's **Latest** release points to Stable v4.3.0. A Source code ZIP is not a
one-click installer. Do not install old versions first or copy managed files by
hand. The repository is now `codex-native-workers`; compatible installed paths,
managed markers and Skill names retain their legacy names.

## 2. Check the same environment Codex will use

Run these read-only checks **inside the local Codex task's shell**. Success in a
different terminal, Windows account, or WSL environment does not establish readiness.

```text
codex --version
git --version
python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
```

- `codex` and Git must be executable. Desktop installation alone does not prove the CLI is on the task's PATH. Follow the [official Codex CLI setup](https://learn.chatgpt.com/docs/codex/cli) if it is missing; package installation or persistent environment repair needs authorization.
- **The command must be `python`.** The released policy/Skill selector commands use that literal name. `py`, `python3`, a terminal-only alias, or an installer launched with a different interpreter is insufficient. Confirm Python 3.11+ and `tomllib` before apply. Do not edit installed managed commands to conceal this mismatch.
- The local client must support [native custom agents and subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Sign in through Codex's normal UI/CLI. This package does not grant model access or include credits. v4.3.0 needs `gpt-6-sol` and `gpt-6-luna` with `low`, `medium`, `high`, `xhigh`, and `max` efforts. CLI/model prechecks do not prove native worker execution.
- The task needs HTTPS access to GitHub for release/source verification and to ModelDial's public data for the first Daily selection. Benchmark availability and account model access are separate checks. Do not change proxy, certificate trust, credentials, or organization policy to force a pass.
- Resolve the actual client's absolute `CODEX_HOME` and user Skill root before writing. Normally these are `<HOME>/.codex` and `<HOME>/.agents/skills`; a custom `CODEX_HOME` must be handled explicitly. For an upgrade, reuse the existing manifest's Skill root. Do not let a temporary checkout or a different user's home become the install target. WSL is a separate Linux environment.

There is no claimed universal minimum Desktop version or all-platform native
guarantee. If a role cannot be loaded, report the actual client version and error.

## 3. Install once, then verify in stages

Paste the chosen README prompt into a local Codex task with shell access and
authorization to update the package's user-level files. It should resolve the
published release, acquire the pinned clean detached source, inspect the dry-run,
apply transactionally and retain the exact backup location. A web-only chat cannot
perform these local changes. System dependency repairs are a separate action.

Contract commands containing `<CODEX_HOME>`, `<SKILLS_ROOT>` or similar names are
templates. Codex must substitute the verified absolute paths and quote them for
the actual shell, especially paths with spaces; do not paste placeholders literally.

v4.3.0 manages the Global AGENTS block, owned Codex agent configuration, ten
role files, two selector files, three Skills and its manifest. It preserves
unrelated user content and does not need to edit your project's application code.
Use explicit roots for dry-run, apply and recovery; keep backup paths private.

| Checkpoint | Evidence and what it means |
| --- | --- |
| Source | Published `v4.3.0` Stable Release, its resolved exact 40-hex tag commit, clean detached checkout, remote tag checked again. A newer documentation commit is not this runtime source. |
| Dry-run / apply | Expected paths only; complete transaction and backup verification. Conflicts stop installation before an overwrite. |
| Installed identity | Correct version/source, 12 payloads, 3 Skills and managed-block integrity; a second matching apply is `IDEMPOTENT_PASS`, with no writes or new backup. |
| Read-only status | Ask `Check Sol/Luna status.` v4.3.0 normally reports `Status Healthy`, `Agents 10/10 Ready`, `Skills 3/3 Ready` and `leaf_config Ready`. These are configuration results. Legacy v4.1.4 has five Luna agents and a different status shape. |
| First useful delegation | Reload/start a fresh task if the host has not loaded the roles. Follow installed `sol-luna-delegate` once, reuse its selection, and verify useful direct Sol/Luna results with Coordinator review. |

`Today Selection not initialized` can be normal immediately after installation.
The status Skill is read-only; it does not fetch data or initialize selection.
The first worthwhile delegation initializes Daily state. Missing/invalid selection
or unavailable roles mean the Coordinator retains that work and reports the cause.
Do not repeatedly call the selector or invent a role to make a smoke test pass.

Diagnostic schema 4 deliberately reports native delegation, tool isolation,
invocation guard and maximum parallelism as `Not checked`: that status reader does
not run native tests. Runtime evidence belongs in the task's separate results.
One successful worker, a receipt, or the legacy one-Luna smoke is not acceptance
of both v4.3.0 worker families.

## 4. Common failures and the next action

| Symptom | Next action |
| --- | --- |
| `codex` not found / unusable | Check executable discovery in the same task environment. Use official setup or an explicitly authorized PATH repair, then rerun the failed precheck. |
| `python` not found, wrong version, or missing `tomllib` | Make the actual `python` command usable in that environment with authorization. A passing `python3`/`py` test alone does not resolve it. |
| Role/model/effort unsupported | Check account access and the exact client error; reload after install if needed. Keep the work with the Coordinator. Do not silently replace Sol with Luna or override the chosen profile. |
| GitHub or ModelDial unavailable | Preserve the concise error and retry when access is restored. On first use there may be no valid selection to reuse. Do not disable HTTPS validation or fabricate data. |
| `OWNERSHIP_CONFLICT`, hash mismatch, or invalid TOML | Stop and inspect the named file locally. Do not delete the manifest, edit hashes, or overwrite user content. A same-version reinstall does not repair a conflict. |
| Non-empty `AGENTS.override.md` or conflicting user-owned agent settings/files | The installer stops intentionally. Agree on how to preserve or reconcile the user's configuration before resuming; never remove it automatically. |
| Skill-root mismatch | Use the existing manifest's absolute Skill root. Stop if it cannot be matched to the actual client; do not redirect an upgrade into another home. |
| Installation looks healthy but roles/Skills are missing from the task | Confirm the task uses the inspected roots; reload the client and create a fresh task. A source checkout or `.var` copy is not the installed authority. |
| Only Luna appears | Check the version first: Legacy v4.1.4 installs no Sol workers. On v4.3.0, task routing may legitimately choose only Luna; status/model availability alone does not require using Sol. |
| No worker appears | Small tasks or work without independent bounded scopes stay with the Coordinator. Explicitly request useful, separate Sol diagnosis and Luna checks when verifying both families. |
| Worker sees delegation tools | Strong recursive isolation is unsupported in v4.3.0. Tool visibility is not a successful nested call. Do not claim or depend on host isolation. |

For help, report the channel/version, OS, Codex/Python versions, failed checkpoint,
concise error and steps to reproduce. Use [Bug Report](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=bug-report.yml)
or [Compatibility Report](https://github.com/SuperDaddyV/codex-native-workers/issues/new?template=compatibility-report.yml).
Redact secrets, account details and private paths; never upload the entire `CODEX_HOME`.

```text
Continue the same installation target. Read the last failed checkpoint and
report its exact error, likely cause, and smallest next action. Preserve the
verified source, existing installation roots and unrelated user content.
Recheck only affected prerequisites after a fix. Stop on ownership conflicts;
do not restart, downgrade, overwrite or change system settings to force success.
```

## 5. Recovery and evidence limits

Rollback and uninstall run only when requested. Use the installer from the verified
version, the exact returned transaction backup for rollback, and the same explicit
roots. v4.3.0 recovery requires both roots and does not accept `--source-commit`;
Legacy v4.1.4 uses its own one-root setup commands. A successful rollback consumes that
backup. Both flows validate ownership and preserve unrelated content. Follow the
immutable version's contract; do not substitute a source archive, delete role files
by hand, or remove the manifest to reset ownership. Reload after recovery.

The [v4.3.0 validation record](https://github.com/SuperDaddyV/codex-native-workers/releases/download/v4.3.0/native-workers-v4.2.0-validation.json)
binds Stable checks to the exact published source. The historical [rc1 validation record](https://github.com/SuperDaddyV/codex-native-workers/releases/download/v4.2.0-rc1/native-workers-rc1-validation.json)
records source CI on Windows, Ubuntu and macOS and one Windows installed/native
scenario. The rc1 release suite discovered 430 tests per platform: Windows passed all
430; Ubuntu/macOS skipped 13 Windows junction tests and passed the remainder.
This is not native installation proof on all platforms or a measured user
installation success rate. Strong recursive isolation, six-worker capacity and
local billing/quota savings remain unsupported or unverified. See
[runtime evidence](RUNTIME_TESTS.md) for the separate checks.

## GPT-6 migration and diagnostics

Active roles pin `gpt-6-sol` / `gpt-6-luna`; all five efforts, four Sol views and one Luna Daily remain dynamic. The Coordinator remains user-selected. `src/worker_selector.py` centralizes the model contract; the installer writes manifest schema 4 with the same strict inventory and two-root rollback checks.

State is isolated in `gpt6-v3` under the existing state directory, bound to exact models, score axes, efforts and selection policy 2. Old GPT-5.6 Daily/LKG files remain untouched and cannot become GPT-6 fallbacks. Missing valid GPT-6 data and same-generation cache means Coordinator ownership. Missing complete comparable cost evidence means explicit `quality_only`, never a claim of local billing or quota savings.

Disk configuration does not prove Desktop role loading. If a task still advertises GPT-5.6 custom roles, fully quit and restart Codex Desktop, then resume that task's native acceptance. Do not override model parameters or call old workers. Report shell CLI and Desktop capabilities separately. Preserve the transaction backup path from the installer receipt; old state is retained and rollback still prevalidates both roots and all ownership hashes.

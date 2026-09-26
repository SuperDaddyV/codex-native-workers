# Codex Native Workers — v4.3.1 Stable installation contract

This contract applies only to the published, non-draft, non-prerelease `v4.3.1`
Release in `SuperDaddyV/codex-native-workers`. This document or a tag alone is not
publication evidence. The renamed repository retains the project's history;
installed paths, managed markers and `sol-luna-*` Skill names remain compatible.
Earlier version contracts and immutable releases keep their original scope.

## Supported product and limitations

The product configures native Sol/Luna worker profiles, validated Daily selection,
bounded task routing and transactional installation. The user chooses the
Coordinator. Stable does not mean that the package enforces a security boundary
inside Codex. Strong recursive isolation is unsupported: the historical Sol
tool-visibility check failed, and nested invocation enforcement was not verified.
Maximum six-worker capacity and measured local billing/quota savings are also
unverified. Preserve these limits when reporting installation success.

## 1. Check prerequisites before managed writes

Confirm the user requested installation or upgrade to this target. An inspection
request alone does not authorize apply. Diagnose independent prerequisites in one
pass in the actual local Codex task environment:

Use `python` on Windows/PowerShell and `python3` on macOS/Linux, matching
rendered Skills. Commands below use the Windows launcher; substitute `python3`
for every installer and assistance invocation on macOS/Linux.

```text
python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
git --version
```

For CLI also check `codex --version`; an alias alone is insufficient. For Desktop
use its local shell-enabled task with `--client desktop`. A separate CLI is not
required. Desktop model/effort availability is checked in that host after
configuration; CLI assistance retains its direct capability precheck. Neither
is native delegation proof until useful workers actually run.

Confirm access to `gpt-6-sol` and `gpt-6-luna` at the configured efforts. Never copy
authentication or private configuration into a test home. GitHub HTTPS is needed
for source identity; Radar selection also needs public reference data. Missing
reference data permits explicit basic routing after installed/host role checks.
Resolve commands in the actual app/terminal environment; GUI PATH, Windows app
execution aliases, WSL and remote hosts may differ.

Missing prerequisites stop dependent managed writes, not independent diagnosis
or authorized recovery. Follow the recovery section below before handing off. Give
the precise blocker and smallest next action if recovery cannot complete. Do not install global dependencies, edit PATH persistently, change
credentials, proxy/certificate trust, sandbox or organization policy without
authorization for that additional scope. Existing explicit authorization remains
valid; no repeated confirmation is required for already authorized operations.

## 2. Resolve the published immutable source

1. Read `/repos/SuperDaddyV/codex-native-workers/releases/tags/v4.3.1`. Require
   `draft=false`, `prerelease=false`, and non-null `published_at`. Do not substitute
   an unpublished candidate, the newest prerelease, or `target_commitish`.
2. Resolve the remote `v4.3.1` tag and peel an annotated/lightweight tag to one exact
   40-hex commit. Acquire a clean detached checkout at that commit, then read the
   remote tag again. A change is `TAG_MOVED`: stop without installation writes.
3. Read this contract from that exact commit. Require detached `HEAD`, the verified
   tag commit and the installer's `--source-commit` to match; require installer
   `VERSION == "v4.3.1"`. Do not install from `master`, another moving branch or an
   unverified tag. A later README/documentation commit is not the runtime source.
4. The source and contract share the verified release commit, so no file is
   required to embed its own SHA. Do not use the old v4.1.4 setup/assisted contract
   to apply v4.3.1 or substitute current source into an older pinned contract.

## 3. Apply one two-root transaction

Resolve both absolute roots: the actual client's `CODEX_HOME` and user Skill root
(normally `<HOME>/.agents/skills`). For upgrades use the manifest-recorded Skill
root. Stop on a mismatch or uncertain client/home mapping; treat WSL separately.
Preserve the user-selected Coordinator model/effort and all unrelated content.
Never downgrade automatically. An already matching target performs zero writes
and creates zero backups.

From the verified detached checkout, replace and shell-quote the placeholders:

```text
python scripts/install.py --dry-run --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT> --source-commit <VERIFIED_40_HEX_COMMIT>
python scripts/install.py --apply --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT> --source-commit <VERIFIED_40_HEX_COMMIT>
```

Inspect a successful dry-run's exact created/modified/removed paths before apply.
Invalid inventories, ownership/hash conflicts, source mismatch, changed roots or
unexpected operations stop the workflow. Do not hand-copy managed files, delete a
manifest, edit hashes or remove user-owned configuration to force a pass. Use the
transaction-aware installer; do not reproduce its merge or rollback logic.

The installer creates and verifies a backup before changes. Keep its exact
returned path private. Verify version/source, all twelve owned payloads, all three
Skills, the Global managed block's 2,048-byte limit and preservation of unrelated
content. A second matching apply must be `IDEMPOTENT_PASS` with zero writes and no
new backup. This verifies installation integrity, not native execution.

## 4. Verify status and actual use separately

Follow the installed `sol-luna-status` Skill once. It is read-only: do not combine
status with Daily initialization or a native probe. Healthy, 10/10 agents,
3/3 Skills and `leaf_config Ready` are configuration results. Native capability
fields remain `Not checked` because the status reader does not run native tests.
`Today Selection not initialized` is normal on a fresh installation; upgrades may
retain valid existing Daily state.

Reload and start a fresh task if the host has not loaded the installed roles.
For useful independent bounded work, follow `sol-luna-delegate` once and reuse
that selection. Verify direct Sol and Luna results, actual model/effort, parentage,
non-overlapping mixed work and Coordinator review. New native children in an
existing task are acceptable if the host demonstrably loads the installed roles.
The old one-Luna compatibility smoke is not two-family acceptance.

Report configuration, native work, tool visibility, invocation enforcement and
observed concurrency separately. Unexpected worker delegation, wrong model/effort
or unsafe writes stop the affected check. A known tool-visibility failure remains
FAIL; it does not become PASS because this version is Stable. Checks depending
on unverified isolation cannot pass. Installation can be complete while a native
check is NOT RUN or BLOCKED; never describe that as full runtime acceptance.

## 5. Recovery

Only run rollback or uninstall when requested. Use this verified version's
installer and the same explicit roots. Rollback uses the exact returned backup:

```text
python scripts/install.py --rollback <EXACT_BACKUP_PATH> --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT>
python scripts/install.py --uninstall --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT>
```

Do not pass `--source-commit` to recovery. Both operations validate ownership and
preserve unrelated content. Successful rollback consumes its backup; uninstall
removes only verified owned content and is not equivalent to rollback. An invalid
backup or ownership mismatch stops the operation. Never delete user files or
rewrite immutable tags to recover. Reload after recovery.

## GPT-6 migration and diagnostics

Active roles pin `gpt-6-sol` / `gpt-6-luna`; all five efforts, four Sol views and one Luna Daily remain dynamic. The Coordinator remains user-selected. `src/worker_selector.py` centralizes the model contract; the installer writes manifest schema 4 with the same strict inventory and two-root rollback checks.

State is isolated in `gpt6-v4` under the existing state directory, bound to exact models, score axes, efforts and selection policy 2. Old GPT-5.6 Daily/LKG files remain untouched and cannot become GPT-6 fallbacks. Missing valid GPT-6 data and same-generation cache means explicit task-based basic routing under routing policy 1, subject to intact installed and host-advertised exact roles. Role or account failures still require Coordinator ownership. Missing complete comparable cost evidence means explicit `quality_only`, never a claim of local billing or quota savings.

Disk configuration does not prove Desktop role loading. If a task still advertises GPT-5.6 custom roles, fully quit and restart Codex Desktop, then resume that task's native acceptance. Do not override model parameters or call old workers. Report shell CLI and Desktop capabilities separately. Preserve the transaction backup path from the installer receipt; old state is retained and rollback still prevalidates both roots and all ownership hashes.

Publication verification checks backend identities, scores, scales and latency against the exact hashed archive. Sol frontend, reasoning and general views additionally require their matching benchmark-index records and hashed archives; a missing or mismatched view cannot become a quality-only choice. The new `gpt6-v4` cache requires publication verification version 1. Earlier `gpt6-v3` caches remain untouched and cannot authorize fallback.

## Three-tier task routing

The installed delegation Skill reads one versioned `routing` contract per workflow.
Verified live data wins, then qualified same-generation cache, then basic mode for
the affected family/view. Each cached view keeps its complete original snapshot;
never recompute general scores from different batches. Existing reference statuses
remain unchanged, including rejected publication evidence.

Basic mode has `evidence_scope: no_benchmark`, allowed roles and no selected effort.
The Coordinator intersects them with intact installed definitions and actual
host-advertised GPT-6 model/effort, chooses by task difficulty and reports that
Radar optimization was not used. No role match means retained work. It does not
change families, bypass model checks, claim cost savings or populate benchmark LKG.
Useful native work may pass under disclosed basic mode while live Radar acceptance
is blocked. A later Daily selection prefers verified live data again; same-day
recovery follows the installed Skill's single-refresh rule.

## Assistance and recovery

Continue until installation is verified or a specific external condition prevents
progress. Do not merely print an error or repeat the same failed install. Preserve
a failed checkpoint for resumption.

1. Identify OS, CLI/Desktop, actual host, both roots and existing manifest. Check
   independent prerequisites together. WSL and remote hosts are separate installs.
2. Locate existing Python/Git before proposing packages. Correct shell quoting
   and task-local command resolution; retry transient downloads at most three
   times. Never replace a missing exact archive with another batch.
3. Prepare concrete official repair commands and verification. New dependencies,
   persistent PATH/proxy/certificate or privilege changes require authorization
   for that scope; reuse existing authorization. Do not copy secrets, disable TLS,
   change sandbox rules, delete conflicts or weaken ownership checks.
4. Recheck affected prerequisites. A temporary PATH workaround must also work in
   the normally launched client before claiming readiness.
5. Run dry-run/apply after source/root/ownership gates pass. Reload as needed,
   then use installed Skills for status and useful worker verification. Report
   configuration, native execution and unrun checks separately.
6. If login, restart, permission or an upstream outage remains, report attempts,
   exact failure, one smallest user action and a resume prompt. Continue from
   that checkpoint, preserving valid files and evidence.

From the verified checkout (use `python3` on macOS/Linux):

```text
python scripts/install_assist.py check --client <cli-or-desktop> --codex-home <CODEX_HOME>
python scripts/install_assist.py plan --client <cli-or-desktop> --codex-home <CODEX_HOME>
python scripts/install_assist.py recover --client <cli-or-desktop> --codex-home <CODEX_HOME> --approve <EXACT_APPROVED_PLAN_ID>
python scripts/install_assist.py report --client <cli-or-desktop> --codex-home <CODEX_HOME> --format markdown
```

A plan identifier detects drift; it is not user authorization. Run `recover` only
when its concrete actions are authorized. If missing tools prevent the helper
from starting, the supervising Codex must diagnose them using its available local
shell and official instructions, then resume the helper. Desktop assistance leaves
capability `NOT_CHECKED` and requires host-native acceptance after installation;
selecting that mode never creates a runtime PASS.

# Codex Native Workers — v4.2.0 Stable installation contract

This contract applies only to the published, non-draft, non-prerelease `v4.2.0`
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

```text
codex --version
git --version
python -c "import sys, tomllib; assert sys.version_info >= (3, 11); print(sys.version)"
```

`codex` must be a normally resolvable executable, not only a shell alias or the
Desktop application. Installed selector commands require the actual `python`
command; having only `python3` or `py` is insufficient. Confirm the client supports
native custom agents/subagents and the account can use `gpt-5.6-sol` and
`gpt-5.6-luna` at the five configured efforts (`low` through `max`). The capability
probe in this exact source can verify direct CLI requests; those requests are not
proof of native delegation. Never copy authentication or private configuration
into a test home. GitHub HTTPS is required for source identity; first Daily
selection additionally needs the public reference data source.

Missing prerequisites stop managed writes. Give the precise blocker and smallest
next action. Do not install global dependencies, edit PATH persistently, change
credentials, proxy/certificate trust, sandbox or organization policy without
authorization for that additional scope. Existing explicit authorization remains
valid; no repeated confirmation is required for already authorized operations.

## 2. Resolve the published immutable source

1. Read `/repos/SuperDaddyV/codex-native-workers/releases/tags/v4.2.0`. Require
   `draft=false`, `prerelease=false`, and non-null `published_at`. Do not substitute
   an unpublished candidate, the newest prerelease, or `target_commitish`.
2. Resolve the remote `v4.2.0` tag and peel an annotated/lightweight tag to one exact
   40-hex commit. Acquire a clean detached checkout at that commit, then read the
   remote tag again. A change is `TAG_MOVED`: stop without installation writes.
3. Read this contract from that exact commit. Require detached `HEAD`, the verified
   tag commit and the installer's `--source-commit` to match; require installer
   `VERSION == "v4.2.0"`. Do not install from `master`, another moving branch or an
   unverified tag. A later README/documentation commit is not the runtime source.
4. The source and contract share the verified release commit, so no file is
   required to embed its own SHA. Do not use the old v4.1.4 setup/assisted contract
   to apply v4.2.0 or substitute current source into an older pinned contract.

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

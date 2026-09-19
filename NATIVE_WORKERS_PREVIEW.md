# Codex Native Workers — v4.2.0-rc1 preview installation

This contract applies only to `v4.2.0-rc1` from the published, non-draft GitHub
Prerelease in `SuperDaddyV/codex-sol-luna-worker`. A branch checkout, this document
alone, or a tag without a published Release is not installation authority.
`v4.1.4` remains the default Stable target through its existing pinned contracts.

The preview provides native Sol/Luna profiles, validated task selection and
transactional installation. Strong prevention of recursive worker delegation is
unsupported. A Sol child reported collaboration tools on Desktop host
`0.155.0-alpha.9.2`; no nested invocation was tested. Maximum six-worker capacity
and local billing/quota savings are unverified. Preserve these limitations in the
installation result. See [runtime evidence](RUNTIME_TESTS.md).

## Resolve and inspect

1. Confirm the user requested this preview or the latest project release including
   prereleases. An inspection request alone does not authorize installation.
2. Read the published Release for exact tag `v4.2.0-rc1`; require `draft=false`,
   `prerelease=true`, and a non-null publication timestamp. If unavailable, stop.
3. Read the remote tag ref, peel an annotated/lightweight tag to one exact 40-hex
   commit, and acquire a clean detached checkout at that commit. Read the remote
   tag again after acquisition. Any change is `TAG_MOVED`: stop without writes.
4. Read this contract from that exact commit. Require detached `HEAD`, the verified
   tag commit and the commit passed as `--source-commit` to match; require installer
   `VERSION == "v4.2.0-rc1"`. Do not install from `master`, `target_commitish`, a
   moving branch, or an unverified tag. Do not use the old Stable setup contract to
   apply this preview. The Release's commit is the preview source/contract anchor;
   no source file needs to contain its own SHA.
5. Confirm Python 3.11+, Git, native custom-agent support, access to the selected
   Sol/Luna models, and a usable Codex executable. CLI/model metadata is not proof
   of native execution. Diagnose missing prerequisites without changing credentials,
   proxy, certificate trust, permissions or unrelated environment settings.

## Apply through the installer

Resolve both absolute roots: the user's existing `CODEX_HOME` and user Skill root
(normally `<HOME>/.agents/skills`). If an existing manifest names a different Skill
root, stop instead of silently redirecting it. Preserve user-selected Coordinator
model/effort and everything outside owned files/managed blocks. Never downgrade
automatically; an already current target performs zero writes and zero backups.

Before apply, display:

```text
目标：v4.2.0-rc1
渠道：Prerelease / Public Beta
此版本可能包含尚未完成的变化，外部真实运行验证少于稳定版。
修改托管文件前会创建事务备份；不会有意覆盖与本项目无关的用户配置。
宿主强制禁止递归委派、六代理容量及额度节省尚未验证。
```

From the verified detached checkout, substitute the verified values below; these
are argument templates, not literal paths or unverified commit values:

```text
python scripts/install.py --dry-run --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT> --source-commit <VERIFIED_40_HEX_COMMIT>
python scripts/install.py --apply --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT> --source-commit <VERIFIED_40_HEX_COMMIT>
```

Require a successful dry-run and inspect its exact created/modified/removed paths
before applying. Ownership/hash conflicts, invalid inventories, source mismatch,
changed roots or an unexpected operation stop the workflow. Do not overwrite a
conflict, hand-edit a manifest, weaken validation, copy credentials or install
global dependencies to force a pass. Existing user authorization for these exact
operations remains valid; request separate authorization only for added scope.

Apply creates and verifies a transaction backup before changes. Retain its exact
returned location privately. Verify installed version/source commit, all twelve
owned payload files, all three rendered Skills, the managed Global byte budget,
unchanged user content and a second idempotent apply with no writes or new backup.
The status reader is read-only: follow the installed `sol-luna-status` Skill once,
without combining it with profile initialization or a native probe.

## Verify actual use

Reload the client and use newly created native workers to validate the installed
roles. In a workflow that needs delegation, follow `sol-luna-delegate` and reuse
its one current selection. Verify actual model/effort and useful output for each
family, direct parentage, independent mixed work and Coordinator review. Native
children may be freshly created inside an existing task if the host discovers
the installed roles; a reload/new task is required when it does not.

Treat configuration, useful delegation, tool visibility, invocation enforcement
and observed concurrency as separate results. The preview core gate does not
require unverified host guarantees. Never relabel the historical leaf FAIL or
claim that an exposed tool was successfully invoked. Unexpected worker spawning,
wrong model/effort or unsafe writes stop the affected check. The legacy one-Luna
compatibility smoke is not sufficient acceptance of this two-family preview.

## Recovery

Rollback uses the exact verified backup returned by this installation:

```text
python scripts/install.py --rollback <EXACT_BACKUP_PATH> --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT>
```

Uninstall removes only verified owned content:

```text
python scripts/install.py --uninstall --codex-home <CODEX_HOME> --skills-root <SKILLS_ROOT>
```

Run these only when requested. Both operations preserve unrelated content and
fail closed on mismatched ownership or invalid backup data. Do not delete user
files or rewrite immutable tags as a recovery shortcut. Reload after recovery.

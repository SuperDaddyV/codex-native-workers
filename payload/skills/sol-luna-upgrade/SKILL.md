---
name: sol-luna-upgrade
description: Safely resolve and apply a requested Codex Native Workers Sol/Luna release upgrade, including prereleases, with immutable-tag and transactional-write checks.
---

# Sol/Luna upgrade

Use this Skill for a user-requested Codex Native Workers release upgrade; the legacy Sol/Luna invocation remains supported. It governs the product's release workflow; it does not change Coordinator/Worker role selection, model choice, or delegation policy.

## Authorization boundary

The request "upgrade Codex Native Workers" or "upgrade Sol/Luna to the latest version" explicitly authorizes the latest published project version, including prereleases. Do not ask Stable or Preview again. A request to inspect, plan, or report an upgrade does not authorize an apply. The authorization covers this product upgrade only; it does not authorize unrelated configuration repair, commit, push, tag, Release publication, or other GitHub writes. If a required source, release, tag, or installer check is unavailable, fail closed without writes.

## Resolve the target release

- Release discovery is a semantic workflow outside the installer. Request all pages of `/repos/SuperDaddyV/codex-native-workers/releases`.
- Accept only entries with `draft = false`, non-null `published_at`, and a strict project SemVer tag.
- Reject build metadata, malformed leading zeroes, a mismatch between the Release prerelease flag and the SemVer prerelease, and duplicate Releases with the same normalized version. Choose by SemVer precedence, never by publication time.
- If the target is a prerelease, show this notice before any apply:
  `目标：<version>`
  `渠道：Prerelease / Public Beta`
  `此版本可能包含尚未完成的变化，外部真实运行验证少于稳定版。`
  `修改托管文件前会创建事务备份；不会有意覆盖与本项目无关的用户配置。`

## Pin and apply

- Resolve the Release tag through its direct ref, peel either an annotated or lightweight tag to one exact 40-hex commit, and acquire a detached checkout. Read the tag again after checkout; if it moved, fail closed as `TAG_MOVED`.
- Before apply, verify detached `HEAD`, installer `VERSION`, the Release tag, and the setup/source contract all identify the same target. Pass the verified commit to the installer as `--source-commit <40hex>`.
- Resolve and validate both managed roots as one two-root transaction, prevalidate every backup and rollback entry before writing either root, then pass explicit `--codex-home <CODEX_HOME>` and `--skills-root <HOME>/.agents/skills` values to installer dry-run and apply. If an installed manifest records a different Skill root, stop; do not redirect or copy managed Skills implicitly.
- Never install from `master`, `target_commitish`, another mutable branch, or an unverified tag.
- If the installed version is already the target, perform zero writes and zero backups. If the installed version is newer by SemVer precedence, never downgrade automatically.
- Apply only through the transaction-aware installer after all checks and the prerelease notice have passed. Preserve unrelated user configuration; any ownership mismatch or unexpected change is a stop condition, not permission to overwrite.

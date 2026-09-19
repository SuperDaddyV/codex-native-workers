import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import scripts.install as installer_module
from scripts.install import (
    AGENT_FILES,
    AGENTS_BEGIN,
    AGENTS_END,
    CONFIG_BEGIN,
    CONFIG_END,
    InstallerError,
    MANIFEST_RELATIVE,
    SCHEMA2_SKILL_FILES,
    STABLE_AGENT_FILES,
    SOL_AGENT_FILES,
    VERSION,
    dry_run_install,
    install,
    rollback,
    uninstall,
)
from src.selector import USER_AGENT


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_ROOT = ROOT / ".tmp" / "installer-validation" / "lifecycle-tests"
FIXED_TIME = datetime(2026, 8, 12, 0, 0, tzinfo=timezone.utc)
LEGACY_FIXTURE = ROOT / "fixtures" / "legacy-v3" / "manifest-3.2.json"
PUBLISHED_V420_RC1_COMMIT = "527b174df13643a38bfe29652208eaa00f63fbf7"
PUBLISHED_V420_RC1_USER_AGENT = b"codex-sol-luna-worker/4.2.0-rc1"
PUBLISHED_V420_RC1_SELECTOR_SHA256 = (
    "c2f0ab9f93179f7feb13b7c76d1a3b83e0e4bc9784a550bfe18f0ae6e50e2225"
)
PUBLISHED_V420_RC1_RELEASES_PATH = (
    b"/repos/SuperDaddyV/codex-sol-luna-worker/releases"
)
PUBLISHED_V420_RC1_UPGRADE_SKILL_SHA256 = (
    "90e28bbd9c2af29164526f22ae0d0a2c101c97da1b05d41f1496715a7e82cd33"
)
STABLE_V420_RELEASES_PATH = b"/repos/SuperDaddyV/codex-native-workers/releases"


def sandbox():
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=VALIDATION_ROOT)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def mutate_owned_policy(path: Path) -> tuple[bytes, bytes]:
    original = path.read_bytes()
    begin = AGENTS_BEGIN.encode("utf-8")
    end = AGENTS_END.encode("utf-8")
    payload_start = original.index(begin) + len(begin)
    payload_end = original.index(end, payload_start)
    mutation_offset = original.index(b" ", payload_start, payload_end)
    mutated = (
        original[:mutation_offset]
        + b"\t"
        + original[mutation_offset + 1 :]
    )
    if mutated == original:
        raise AssertionError("owned policy mutation was a no-op")
    path.write_bytes(mutated)
    return original, mutated


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def installation_hash(target: Path) -> str:
    """Hash both managed roots, including whether either root exists."""

    digest = hashlib.sha256()
    roots = (
        ("codex_home", target),
        ("skills_root", target.parent / ".agents" / "skills"),
    )
    for label, root in roots:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(b"1" if root.exists() else b"0")
        digest.update(b"\0")
        digest.update(tree_hash(root).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def simulate_rc1_managed_policy(target: Path) -> None:
    agents_path = target / "AGENTS.md"
    policy = agents_path.read_text(encoding="utf-8")
    receipt_start = policy.index("## Receipts")
    end_start = policy.index(AGENTS_END, receipt_start)
    rc1_policy = policy[:receipt_start] + policy[end_start:]
    rc1_policy = rc1_policy.replace("- Never select `ultra` for Luna.\n", "")
    agents_path.write_bytes(rc1_policy.encode("utf-8"))

    block_start = rc1_policy.index(AGENTS_BEGIN)
    block_finish = rc1_policy.index(AGENTS_END, block_start) + len(AGENTS_END)
    if block_finish < len(rc1_policy) and rc1_policy[block_finish] == "\r":
        block_finish += 1
    if block_finish < len(rc1_policy) and rc1_policy[block_finish] == "\n":
        block_finish += 1

    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = "v4.1.0-rc1"
    manifest["owned_blocks"]["AGENTS.md"]["sha256"] = hashlib.sha256(
        rc1_policy[block_start:block_finish].encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def simulate_rc3_managed_policy(target: Path) -> None:
    agents_path = target / "AGENTS.md"
    policy = agents_path.read_text(encoding="utf-8")
    receipts_start = policy.index("## Receipts")
    end_start = policy.index(AGENTS_END, receipts_start)
    legacy_receipts = (
        "## Receipts\n\n"
        "- Use `LUNA_UNAVAILABLE` only after a current-task selector or capability failure.\n"
        "- Build the final receipt only from facts already collected during the task.\n\n"
    )
    rc3_policy = (
        policy[:receipts_start] + legacy_receipts + policy[end_start:]
    )
    agents_path.write_bytes(rc3_policy.encode("utf-8"))

    block_start = rc3_policy.index(AGENTS_BEGIN)
    block_finish = rc3_policy.index(AGENTS_END, block_start) + len(AGENTS_END)
    if block_finish < len(rc3_policy) and rc3_policy[block_finish] == "\r":
        block_finish += 1
    if block_finish < len(rc3_policy) and rc3_policy[block_finish] == "\n":
        block_finish += 1

    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = "v4.1.0-rc3"
    manifest["owned_blocks"]["AGENTS.md"]["sha256"] = hashlib.sha256(
        rc3_policy[block_start:block_finish].encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def simulate_rc4_managed_install(target: Path) -> None:
    agents_path = target / "AGENTS.md"
    policy = agents_path.read_text(encoding="utf-8")
    end_start = policy.index(AGENTS_END)
    policy = (
        policy[:end_start]
        + "- Legacy RC4 receipt: record one selected role and observed outcome.\n"
        + policy[end_start:]
    )
    agents_path.write_bytes(policy.encode("utf-8"))

    block_start = policy.index(AGENTS_BEGIN)
    block_finish = policy.index(AGENTS_END, block_start) + len(AGENTS_END)
    if block_finish < len(policy) and policy[block_finish] == "\r":
        block_finish += 1
    if block_finish < len(policy) and policy[block_finish] == "\n":
        block_finish += 1

    selector_relative = "sol-luna-v4/selector.py"
    selector_path = target / selector_relative
    selector = b"# simulated manifest-owned RC4 selector\n" + selector_path.read_bytes()
    selector_path.write_bytes(selector)
    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = "v4.1.0-rc4"
    manifest.pop("source_commit", None)
    manifest["owned_files"][selector_relative] = hashlib.sha256(selector).hexdigest()
    manifest["owned_blocks"]["AGENTS.md"]["sha256"] = hashlib.sha256(
        policy[block_start:block_finish].encode("utf-8")
    ).hexdigest()

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def simulate_schema2_local1(target: Path) -> None:
    """Convert a fresh install to the exact two-Skill local.1 schema-2 layout."""

    call_install(target)
    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    skills_root = Path(manifest["skills_root"])
    delegate_skill = skills_root / "sol-luna-delegate" / "SKILL.md"
    if delegate_skill.is_file():
        delegate_skill.unlink()
        delegate_skill.parent.rmdir()
    for filename in SOL_AGENT_FILES:
        path = target / "agents" / filename
        if path.is_file():
            path.unlink()
    worker_module = target / "sol-luna-v4" / "worker_selector.py"
    if worker_module.is_file():
        worker_module.unlink()

    selector_relative = "sol-luna-v4/selector.py"
    selector_path = target / selector_relative
    selector = selector_path.read_bytes().replace(
        USER_AGENT.encode("ascii"),
        b"codex-sol-luna-worker/4.2.0-local.1",
    )
    selector_path.write_bytes(selector)
    manifest["schema_version"] = 2
    manifest["version"] = "v4.2.0-local.1"
    manifest["owned_files"] = {
        **{
            f"agents/{filename}": hashlib.sha256(
                (target / "agents" / filename).read_bytes()
            ).hexdigest()
            for filename in STABLE_AGENT_FILES
        },
        selector_relative: hashlib.sha256(selector).hexdigest(),
    }

    config_path = target / "config.toml"
    config_bytes = config_path.read_bytes().replace(
        b"max_concurrent_threads_per_session = 6",
        b"max_concurrent_threads_per_session = 3",
    )
    config_path.write_bytes(config_bytes)
    config = config_bytes.decode("utf-8")
    config_start = config.index(CONFIG_BEGIN)
    config_finish = config.index(CONFIG_END, config_start) + len(CONFIG_END)
    if config_finish < len(config) and config[config_finish] == "\r":
        config_finish += 1
    if config_finish < len(config) and config[config_finish] == "\n":
        config_finish += 1
    manifest["owned_blocks"]["config.toml"]["sha256"] = hashlib.sha256(
        config[config_start:config_finish].encode("utf-8")
    ).hexdigest()
    manifest["owned_skill_files"] = {
        relative: digest
        for relative, digest in manifest["owned_skill_files"].items()
        if relative in {f"{name}/SKILL.md" for name in SCHEMA2_SKILL_FILES}
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def simulate_v414_managed_install(target: Path) -> None:
    """Convert a current fake install into a manifest-owned v4.1.4 layout."""

    agents_path = target / "AGENTS.md"
    policy = agents_path.read_text(encoding="utf-8")
    # Freeze a representative old owned policy instead of replacing phrases in
    # the evolving current template (which can silently become a no-op).
    payload_start = policy.index(AGENTS_BEGIN) + len(AGENTS_BEGIN)
    payload_end = policy.index(AGENTS_END, payload_start)
    policy = (
        policy[:payload_start]
        + "\n# Sol + Luna native delegation\n\n"
        + "- Sol is the sole planner, orchestrator, ambiguity resolver, and final acceptance owner.\n"
        + "- Luna executes bounded tasks and returns evidence to Sol.\n"
        + policy[payload_end:]
    )
    agents_path.write_bytes(policy.encode("utf-8"))

    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for filename in STABLE_AGENT_FILES:
        relative = f"agents/{filename}"
        path = target / relative
        payload = path.read_text(encoding="utf-8").replace(
            "parent Coordinator", "parent Sol agent"
        )
        path.write_text(payload, encoding="utf-8")
        manifest["owned_files"][relative] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    selector_relative = "sol-luna-v4/selector.py"
    selector_path = target / selector_relative
    selector = selector_path.read_bytes().replace(
        USER_AGENT.encode("ascii"),
        b"codex-sol-luna-worker/4.1.4",
    )
    selector_path.write_bytes(selector)
    manifest["owned_files"] = {
        **{
            f"agents/{filename}": hashlib.sha256(
                (target / "agents" / filename).read_bytes()
            ).hexdigest()
            for filename in STABLE_AGENT_FILES
        },
        selector_relative: hashlib.sha256(selector).hexdigest(),
    }

    for filename in SOL_AGENT_FILES:
        (target / "agents" / filename).unlink()
    worker_module = target / "sol-luna-v4" / "worker_selector.py"
    if worker_module.is_file():
        worker_module.unlink()

    block_start = policy.index(AGENTS_BEGIN)
    block_finish = policy.index(AGENTS_END, block_start) + len(AGENTS_END)
    if block_finish < len(policy) and policy[block_finish] == "\r":
        block_finish += 1
    if block_finish < len(policy) and policy[block_finish] == "\n":
        block_finish += 1
    manifest["owned_blocks"]["AGENTS.md"]["sha256"] = hashlib.sha256(
        policy[block_start:block_finish].encode("utf-8")
    ).hexdigest()
    config_path = target / "config.toml"
    config_bytes = config_path.read_bytes().replace(
        b"max_concurrent_threads_per_session = 6",
        b"max_concurrent_threads_per_session = 3",
    )
    config_path.write_bytes(config_bytes)
    config = config_bytes.decode("utf-8")
    config_start = config.index(CONFIG_BEGIN)
    config_finish = config.index(CONFIG_END, config_start) + len(CONFIG_END)
    if config_finish < len(config) and config[config_finish] == "\r":
        config_finish += 1
    if config_finish < len(config) and config[config_finish] == "\n":
        config_finish += 1
    manifest["owned_blocks"]["config.toml"]["sha256"] = hashlib.sha256(
        config[config_start:config_finish].encode("utf-8")
    ).hexdigest()

    skills_root = target.parent / ".agents" / "skills"
    for relative in manifest.get("owned_skill_files", {}):
        path = skills_root.joinpath(*Path(relative).parts)
        if path.is_file():
            path.unlink()
            path.parent.rmdir()
    if skills_root.exists() and not any(skills_root.iterdir()):
        skills_root.rmdir()
    if skills_root.parent.exists() and not any(skills_root.parent.iterdir()):
        skills_root.parent.rmdir()

    manifest["schema_version"] = 1
    manifest["version"] = "v4.1.4"
    manifest["source_commit"] = "71894e2ef5007c9ba3e6f9d9efbf91cbdad302b4"
    manifest.pop("skills_root", None)
    manifest.pop("owned_skill_files", None)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def call_install(target: Path, **kwargs):
    return install(
        target,
        project_root=ROOT,
        generated_at=kwargs.pop("generated_at", FIXED_TIME),
        allow_validation_sandbox=True,
        **kwargs,
    )


def simulate_published_v420_rc1_install(target: Path) -> None:
    """Materialize the published rc1 payload in an isolated fake home."""

    call_install(target, source_commit=PUBLISHED_V420_RC1_COMMIT)
    manifest_path = target / MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    selector_relative = "sol-luna-v4/selector.py"
    selector_path = target / selector_relative
    selector = selector_path.read_bytes()
    stable_user_agent = USER_AGENT.encode("ascii")
    if selector.count(stable_user_agent) != 1:
        raise AssertionError("stable selector User-Agent fixture is not unique")
    selector = selector.replace(stable_user_agent, PUBLISHED_V420_RC1_USER_AGENT)
    selector_digest = hashlib.sha256(selector).hexdigest()
    if selector_digest != PUBLISHED_V420_RC1_SELECTOR_SHA256:
        raise AssertionError("selector does not match the published rc1 payload")
    selector_path.write_bytes(selector)

    upgrade_relative = "sol-luna-upgrade/SKILL.md"
    skills_root = Path(manifest["skills_root"])
    upgrade_path = skills_root / upgrade_relative
    upgrade_skill = upgrade_path.read_bytes()
    if upgrade_skill.count(STABLE_V420_RELEASES_PATH) != 1:
        raise AssertionError("Stable release endpoint fixture is not unique")
    upgrade_skill = upgrade_skill.replace(
        STABLE_V420_RELEASES_PATH,
        PUBLISHED_V420_RC1_RELEASES_PATH,
    )
    upgrade_digest = hashlib.sha256(upgrade_skill).hexdigest()
    if upgrade_digest != PUBLISHED_V420_RC1_UPGRADE_SKILL_SHA256:
        raise AssertionError("upgrade Skill does not match the published rc1 payload")
    upgrade_path.write_bytes(upgrade_skill)

    manifest["version"] = "v4.2.0-rc1"
    manifest["source_commit"] = PUBLISHED_V420_RC1_COMMIT
    manifest["owned_files"][selector_relative] = selector_digest
    manifest["owned_skill_files"][upgrade_relative] = upgrade_digest
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def materialize_legacy_fixture(target: Path) -> dict:
    fixture = json.loads(LEGACY_FIXTURE.read_text(encoding="utf-8"))
    fixture["created_files"] = [
        path.replace("<installation>", "fixture")
        for path in fixture["created_files"]
    ]
    target.mkdir(parents=True, exist_ok=True)
    for relative in fixture["created_files"]:
        if relative in {"hooks.json", "sol-luna-router/install-manifest.json"}:
            continue
        write_text(target / relative, "legacy owned fixture\n")

    write_text(
        target / "config.toml",
        'user_model = "preserve"\n'
        "# BEGIN SOL_LUNA_DAILY_BEST_FEATURES\n"
        "legacy_feature = true\n"
        "# END SOL_LUNA_DAILY_BEST_FEATURES\n"
        "# BEGIN SOL_LUNA_DAILY_BEST_AGENTS\n"
        'legacy_worker = "remove"\n'
        "# END SOL_LUNA_DAILY_BEST_AGENTS\n",
    )
    write_text(
        target / "AGENTS.md",
        "User instruction stays.\n"
        "<!-- BEGIN SOL_LUNA_DAILY_BEST -->\n"
        "Legacy owned policy.\n"
        "<!-- END SOL_LUNA_DAILY_BEST -->\n",
    )
    old_group = {
        "hooks": [
            {
                "type": "command",
                "command": "python hooks/sol_luna_router.py",
            }
        ]
    }
    user_group = {
        "hooks": [{"type": "command", "command": "python hooks/user_hook.py"}]
    }
    hooks = {
        "description": "user and legacy hooks",
        "hooks": {
            "PreToolUse": [user_group, old_group],
            "SubagentStart": [old_group],
            "SubagentStop": [old_group],
            "SessionStart": [old_group],
        },
    }
    write_text(target / "hooks.json", json.dumps(hooks, indent=2) + "\n")
    write_text(target / "hooks" / "user_hook.py", "# user hook\n")
    write_text(target / "agents" / "user-agent.toml", 'name = "user_agent"\n')
    write_text(target / "sol-luna-router" / "user-note.txt", "preserve\n")
    write_text(
        target / "sol-luna-router" / "install-manifest.json",
        json.dumps(fixture, indent=2) + "\n",
    )
    return fixture


class InstallerLifecycleTests(unittest.TestCase):
    def test_rollback_corrupt_late_backup_preserves_both_roots(self):
        for backup_root_name in ("codex_home", "skills_root"):
            for damage in ("hash", "missing"):
                with self.subTest(root=backup_root_name, damage=damage), sandbox() as directory:
                    target = Path(directory) / ".codex"
                    write_text(target / "AGENTS.md", "user policy\n")
                    write_text(target / "config.toml", 'user_setting = "keep"\n')
                    installed = call_install(target)
                    relative = "config.toml"
                    if backup_root_name == "skills_root":
                        relative = "sol-luna-upgrade/SKILL.md"
                        skill = target.parent / ".agents" / "skills" / relative
                        skill.write_bytes(skill.read_bytes() + b"\nprevious candidate\n")
                        manifest_path = target / MANIFEST_RELATIVE
                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        manifest["owned_skill_files"][relative] = hashlib.sha256(
                            skill.read_bytes()
                        ).hexdigest()
                        write_text(manifest_path, json.dumps(manifest))
                        installed = call_install(target)
                    backup = Path(installed["backup"])
                    payload = backup / "files" / backup_root_name / relative
                    if damage == "hash":
                        payload.write_bytes(b"corrupt backup fixture\n")
                    else:
                        payload.unlink()
                    before = installation_hash(target)
                    with self.assertRaises(InstallerError) as raised:
                        rollback(target, backup, project_root=ROOT, allow_validation_sandbox=True)
                    self.assertEqual(raised.exception.reason_code, "BACKUP_INVALID")
                    self.assertEqual(installation_hash(target), before)
                    self.assertTrue(backup.is_dir())

    def test_rollback_invalid_late_entry_preserves_both_roots(self):
        for invalid_entry in (
            {"root": "unknown", "path": "later", "existed": False},
            {"root": "codex_home", "path": "../outside", "existed": False},
            {"root": "codex_home", "path": "AGENTS.md", "existed": False},
            {"root": "codex_home", "path": "later", "existed": "false"},
            None,
        ):
            with self.subTest(entry=invalid_entry), sandbox() as directory:
                target = Path(directory) / ".codex"
                write_text(target / "AGENTS.md", "user policy\n")
                installed = call_install(target)
                backup = Path(installed["backup"])
                snapshot_path = backup / "snapshot.json"
                snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                snapshot["entries"].append(invalid_entry)
                write_text(snapshot_path, json.dumps(snapshot))
                before = installation_hash(target)
                with self.assertRaises(InstallerError) as raised:
                    rollback(target, backup, project_root=ROOT, allow_validation_sandbox=True)
                self.assertEqual(raised.exception.reason_code, "BACKUP_INVALID")
                self.assertEqual(installation_hash(target), before)

    def test_rollback_legacy_single_root_backup_remains_supported(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "AGENTS.md", "installed policy\n")
            backup = target / "backups" / "sol-luna-v4" / "legacy-fixture"
            original = b"original user policy\n"
            (backup / "files").mkdir(parents=True)
            (backup / "files" / "AGENTS.md").write_bytes(original)
            write_text(backup / "snapshot.json", json.dumps({
                "schema_version": 1,
                "target_existed": True,
                "entries": [{
                    "path": "AGENTS.md",
                    "existed": True,
                    "sha256": hashlib.sha256(original).hexdigest(),
                }],
            }))
            result = rollback(
                target, backup, project_root=ROOT, allow_validation_sandbox=True
            )
            self.assertEqual(result["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual((target / "AGENTS.md").read_bytes(), original)
            self.assertFalse(backup.exists())

    def test_schema3_invalid_skill_inventory_rejects_all_lifecycle_modes(self):
        for damage in ("empty", "missing", "extra", "bad-hash"):
            with self.subTest(damage=damage), sandbox() as directory:
                target = Path(directory) / ".codex"
                call_install(target)
                manifest_path = target / MANIFEST_RELATIVE
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                owned = manifest["owned_skill_files"]
                if damage == "empty":
                    owned.clear()
                elif damage == "missing":
                    del owned["sol-luna-status/SKILL.md"]
                elif damage == "extra":
                    owned["user-skill/SKILL.md"] = "0" * 64
                else:
                    owned["sol-luna-status/SKILL.md"] = "invalid"
                write_text(manifest_path, json.dumps(manifest))
                before = installation_hash(target)
                other_root = target.parent / "other-skills"
                for action in (dry_run_install, install, uninstall):
                    with self.subTest(action=action.__name__):
                        with self.assertRaises(InstallerError) as raised:
                            action(target, skills_root=other_root, project_root=ROOT,
                                   allow_validation_sandbox=True)
                        self.assertEqual(raised.exception.reason_code, "MANIFEST_INVALID")
                        self.assertEqual(installation_hash(target), before)
                        self.assertFalse(other_root.exists())

    def test_schema2_keeps_exact_legacy_two_skill_inventory(self):
        for damage in ("empty", "missing", "extra", "bad-hash"):
            with self.subTest(damage=damage), sandbox() as directory:
                target = Path(directory) / ".codex"
                simulate_schema2_local1(target)
                manifest_path = target / MANIFEST_RELATIVE
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                owned = manifest["owned_skill_files"]
                if damage == "empty":
                    owned.clear()
                elif damage == "missing":
                    del owned["sol-luna-status/SKILL.md"]
                elif damage == "extra":
                    owned["sol-luna-delegate/SKILL.md"] = "0" * 64
                else:
                    owned["sol-luna-status/SKILL.md"] = "invalid"
                write_text(manifest_path, json.dumps(manifest))
                before = installation_hash(target)
                for action in (dry_run_install, install, uninstall):
                    with self.subTest(action=action.__name__):
                        with self.assertRaises(InstallerError) as raised:
                            action(
                                target,
                                project_root=ROOT,
                                allow_validation_sandbox=True,
                            )
                        self.assertEqual(
                            raised.exception.reason_code, "MANIFEST_INVALID"
                        )
                        self.assertEqual(installation_hash(target), before)

    def test_schema2_upgrade_preserves_daily_and_lkg_state_and_installs_v3(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            simulate_schema2_local1(target)
            state = target / "sol-luna-v4" / "state"
            write_text(state / "daily-profile.json", '{"role":"luna_high"}\n')
            write_text(state / "last-good-profile.json", '{"role":"luna_max"}\n')
            state_before = {
                path.name: path.read_bytes() for path in state.iterdir() if path.is_file()
            }
            old_manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(old_manifest["schema_version"], 2)
            self.assertEqual(
                set(old_manifest["owned_skill_files"]),
                {f"{name}/SKILL.md" for name in SCHEMA2_SKILL_FILES},
            )
            before = installation_hash(target)
            dry = dry_run_install(
                target,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(installation_hash(target), before)

            upgraded = call_install(target, generated_at=FIXED_TIME + timedelta(days=1))
            self.assertEqual(upgraded["status"], "UPGRADED")
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(
                {path for path in manifest["owned_files"] if path.startswith("agents/")},
                {f"agents/{filename}" for filename in AGENT_FILES},
            )
            self.assertEqual(len(manifest["owned_skill_files"]), 3)
            self.assertTrue((target / "sol-luna-v4" / "worker_selector.py").is_file())
            self.assertTrue(
                (target.parent / ".agents" / "skills" / "sol-luna-delegate" / "SKILL.md").is_file()
            )
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in state.iterdir()
                    if path.is_file()
                },
                state_before,
            )

            rollback(
                target,
                Path(upgraded["backup"]),
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            restored = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(restored["schema_version"], 2)
            self.assertEqual(installation_hash(target), before)

    def test_schema3_inventory_or_module_corruption_has_no_partial_mutation(self):
        for damage in (
            "missing-agent",
            "extra-agent",
            "missing-module",
            "bad-agent-hash",
            "missing-skill",
            "modified-module",
        ):
            with self.subTest(damage=damage), sandbox() as directory:
                target = Path(directory) / ".codex"
                installed = call_install(target)
                backup = Path(installed["backup"])
                backup_before = tree_hash(backup)
                manifest_path = target / MANIFEST_RELATIVE
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                expected_reason = "MANIFEST_INVALID"
                if damage == "missing-agent":
                    del manifest["owned_files"]["agents/sol-low.toml"]
                elif damage == "extra-agent":
                    manifest["owned_files"]["agents/user.toml"] = "0" * 64
                elif damage == "missing-module":
                    del manifest["owned_files"]["sol-luna-v4/worker_selector.py"]
                elif damage == "bad-agent-hash":
                    manifest["owned_files"]["agents/sol-low.toml"] = "invalid"
                elif damage == "missing-skill":
                    del manifest["owned_skill_files"]["sol-luna-delegate/SKILL.md"]
                else:
                    expected_reason = "OWNERSHIP_CONFLICT"
                    module = target / "sol-luna-v4" / "worker_selector.py"
                    module.write_bytes(module.read_bytes() + b"\n# altered\n")
                if damage != "modified-module":
                    write_text(manifest_path, json.dumps(manifest))
                before = installation_hash(target)
                for action in (dry_run_install, install, uninstall, rollback):
                    with self.subTest(action=action.__name__):
                        with self.assertRaises(InstallerError) as raised:
                            if action is rollback:
                                action(
                                    target,
                                    backup,
                                    project_root=ROOT,
                                    allow_validation_sandbox=True,
                                )
                            else:
                                action(
                                    target,
                                    project_root=ROOT,
                                    allow_validation_sandbox=True,
                                )
                        self.assertEqual(raised.exception.reason_code, expected_reason)
                        self.assertEqual(installation_hash(target), before)
                        self.assertEqual(tree_hash(backup), backup_before)

    def test_skill_root_and_parent_creation_ownership_survives_lifecycle(self):
        for root_existed, parent_existed in ((False, False), (False, True), (True, True)):
            for action in ("rollback", "uninstall"):
                with self.subTest(root=root_existed, parent=parent_existed, action=action), sandbox() as directory:
                    target = Path(directory) / ".codex"
                    skills_root = target.parent / ".agents" / "skills"
                    if parent_existed:
                        skills_root.parent.mkdir()
                    if root_existed:
                        skills_root.mkdir()
                    installed = call_install(target)
                    self.assertEqual(call_install(target)["status"], "IDEMPOTENT_PASS")
                    if action == "rollback":
                        rollback(target, Path(installed["backup"]), project_root=ROOT,
                                 allow_validation_sandbox=True)
                    else:
                        uninstall(target, project_root=ROOT, allow_validation_sandbox=True)
                    self.assertEqual(skills_root.exists(), root_existed)
                    self.assertEqual(skills_root.parent.exists(), parent_existed)

    def test_older_schema2_without_directory_ownership_preserves_empty_roots(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            simulate_schema2_local1(target)
            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop("skill_root_created", None)
            manifest.pop("skill_parent_created", None)
            write_text(manifest_path, json.dumps(manifest))
            call_install(target)
            uninstall(target, project_root=ROOT, allow_validation_sandbox=True)
            self.assertTrue((target.parent / ".agents" / "skills").is_dir())

    def test_uninstall_codex_phase_failure_restores_completed_skill_phase(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            call_install(target)
            before = installation_hash(target)
            original = installer_module._apply_operations
            skills_root = target.parent / ".agents" / "skills"
            observed = []

            def fail_codex_phase(managed_root, operations):
                if managed_root == target:
                    observed.append(not any(skills_root.rglob("SKILL.md")))
                    raise InstallerError("OWNERSHIP_CONFLICT", "forced codex phase failure")
                original(managed_root, operations)

            with patch("scripts.install._apply_operations", side_effect=fail_codex_phase):
                with self.assertRaises(InstallerError) as raised:
                    uninstall(target, project_root=ROOT, allow_validation_sandbox=True)
            self.assertEqual(observed, [True])
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(installation_hash(target), before)

    def test_clean_install_installs_only_native_v4_artifacts(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            result = call_install(target)

            self.assertEqual(result["status"], "INSTALLED")
            self.assertGreater(result["effective_changes"], 0)
            self.assertEqual(
                {path.name for path in (target / "agents").glob("*.toml")},
                set(AGENT_FILES),
            )
            for path in (target / "agents").glob("*.toml"):
                with path.open("rb") as handle:
                    agent = tomllib.load(handle)
                self.assertEqual(
                    agent["model"],
                    "gpt-5.6-sol" if path.name.startswith("sol-") else "gpt-5.6-luna",
                )
                self.assertFalse(agent["agents"]["enabled"])
            installed_policy = (target / "AGENTS.md").read_text(encoding="utf-8")
            skills_root = target.parent / ".agents" / "skills"
            status_skill = (skills_root / "sol-luna-status" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(AGENTS_BEGIN, installed_policy)
            self.assertNotIn(str(target.resolve()), installed_policy)
            self.assertIn("sol-luna-delegate", installed_policy)
            self.assertNotIn("--ensure-daily", installed_policy)
            self.assertNotIn("--print-selection", installed_policy)
            self.assertNotIn("--status-json", installed_policy)
            self.assertIn("--status-json", status_skill)
            self.assertNotIn("<STATUS_COMMAND>", status_skill)
            delegate_skill = (
                skills_root / "sol-luna-delegate" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn("--workers", delegate_skill)
            self.assertIn(str(target.resolve()), delegate_skill)
            self.assertNotIn("<SELECTOR_COMMAND>", delegate_skill)
            self.assertNotIn(".var", installed_policy)
            self.assertIn(
                CONFIG_BEGIN, (target / "config.toml").read_text(encoding="utf-8")
            )
            self.assertTrue((target / "sol-luna-v4" / "selector.py").is_file())
            self.assertTrue((target / "sol-luna-v4" / "worker_selector.py").is_file())
            self.assertTrue((target / MANIFEST_RELATIVE).is_file())
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(manifest["version"], VERSION)
            self.assertEqual(len(manifest["owned_files"]), 12)
            self.assertEqual(
                {path for path in manifest["owned_files"] if path.startswith("agents/")},
                {f"agents/{filename}" for filename in AGENT_FILES},
            )
            self.assertEqual(len(manifest["owned_skill_files"]), 3)
            self.assertEqual(Path(manifest["skills_root"]), skills_root.resolve())
            self.assertEqual(set(manifest["owned_blocks"]), {"AGENTS.md", "config.toml"})
            self.assertNotIn("installation_id", manifest)
            self.assertTrue(Path(result["backup"]).is_dir())
            self.assertFalse((target / "hooks.json").exists())
            self.assertFalse((target / "hooks").exists())
            self.assertFalse((target / ".var").exists())
            self.assertFalse((target / "daily-profile.json").exists())

    def test_merge_preserves_config_agents_policy_hooks_and_user_agents(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            original_agents = "User policy remains.\n"
            original_hook = b'{"hooks":{"UserEvent":[{"command":"user"}]}}\n'
            write_text(
                target / "config.toml",
                'model = "user-model"\n'
                "[mcp_servers.user]\n"
                'command = "user-tool"\n'
                "[agents]\n"
                'user_option = "keep"\n',
            )
            write_text(target / "AGENTS.md", original_agents)
            write_text(target / "agents" / "user-agent.toml", 'name = "user_agent"\n')
            (target / "hooks.json").write_bytes(original_hook)

            call_install(target)
            config = tomllib.loads(
                (target / "config.toml").read_text(encoding="utf-8")
            )
            self.assertEqual(config["model"], "user-model")
            self.assertEqual(config["mcp_servers"]["user"]["command"], "user-tool")
            self.assertEqual(config["agents"]["user_option"], "keep")
            self.assertTrue(config["agents"]["enabled"])
            self.assertEqual(config["agents"]["max_concurrent_threads_per_session"], 6)
            self.assertTrue(
                (target / "AGENTS.md")
                .read_text(encoding="utf-8")
                .startswith(original_agents)
            )
            self.assertEqual(
                (target / "agents" / "user-agent.toml").read_text(encoding="utf-8"),
                'name = "user_agent"\n',
            )
            self.assertEqual((target / "hooks.json").read_bytes(), original_hook)

    def test_nonempty_agents_override_fails_closed_without_changes(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            write_text(target / "AGENTS.override.md", "User override takes priority.\n")
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "AGENTS_OVERRIDE_PRESENT")
            self.assertEqual(tree_hash(target), before)

    def test_second_install_is_idempotent(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            before = installation_hash(target)
            backups_before = list((target / "backups" / "sol-luna-v4").iterdir())
            second = call_install(target)
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertEqual(second["backup"], None)
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(
                len(list((target / "backups" / "sol-luna-v4").iterdir())),
                len(backups_before),
            )

    def test_existing_agents_table_is_idempotent_and_uninstalls_exactly(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            original_config = (
                'model = "user-model"\n'
                "[agents]\n"
                'user_option = "keep"\n'
                "[mcp_servers.user]\n"
                'command = "user-tool"\n'
            )
            write_text(target / "config.toml", original_config)

            call_install(target)
            second = call_install(target)
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)

            result = uninstall(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
            )
            self.assertEqual(result["status"], "UNINSTALLED")
            self.assertEqual(
                (target / "config.toml").read_text(encoding="utf-8"), original_config
            )

    def test_upgrade_restores_leaf_removes_owned_experiment_and_rolls_back(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            skills_root = Path(manifest["skills_root"])
            for relative in manifest["owned_skill_files"]:
                skill = skills_root.joinpath(*Path(relative).parts)
                skill.unlink()
                skill.parent.rmdir()
            if skills_root.exists() and not any(skills_root.iterdir()):
                skills_root.rmdir()
            if skills_root.parent.exists() and not any(skills_root.parent.iterdir()):
                skills_root.parent.rmdir()
            for filename in SOL_AGENT_FILES:
                (target / "agents" / filename).unlink()
            worker_module = target / "sol-luna-v4" / "worker_selector.py"
            worker_module.unlink()
            selector_relative = "sol-luna-v4/selector.py"
            selector_path = target / selector_relative
            selector = (
                b"# simulated manifest-owned v4.0 payload\n"
                + selector_path.read_bytes()
            )
            selector_path.write_bytes(selector)
            manifest["schema_version"] = 1
            manifest["owned_files"] = {
                **{
                    f"agents/{filename}": hashlib.sha256(
                        (target / "agents" / filename).read_bytes()
                    ).hexdigest()
                    for filename in STABLE_AGENT_FILES
                },
                selector_relative: hashlib.sha256(selector).hexdigest(),
            }
            for key in (
                "owned_skill_files",
                "skills_root",
                "skill_root_created",
                "skill_parent_created",
            ):
                manifest.pop(key, None)
            for filename in STABLE_AGENT_FILES:
                path = target / "agents" / filename
                prototype = path.read_text(encoding="utf-8").replace(
                    "\n[agents]\nenabled = false\n", "\n"
                )
                self.assertNotIn("enabled = false", prototype)
                write_text(path, prototype)
                manifest["owned_files"][f"agents/{filename}"] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
            experiment_relative = "agents/luna-leaf-experiment.toml"
            experiment = b'name = "luna_leaf_experiment"\n'
            (target / experiment_relative).write_bytes(experiment)
            manifest["owned_files"][experiment_relative] = hashlib.sha256(
                experiment
            ).hexdigest()
            manifest["version"] = "v4.0.0-prototype"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            write_text(target / "agents" / "user-agent.toml", 'name = "user_agent"\n')
            before = tree_hash(target)

            upgraded = call_install(target, generated_at=FIXED_TIME + timedelta(days=1))
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertFalse((target / experiment_relative).exists())
            for filename in STABLE_AGENT_FILES:
                with (target / "agents" / filename).open("rb") as handle:
                    self.assertFalse(tomllib.load(handle)["agents"]["enabled"])
            self.assertEqual(
                (target / "agents" / "user-agent.toml").read_text(encoding="utf-8"),
                'name = "user_agent"\n',
            )
            self.assertTrue(Path(upgraded["backup"]).is_dir())

            rolled_back = rollback(
                target,
                Path(upgraded["backup"]),
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)

    def test_v40_manifest_owned_selector_upgrades_to_stable_and_rolls_back(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", 'user_setting = "preserve"\n')
            write_text(target / "AGENTS.md", "User policy remains.\n")
            call_install(target)

            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            selector_relative = "sol-luna-v4/selector.py"
            selector_path = target / selector_relative
            v40_selector = (
                b"# simulated manifest-owned v4.0.0 payload\n"
                + selector_path.read_bytes()
            )
            selector_path.write_bytes(v40_selector)
            manifest["version"] = "v4.0.0"
            manifest["owned_files"][selector_relative] = hashlib.sha256(
                v40_selector
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            state = target / "sol-luna-v4" / "state"
            write_text(state / "daily-profile.json", '{"legacy":"daily"}\n')
            write_text(state / "last-good-profile.json", '{"legacy":"lkg"}\n')
            state_before = {
                path.name: path.read_bytes() for path in state.iterdir() if path.is_file()
            }
            agents_before = {
                filename: (target / "agents" / filename).read_bytes()
                for filename in STABLE_AGENT_FILES
            }
            config_before = (target / "config.toml").read_bytes()
            agents_policy_before = (target / "AGENTS.md").read_bytes()
            before = tree_hash(target)

            upgraded = call_install(target, generated_at=FIXED_TIME + timedelta(days=1))
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertTrue(Path(upgraded["backup"]).is_dir())
            self.assertEqual(
                selector_path.read_bytes(), (ROOT / "src/selector.py").read_bytes()
            )
            self.assertEqual(
                json.loads(manifest_path.read_text(encoding="utf-8"))["version"],
                VERSION,
            )
            self.assertEqual(
                {
                    filename: (target / "agents" / filename).read_bytes()
                    for filename in STABLE_AGENT_FILES
                },
                agents_before,
            )
            self.assertEqual((target / "config.toml").read_bytes(), config_before)
            self.assertEqual((target / "AGENTS.md").read_bytes(), agents_policy_before)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in state.iterdir()
                    if path.is_file()
                },
                state_before,
            )

            second = call_install(target, generated_at=FIXED_TIME + timedelta(days=2))
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)

            rolled_back = rollback(
                target,
                Path(upgraded["backup"]),
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)

    def test_rc4_to_stable_upgrade_changes_exactly_three_paths(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", 'user_setting = "preserve"\n')
            write_text(target / "AGENTS.md", "User policy remains.\n")
            call_install(target)
            simulate_rc4_managed_install(target)

            state = target / "sol-luna-v4" / "state"
            write_text(state / "daily-profile.json", '{"preserve":"daily"}\n')
            write_text(state / "last-good-profile.json", '{"preserve":"lkg"}\n')
            agents_before = {
                filename: (target / "agents" / filename).read_bytes()
                for filename in STABLE_AGENT_FILES
            }
            config_before = (target / "config.toml").read_bytes()
            state_before = {
                path.name: path.read_bytes() for path in state.iterdir() if path.is_file()
            }
            before = tree_hash(target)
            expected = {
                "AGENTS.md",
                "sol-luna-v4/selector.py",
                MANIFEST_RELATIVE.as_posix(),
            }

            dry = dry_run_install(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
                source_commit="b" * 40,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(dry["effective_changes"], 3)
            self.assertEqual(set(dry["modified"]), expected)
            self.assertEqual(tree_hash(target), before)

            upgraded = call_install(
                target,
                generated_at=FIXED_TIME + timedelta(days=1),
                source_commit="b" * 40,
            )
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 3)
            self.assertEqual(set(upgraded["modified"]), expected)
            backup = Path(upgraded["backup"])
            backup_entries = json.loads(
                (backup / "snapshot.json").read_text(encoding="utf-8")
            )["entries"]
            self.assertEqual({entry["path"] for entry in backup_entries}, expected)
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["version"], VERSION)
            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(manifest["source_commit"], "b" * 40)
            self.assertEqual(
                {
                    filename: (target / "agents" / filename).read_bytes()
                    for filename in STABLE_AGENT_FILES
                },
                agents_before,
            )
            self.assertEqual((target / "config.toml").read_bytes(), config_before)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in state.iterdir()
                    if path.is_file()
                },
                state_before,
            )

            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertIsNone(second["backup"])
            self.assertEqual(
                json.loads(
                    (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
                )["source_commit"],
                "b" * 40,
            )

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)

    def test_rc5_to_rc6_upgrade_is_idempotent_and_rolls_back_exactly(self):
        version_patch = patch("scripts.install.VERSION", "v4.1.0-rc6")
        version_patch.start()
        self.addCleanup(version_patch.stop)
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)

            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            selector_relative = "sol-luna-v4/selector.py"
            selector_path = target / selector_relative
            rc5_selector = (
                b"# simulated manifest-owned RC5 selector\n"
                + selector_path.read_bytes()
            )
            selector_path.write_bytes(rc5_selector)
            manifest["version"] = "v4.1.0-rc5"
            manifest["owned_files"][selector_relative] = hashlib.sha256(
                rc5_selector
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            rc5_before = tree_hash(target)

            dry = dry_run_install(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(dry["effective_changes"], 2)
            self.assertEqual(
                set(dry["modified"]),
                {MANIFEST_RELATIVE.as_posix(), selector_relative},
            )
            self.assertIsNone(dry["backup"])
            self.assertEqual(tree_hash(target), rc5_before)

            upgraded = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=1)
            )
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 2)
            self.assertEqual(
                set(upgraded["modified"]),
                {MANIFEST_RELATIVE.as_posix(), selector_relative},
            )
            backup = Path(upgraded["backup"])
            self.assertTrue(backup.is_dir())
            self.assertEqual(
                {
                    entry["path"]
                    for entry in json.loads(
                        (backup / "snapshot.json").read_text(encoding="utf-8")
                    )["entries"]
                },
                {MANIFEST_RELATIVE.as_posix(), selector_relative},
            )
            self.assertEqual(
                json.loads(manifest_path.read_text(encoding="utf-8"))["version"],
                "v4.1.0-rc6",
            )
            self.assertEqual(
                selector_path.read_bytes(), (ROOT / "src/selector.py").read_bytes()
            )
            upgraded_tree = tree_hash(target)

            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertIsNone(second["backup"])
            self.assertEqual(tree_hash(target), upgraded_tree)

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), rc5_before)
            self.assertEqual(
                json.loads(manifest_path.read_text(encoding="utf-8"))["version"],
                "v4.1.0-rc5",
            )

    def test_rc6_to_stable_upgrade_changes_only_manifest(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            with patch("scripts.install.VERSION", "v4.1.0-rc6"):
                call_install(target)

            manifest_path = target / MANIFEST_RELATIVE
            rc6_manifest_before = manifest_path.read_bytes()
            before = tree_hash(target)

            dry = dry_run_install(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(dry["effective_changes"], 1)
            self.assertEqual(dry["created"], [])
            self.assertEqual(dry["modified"], [MANIFEST_RELATIVE.as_posix()])
            self.assertEqual(dry["removed"], [])
            self.assertIsNone(dry["backup"])
            self.assertEqual(tree_hash(target), before)

            upgraded = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=1)
            )
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 1)
            self.assertEqual(upgraded["created"], [])
            self.assertEqual(upgraded["modified"], [MANIFEST_RELATIVE.as_posix()])
            self.assertEqual(upgraded["removed"], [])
            backup = Path(upgraded["backup"])
            self.assertTrue(backup.is_dir())
            self.assertEqual(
                {
                    entry["path"]
                    for entry in json.loads(
                        (backup / "snapshot.json").read_text(encoding="utf-8")
                    )["entries"]
                },
                {MANIFEST_RELATIVE.as_posix()},
            )
            self.assertEqual(
                json.loads(manifest_path.read_text(encoding="utf-8"))["version"],
                VERSION,
            )

            upgraded_tree = tree_hash(target)
            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertIsNone(second["backup"])
            self.assertEqual(tree_hash(target), upgraded_tree)

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)
            self.assertEqual(manifest_path.read_bytes(), rc6_manifest_before)

    def test_published_v420_rc1_to_stable_preserves_state_and_rolls_back(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", 'user_model = "keep"\n')
            write_text(target / "AGENTS.md", "User policy remains.\n")
            user_file = target / "user" / "content.txt"
            write_text(user_file, "user content stays\n")
            user_skill = target.parent / ".agents" / "skills" / "user-skill" / "SKILL.md"
            write_text(user_skill, "user skill stays\n")
            simulate_published_v420_rc1_install(target)

            state = target / "sol-luna-v4" / "state"
            daily = state / "daily-profile.json"
            last_good = state / "last-good-profile.json"
            write_text(daily, '{"role":"sol_max","date":"2026-08-12"}\n')
            write_text(last_good, '{"role":"sol_max"}\n')
            protected_paths = (
                target / "config.toml",
                target / "AGENTS.md",
                user_file,
                user_skill,
                daily,
                last_good,
            )
            protected_before = {
                path: path.read_bytes() for path in protected_paths
            }

            manifest_path = target / MANIFEST_RELATIVE
            selector_relative = "sol-luna-v4/selector.py"
            selector_path = target / selector_relative
            upgrade_relative = "sol-luna-upgrade/SKILL.md"
            upgrade_path = user_skill.parents[1] / upgrade_relative
            rc1_manifest = manifest_path.read_bytes()
            rc1_selector = selector_path.read_bytes()
            rc1_upgrade_skill = upgrade_path.read_bytes()
            before = installation_hash(target)
            expected_modified = {
                MANIFEST_RELATIVE.as_posix(),
                selector_relative,
                f"skills:{upgrade_relative}",
            }
            stable_source_commit = "4" * 40

            dry = dry_run_install(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
                source_commit=stable_source_commit,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(dry["effective_changes"], 3)
            self.assertEqual(dry["created"], [])
            self.assertEqual(set(dry["modified"]), expected_modified)
            self.assertEqual(dry["removed"], [])
            self.assertIsNone(dry["backup"])
            self.assertEqual(installation_hash(target), before)

            upgraded = call_install(
                target,
                generated_at=FIXED_TIME + timedelta(days=1),
                source_commit=stable_source_commit,
            )
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 3)
            self.assertEqual(upgraded["created"], [])
            self.assertEqual(set(upgraded["modified"]), expected_modified)
            self.assertEqual(upgraded["removed"], [])
            for path, payload in protected_before.items():
                self.assertEqual(path.read_bytes(), payload)

            backup = Path(upgraded["backup"])
            snapshot = json.loads(
                (backup / "snapshot.json").read_text(encoding="utf-8")
            )
            snapshot_entries = {
                (entry["root"], entry["path"]): entry
                for entry in snapshot["entries"]
            }
            expected_snapshot_hashes = {
                ("codex_home", MANIFEST_RELATIVE.as_posix()): hashlib.sha256(
                    rc1_manifest
                ).hexdigest(),
                ("codex_home", selector_relative): hashlib.sha256(
                    rc1_selector
                ).hexdigest(),
                ("skills_root", upgrade_relative): hashlib.sha256(
                    rc1_upgrade_skill
                ).hexdigest(),
            }
            self.assertEqual(set(snapshot_entries), set(expected_snapshot_hashes))
            for key, expected_hash in expected_snapshot_hashes.items():
                self.assertTrue(snapshot_entries[key]["existed"])
                self.assertEqual(snapshot_entries[key]["sha256"], expected_hash)

            installed = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(installed["version"], VERSION)
            self.assertEqual(installed["source_commit"], stable_source_commit)
            for relative, digest in installed["owned_files"].items():
                self.assertEqual(
                    hashlib.sha256((target / relative).read_bytes()).hexdigest(),
                    digest,
                )
            skills_root = Path(installed["skills_root"])
            for relative, digest in installed["owned_skill_files"].items():
                self.assertEqual(
                    hashlib.sha256(
                        skills_root.joinpath(*Path(relative).parts).read_bytes()
                    ).hexdigest(),
                    digest,
                )
            self.assertIn(USER_AGENT.encode("ascii"), selector_path.read_bytes())
            self.assertIn(STABLE_V420_RELEASES_PATH, upgrade_path.read_bytes())

            upgraded_tree = installation_hash(target)
            second = call_install(
                target,
                generated_at=FIXED_TIME + timedelta(days=2),
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertIsNone(second["backup"])
            self.assertEqual(installation_hash(target), upgraded_tree)

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(manifest_path.read_bytes(), rc1_manifest)
            self.assertEqual(selector_path.read_bytes(), rc1_selector)
            self.assertEqual(upgrade_path.read_bytes(), rc1_upgrade_skill)
            for path, payload in protected_before.items():
                self.assertEqual(path.read_bytes(), payload)

    def test_published_v420_rc1_modified_payload_blocks_stable_upgrade(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            simulate_published_v420_rc1_install(target)
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            upgrade_skill = (
                Path(manifest["skills_root"])
                / "sol-luna-upgrade"
                / "SKILL.md"
            )
            upgrade_skill.write_bytes(upgrade_skill.read_bytes() + b"\n# user change\n")
            before = installation_hash(target)

            for action in ("dry-run", "apply"):
                with self.subTest(action=action):
                    with self.assertRaises(InstallerError) as raised:
                        if action == "dry-run":
                            dry_run_install(
                                target,
                                project_root=ROOT,
                                generated_at=FIXED_TIME + timedelta(days=1),
                                allow_validation_sandbox=True,
                            )
                        else:
                            call_install(
                                target,
                                generated_at=FIXED_TIME + timedelta(days=1),
                            )
                    self.assertEqual(
                        raised.exception.reason_code,
                        "OWNERSHIP_CONFLICT",
                    )
                    self.assertEqual(installation_hash(target), before)

    def test_v414_to_v420_stable_adds_workers_skills_module_and_policy(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            simulate_v414_managed_install(target)

            manifest_path = target / MANIFEST_RELATIVE
            selector_relative = "sol-luna-v4/selector.py"
            selector_path = target / selector_relative
            v414_selector = selector_path.read_bytes()
            v414_manifest_before = manifest_path.read_bytes()
            before = installation_hash(target)
            skill_paths = {
                "skills:sol-luna-status/SKILL.md",
                "skills:sol-luna-upgrade/SKILL.md",
                "skills:sol-luna-delegate/SKILL.md",
            }
            modified_paths = {
                "AGENTS.md",
                "config.toml",
                MANIFEST_RELATIVE.as_posix(),
                selector_relative,
            } | {f"agents/{filename}" for filename in STABLE_AGENT_FILES}
            created_paths = skill_paths | {
                "sol-luna-v4/worker_selector.py",
                *(f"agents/{filename}" for filename in SOL_AGENT_FILES),
            }

            dry = dry_run_install(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
                source_commit="2" * 40,
            )
            self.assertEqual(dry["status"], "DRY_RUN_PASS")
            self.assertEqual(dry["effective_changes"], 18)
            self.assertEqual(set(dry["created"]), created_paths)
            self.assertEqual(set(dry["modified"]), modified_paths)
            self.assertEqual(dry["removed"], [])
            self.assertIsNone(dry["backup"])
            self.assertEqual(installation_hash(target), before)

            upgraded = call_install(
                target,
                generated_at=FIXED_TIME + timedelta(days=1),
                source_commit="2" * 40,
            )
            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 18)
            self.assertEqual(set(upgraded["created"]), created_paths)
            self.assertEqual(set(upgraded["modified"]), modified_paths)
            self.assertEqual(upgraded["removed"], [])
            backup = Path(upgraded["backup"])
            expected_entries = {
                ("codex_home", path)
                for path in (
                    modified_paths
                    | {
                        path
                        for path in created_paths
                        if not path.startswith("skills:")
                    }
                )
            } | {
                ("skills_root", path.removeprefix("skills:"))
                for path in skill_paths
            }
            self.assertEqual(
                {
                    (entry["root"], entry["path"])
                    for entry in json.loads(
                        (backup / "snapshot.json").read_text(encoding="utf-8")
                    )["entries"]
                },
                expected_entries,
            )
            installed = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(installed["version"], VERSION)
            self.assertEqual(installed["schema_version"], 3)
            self.assertEqual(installed["source_commit"], "2" * 40)
            self.assertNotEqual(selector_path.read_bytes(), v414_selector)
            self.assertIn(
                USER_AGENT.encode("ascii"),
                selector_path.read_bytes(),
            )

            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)
            self.assertIsNone(second["backup"])

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(manifest_path.read_bytes(), v414_manifest_before)
            self.assertEqual(selector_path.read_bytes(), v414_selector)

    def test_v414_modified_selector_blocks_v420_upgrade_without_changes(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            simulate_v414_managed_install(target)

            selector_path = target / "sol-luna-v4" / "selector.py"
            selector_path.write_bytes(selector_path.read_bytes() + b"\n# user change\n")
            before = installation_hash(target)
            for action in ("dry-run", "apply"):
                with self.subTest(action=action):
                    with self.assertRaises(InstallerError) as raised:
                        if action == "dry-run":
                            dry_run_install(
                                target,
                                project_root=ROOT,
                                generated_at=FIXED_TIME + timedelta(days=1),
                                allow_validation_sandbox=True,
                            )
                        else:
                            call_install(
                                target,
                                generated_at=FIXED_TIME + timedelta(days=1),
                            )
                    self.assertEqual(
                        raised.exception.reason_code,
                        "OWNERSHIP_CONFLICT",
                    )
                    self.assertEqual(installation_hash(target), before)

    def test_rc6_modified_owned_file_blocks_stable_upgrade_without_changes(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            with patch("scripts.install.VERSION", "v4.1.0-rc6"):
                call_install(target)

            selector_path = target / "sol-luna-v4" / "selector.py"
            selector_path.write_bytes(selector_path.read_bytes() + b"\n# user change\n")
            before = tree_hash(target)

            with self.assertRaises(InstallerError) as raised:
                dry_run_install(
                    target,
                    project_root=ROOT,
                    generated_at=FIXED_TIME + timedelta(days=1),
                    allow_validation_sandbox=True,
                )
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

            with self.assertRaises(InstallerError) as raised:
                call_install(target, generated_at=FIXED_TIME + timedelta(days=1))
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_rc5_modified_owned_file_blocks_rc6_upgrade_without_changes(self):
        version_patch = patch("scripts.install.VERSION", "v4.1.0-rc6")
        version_patch.start()
        self.addCleanup(version_patch.stop)
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)

            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "v4.1.0-rc5"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            selector_path = target / "sol-luna-v4" / "selector.py"
            selector_path.write_bytes(selector_path.read_bytes() + b"\n# user change\n")
            before = tree_hash(target)

            with self.assertRaises(InstallerError) as raised:
                call_install(
                    target, generated_at=FIXED_TIME + timedelta(days=1)
                )

            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_rc4_modified_owned_content_blocks_upgrade(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            simulate_rc4_managed_install(target)
            policy = target / "AGENTS.md"
            policy.write_text(
                policy.read_text(encoding="utf-8").replace(
                    "Legacy RC4 receipt:", "User changed the Legacy RC4 receipt:"
                ),
                encoding="utf-8",
            )
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target, generated_at=FIXED_TIME + timedelta(days=1))
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_rc1_global_policy_upgrades_to_stable_receipt_and_rolls_back(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", 'user_setting = "preserve"\n')
            write_text(target / "AGENTS.md", "User policy remains.\n")
            call_install(target)
            simulate_rc1_managed_policy(target)

            state = target / "sol-luna-v4" / "state"
            write_text(state / "daily-profile.json", '{"preserve":"daily"}\n')
            write_text(state / "last-good-profile.json", '{"preserve":"lkg"}\n')
            state_before = {
                path.name: path.read_bytes() for path in state.iterdir() if path.is_file()
            }
            selector_before = (target / "sol-luna-v4" / "selector.py").read_bytes()
            agents_before = {
                filename: (target / "agents" / filename).read_bytes()
                for filename in STABLE_AGENT_FILES
            }
            config_before = (target / "config.toml").read_bytes()
            rc1_agents_before = (target / "AGENTS.md").read_bytes()
            rc1_manifest_before = (target / MANIFEST_RELATIVE).read_bytes()
            before = tree_hash(target)

            upgraded = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=1)
            )

            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 2)
            self.assertEqual(
                set(upgraded["modified"]),
                {"AGENTS.md", MANIFEST_RELATIVE.as_posix()},
            )
            backup = Path(upgraded["backup"])
            self.assertTrue(backup.is_dir())
            snapshot = json.loads(
                (backup / "snapshot.json").read_text(encoding="utf-8")
            )
            backed = {entry["path"] for entry in snapshot["entries"]}
            self.assertIn("AGENTS.md", backed)
            self.assertIn(MANIFEST_RELATIVE.as_posix(), backed)

            upgraded_policy = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertTrue(upgraded_policy.startswith("User policy remains.\n"))
            self.assertIn("## Receipts", upgraded_policy)
            self.assertEqual(
                json.loads(
                    (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
                )["version"],
                VERSION,
            )
            self.assertEqual(
                (target / "sol-luna-v4" / "selector.py").read_bytes(),
                selector_before,
            )
            self.assertEqual(
                {
                    filename: (target / "agents" / filename).read_bytes()
                    for filename in STABLE_AGENT_FILES
                },
                agents_before,
            )
            self.assertEqual((target / "config.toml").read_bytes(), config_before)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in state.iterdir()
                    if path.is_file()
                },
                state_before,
            )

            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)
            self.assertEqual((target / "AGENTS.md").read_bytes(), rc1_agents_before)
            self.assertEqual(
                (target / MANIFEST_RELATIVE).read_bytes(), rc1_manifest_before
            )

    def test_rc1_modified_owned_policy_blocks_stable_upgrade(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            simulate_rc1_managed_policy(target)
            agents_path = target / "AGENTS.md"
            policy_before, policy_after = mutate_owned_policy(agents_path)
            self.assertNotEqual(policy_after, policy_before)
            before = tree_hash(target)

            with self.assertRaises(InstallerError) as raised:
                call_install(target, generated_at=FIXED_TIME + timedelta(days=1))

            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_rc3_global_policy_upgrades_to_stable_evidence_gate_and_rolls_back(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", 'user_setting = "preserve"\n')
            write_text(target / "AGENTS.md", "User policy remains.\n")
            call_install(target)
            simulate_rc3_managed_policy(target)

            state = target / "sol-luna-v4" / "state"
            write_text(state / "daily-profile.json", '{"preserve":"daily"}\n')
            write_text(state / "last-good-profile.json", '{"preserve":"lkg"}\n')
            selector_before = (target / "sol-luna-v4" / "selector.py").read_bytes()
            agents_before = {
                filename: (target / "agents" / filename).read_bytes()
                for filename in STABLE_AGENT_FILES
            }
            config_before = (target / "config.toml").read_bytes()
            state_before = {
                path.name: path.read_bytes() for path in state.iterdir() if path.is_file()
            }
            rc3_policy_before = (target / "AGENTS.md").read_bytes()
            rc3_manifest_before = (target / MANIFEST_RELATIVE).read_bytes()
            before = tree_hash(target)

            upgraded = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=1)
            )

            self.assertEqual(upgraded["status"], "UPGRADED")
            self.assertEqual(upgraded["effective_changes"], 2)
            self.assertEqual(
                set(upgraded["modified"]),
                {"AGENTS.md", MANIFEST_RELATIVE.as_posix()},
            )
            backup = Path(upgraded["backup"])
            self.assertTrue(backup.is_dir())
            snapshot = json.loads(
                (backup / "snapshot.json").read_text(encoding="utf-8")
            )
            backed = {entry["path"] for entry in snapshot["entries"]}
            self.assertIn("AGENTS.md", backed)
            self.assertIn(MANIFEST_RELATIVE.as_posix(), backed)

            upgraded_policy = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(
                "only after current-task selection/agent/spawn failure",
                upgraded_policy,
            )
            self.assertIn("No derived savings", upgraded_policy)
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["schema_version"], 3)
            self.assertEqual(manifest["version"], VERSION)
            self.assertEqual(
                (target / "sol-luna-v4" / "selector.py").read_bytes(),
                selector_before,
            )
            self.assertEqual(
                {
                    filename: (target / "agents" / filename).read_bytes()
                    for filename in STABLE_AGENT_FILES
                },
                agents_before,
            )
            self.assertEqual((target / "config.toml").read_bytes(), config_before)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in state.iterdir()
                    if path.is_file()
                },
                state_before,
            )

            second = call_install(
                target, generated_at=FIXED_TIME + timedelta(days=2)
            )
            self.assertEqual(second["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second["effective_changes"], 0)

            rolled_back = rollback(
                target,
                backup,
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(rolled_back["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(tree_hash(target), before)
            self.assertEqual((target / "AGENTS.md").read_bytes(), rc3_policy_before)
            self.assertEqual(
                (target / MANIFEST_RELATIVE).read_bytes(), rc3_manifest_before
            )

    def test_rc3_modified_owned_policy_blocks_stable_upgrade(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            simulate_rc3_managed_policy(target)
            agents_path = target / "AGENTS.md"
            policy_before, policy_after = mutate_owned_policy(agents_path)
            self.assertNotEqual(policy_after, policy_before)
            before = tree_hash(target)

            with self.assertRaises(InstallerError) as raised:
                call_install(target, generated_at=FIXED_TIME + timedelta(days=1))

            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_sanitized_legacy_migration_removes_only_manifest_owned_content(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            fixture = materialize_legacy_fixture(target)
            before = tree_hash(target)
            result = call_install(target, migrate_legacy=True)

            self.assertEqual(result["migration"]["source_version"], fixture["version"])
            for relative in fixture["created_files"]:
                relative = relative.replace("<installation>", "fixture")
                if relative == "hooks.json":
                    continue
                self.assertFalse((target / relative).exists(), relative)
            self.assertTrue((target / "agents" / "user-agent.toml").is_file())
            self.assertTrue((target / "hooks" / "user_hook.py").is_file())
            self.assertTrue((target / "sol-luna-router" / "user-note.txt").is_file())
            hooks = json.loads((target / "hooks.json").read_text(encoding="utf-8"))
            self.assertEqual(len(hooks["hooks"]["PreToolUse"]), 1)
            self.assertNotIn("SubagentStart", hooks["hooks"])
            self.assertIn(
                "User instruction stays.",
                (target / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertNotIn(
                "SOL_LUNA_DAILY_BEST",
                (target / "AGENTS.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                tomllib.loads(
                    (target / "config.toml").read_text(encoding="utf-8")
                )["user_model"],
                "preserve",
            )
            self.assertFalse((target / "sol-luna-v4" / "state").exists())

            rollback(
                target,
                Path(result["backup"]),
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(tree_hash(target), before)

    def test_empty_legacy_created_hooks_file_is_removed(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            materialize_legacy_fixture(target)
            old_group = {
                "hooks": [
                    {
                        "type": "command",
                        "command": "python hooks/sol_luna_router.py",
                    }
                ]
            }
            write_text(
                target / "hooks.json",
                json.dumps(
                    {
                        "description": "Sol Luna managed hooks",
                        "hooks": {
                            "PreToolUse": [old_group],
                            "SubagentStart": [old_group],
                            "SubagentStop": [old_group],
                            "SessionStart": [old_group],
                        },
                    },
                    indent=2,
                )
                + "\n",
            )
            call_install(target, migrate_legacy=True)
            self.assertFalse((target / "hooks.json").exists())

    def test_audit_bundles_are_untouched_and_backup_covers_commit_markers(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            materialize_legacy_fixture(target)
            audit = target / "sol-luna-router" / "audit-bundles" / "evidence.json"
            write_text(audit, '{"preserve": true}\n')
            audit_before = audit.read_bytes()

            result = call_install(target, migrate_legacy=True)

            self.assertEqual(audit.read_bytes(), audit_before)
            snapshot = json.loads(
                (Path(result["backup"]) / "snapshot.json").read_text(encoding="utf-8")
            )
            backed = {entry["path"] for entry in snapshot["entries"]}
            self.assertIn(MANIFEST_RELATIVE.as_posix(), backed)
            self.assertIn("sol-luna-router/install-manifest.json", backed)
            self.assertIn("agents/luna-low.toml", backed)
            self.assertIn("AGENTS.md", backed)
            self.assertIn("config.toml", backed)
            self.assertNotIn("sol-luna-router/audit-bundles/evidence.json", backed)

    def test_precommit_failpoints_restore_exact_tree(self):
        points = (
            "after_agent_install",
            "after_skill_install",
            "after_config_merge",
            "after_hook_removal",
            "after_old_file_deletion",
            "before_v4_manifest_write",
        )
        for point in points:
            with self.subTest(point=point), sandbox() as directory:
                target = Path(directory) / ".codex"
                materialize_legacy_fixture(target)
                write_text(
                    target / "sol-luna-router" / "audit-bundles" / "evidence.txt",
                    "preserve\n",
                )
                before = installation_hash(target)

                def failpoint(name, expected=point):
                    if name == expected:
                        self.assertFalse((target / MANIFEST_RELATIVE).exists())
                        raise OSError(f"fixture failure at {name}")

                with self.assertRaises(InstallerError) as raised:
                    call_install(target, migrate_legacy=True, failpoint=failpoint)
                self.assertEqual(raised.exception.reason_code, "APPLY_FAILED")
                self.assertEqual(installation_hash(target), before)

    def test_manifest_is_last_then_legacy_cleanup_is_postcommit(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            materialize_legacy_fixture(target)
            observed = []

            def observe(name):
                observed.append(name)
                if name != "legacy_manifest_cleanup":
                    self.assertFalse((target / MANIFEST_RELATIVE).exists())
                else:
                    self.assertTrue((target / MANIFEST_RELATIVE).is_file())
                    self.assertTrue(
                        (target / "sol-luna-router" / "install-manifest.json").is_file()
                    )

            result = call_install(target, migrate_legacy=True, failpoint=observe)
            self.assertEqual(result["status"], "INSTALLED")
            self.assertEqual(
                observed,
                [
                    "after_agent_install",
                    "after_skill_install",
                    "after_config_merge",
                    "after_hook_removal",
                    "after_old_file_deletion",
                    "before_v4_manifest_write",
                    "legacy_manifest_cleanup",
                ],
            )
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["legacy_cleanup"]["status"], "complete")

    def test_postcommit_legacy_manifest_cleanup_failure_is_retryable(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            materialize_legacy_fixture(target)

            def fail_cleanup(name):
                if name == "legacy_manifest_cleanup":
                    raise OSError("fixture cleanup failure")

            result = call_install(
                target, migrate_legacy=True, failpoint=fail_cleanup
            )
            self.assertEqual(result["status"], "LEGACY_MANIFEST_CLEANUP_PENDING")
            self.assertTrue((target / MANIFEST_RELATIVE).is_file())
            self.assertTrue(
                (target / "sol-luna-router" / "install-manifest.json").is_file()
            )
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["legacy_cleanup"]["status"], "pending")
            self.assertTrue((target / "agents" / "luna-low.toml").is_file())

            retried = call_install(
                target,
                migrate_legacy=True,
                generated_at=FIXED_TIME + timedelta(days=1),
            )
            self.assertEqual(retried["status"], "LEGACY_CLEANUP_COMPLETED")
            self.assertFalse(
                (target / "sol-luna-router" / "install-manifest.json").exists()
            )
            manifest = json.loads(
                (target / MANIFEST_RELATIVE).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["legacy_cleanup"]["status"], "complete")

    def test_foreign_luna_agent_is_ownership_conflict(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "agents" / "luna-low.toml", "user-owned\n")
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(tree_hash(target), before)

    def test_new_agent_module_and_third_skill_collisions_do_not_write(self):
        for collision in ("sol-agent", "worker-module", "delegate-skill"):
            with self.subTest(collision=collision), sandbox() as directory:
                target = Path(directory) / ".codex"
                skills_root = target.parent / ".agents" / "skills"
                if collision == "sol-agent":
                    write_text(target / "agents" / "sol-low.toml", "user agent\n")
                elif collision == "worker-module":
                    write_text(
                        target / "sol-luna-v4" / "worker_selector.py",
                        "user module\n",
                    )
                else:
                    write_text(
                        skills_root / "sol-luna-delegate" / "SKILL.md",
                        "user skill\n",
                    )
                before = installation_hash(target)
                for action in (dry_run_install, install):
                    with self.subTest(action=action.__name__):
                        with self.assertRaises(InstallerError) as raised:
                            action(
                                target,
                                project_root=ROOT,
                                allow_validation_sandbox=True,
                            )
                        self.assertEqual(
                            raised.exception.reason_code, "OWNERSHIP_CONFLICT"
                        )
                        self.assertEqual(installation_hash(target), before)
                        self.assertFalse((target / "backups").exists())

    def test_corrupt_agents_marker_fails_closed(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "AGENTS.md", f"user\n{AGENTS_BEGIN}\nbroken\n")
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "AGENTS_MARKER_CORRUPT")
            self.assertEqual(tree_hash(target), before)

    def test_invalid_config_fails_closed(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "config.toml", "[broken\n")
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "CONFIG_MERGE_UNSAFE")
            self.assertEqual(tree_hash(target), before)

    def test_unsupported_manifest_schema_fails_closed_without_changes(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            manifest_path = target / MANIFEST_RELATIVE
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = 99
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            before = installation_hash(target)

            actions = (
                lambda: dry_run_install(
                    target,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
                lambda: call_install(target),
                lambda: uninstall(
                    target,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
            )
            for action in actions:
                with self.subTest(action=action):
                    with self.assertRaises(InstallerError) as raised:
                        action()
                    self.assertEqual(raised.exception.reason_code, "MANIFEST_INVALID")
                    self.assertEqual(installation_hash(target), before)

    def test_missing_manifest_blocks_uninstall(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            with self.assertRaises(InstallerError) as raised:
                uninstall(target, project_root=ROOT, allow_validation_sandbox=True)
            self.assertEqual(raised.exception.reason_code, "MANIFEST_MISSING")

    def test_backup_failure_is_reported_without_partial_install(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            write_text(target / "backups", "user file blocks backup root\n")
            before = tree_hash(target)
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "BACKUP_FAILED")
            self.assertEqual(tree_hash(target), before)

    def test_non_directory_target_is_not_writable(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target, "not a directory\n")
            with self.assertRaises(InstallerError) as raised:
                call_install(target)
            self.assertEqual(raised.exception.reason_code, "TARGET_NOT_WRITABLE")

    def test_rollback_restores_exact_preinstall_tree(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            write_text(target / "user" / "state.txt", "preserve exactly\n")
            user_skill = target.parent / ".agents" / "skills" / "user-skill" / "SKILL.md"
            write_text(user_skill, "user skill stays\n")
            before = installation_hash(target)
            installed = call_install(target)
            restored = rollback(
                target,
                Path(installed["backup"]),
                project_root=ROOT,
                allow_validation_sandbox=True,
            )
            self.assertEqual(restored["status"], "ROLLBACK_EXACT_PASS")
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(user_skill.read_text(encoding="utf-8"), "user skill stays\n")

    def test_uninstall_removes_owned_content_and_preserves_user_content(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            original_config = 'user_model = "keep"\n'
            original_agents = "User policy remains.\n"
            write_text(target / "config.toml", original_config)
            write_text(target / "AGENTS.md", original_agents)
            write_text(target / "agents" / "user-agent.toml", 'name = "user_agent"\n')
            write_text(target / "runtime" / "user-state.json", "{}\n")
            user_skill = target.parent / ".agents" / "skills" / "user-skill" / "SKILL.md"
            write_text(user_skill, "user skill stays\n")
            call_install(target)

            result = uninstall(
                target,
                project_root=ROOT,
                generated_at=FIXED_TIME + timedelta(days=1),
                allow_validation_sandbox=True,
            )
            self.assertEqual(result["status"], "UNINSTALLED")
            for filename in AGENT_FILES:
                self.assertFalse((target / "agents" / filename).exists())
            self.assertFalse((target / "sol-luna-v4" / "selector.py").exists())
            self.assertFalse((target / "sol-luna-v4" / "worker_selector.py").exists())
            self.assertFalse((target / MANIFEST_RELATIVE).exists())
            self.assertEqual(
                (target / "config.toml").read_text(encoding="utf-8"), original_config
            )
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"), original_agents
            )
            self.assertTrue((target / "agents" / "user-agent.toml").is_file())
            self.assertTrue((target / "runtime" / "user-state.json").is_file())
            self.assertEqual(user_skill.read_text(encoding="utf-8"), "user skill stays\n")
            self.assertFalse(
                (user_skill.parents[1] / "sol-luna-status" / "SKILL.md").exists()
            )
            self.assertFalse(
                (user_skill.parents[1] / "sol-luna-upgrade" / "SKILL.md").exists()
            )
            self.assertFalse(
                (user_skill.parents[1] / "sol-luna-delegate" / "SKILL.md").exists()
            )

    def test_modified_managed_skill_blocks_upgrade_and_uninstall(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            skill = (
                target.parent
                / ".agents"
                / "skills"
                / "sol-luna-status"
                / "SKILL.md"
            )
            skill.write_bytes(skill.read_bytes() + b"\nuser change\n")
            before = installation_hash(target)

            actions = (
                lambda: dry_run_install(
                    target,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
                lambda: call_install(target),
                lambda: uninstall(
                    target,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
            )
            for action in actions:
                with self.subTest(action=action):
                    with self.assertRaises(InstallerError) as raised:
                        action()
                    self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
                    self.assertEqual(installation_hash(target), before)

    def test_recorded_skill_root_mismatch_fails_closed(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            wrong_root = target.parent / ".agents-other" / "skills"
            before = installation_hash(target)

            actions = (
                lambda: dry_run_install(
                    target,
                    skills_root=wrong_root,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
                lambda: uninstall(
                    target,
                    skills_root=wrong_root,
                    project_root=ROOT,
                    allow_validation_sandbox=True,
                ),
            )
            for action in actions:
                with self.subTest(action=action):
                    with self.assertRaises(InstallerError) as raised:
                        action()
                    self.assertEqual(raised.exception.reason_code, "SKILLS_ROOT_MISMATCH")
                    self.assertEqual(installation_hash(target), before)

    def test_uninstall_preserves_modified_owned_file_by_failing_closed(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            write_text(target / "agents" / "luna-low.toml", "user changed owned file\n")
            with self.assertRaises(InstallerError) as raised:
                uninstall(target, project_root=ROOT, allow_validation_sandbox=True)
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertTrue((target / "agents" / "luna-low.toml").is_file())

    def test_uninstall_backup_verification_failure_preserves_exact_tree(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            before = installation_hash(target)

            with patch(
                "scripts.install._verify_backup",
                side_effect=InstallerError("BACKUP_FAILED", "forced verification failure"),
            ):
                with self.assertRaises(InstallerError) as raised:
                    uninstall(target, project_root=ROOT, allow_validation_sandbox=True)

            self.assertEqual(raised.exception.reason_code, "BACKUP_FAILED")
            self.assertEqual(installation_hash(target), before)

    def test_uninstall_installer_error_after_partial_apply_rolls_back_exact_tree(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            target.mkdir()
            call_install(target)
            before = installation_hash(target)
            original_apply_operations = installer_module._apply_operations
            failed = False

            def fail_after_first_operation(target, operations):
                nonlocal failed
                first = sorted(operations)[0]
                original_apply_operations(target, {first: operations[first]})
                failed = True
                raise InstallerError("OWNERSHIP_CONFLICT", "forced uninstall failure")

            with patch(
                "scripts.install._apply_operations",
                side_effect=fail_after_first_operation,
            ):
                with self.assertRaises(InstallerError) as raised:
                    uninstall(target, project_root=ROOT, allow_validation_sandbox=True)

            self.assertTrue(failed)
            self.assertEqual(raised.exception.reason_code, "OWNERSHIP_CONFLICT")
            self.assertEqual(installation_hash(target), before)

    def test_cli_apply_and_second_run_use_validation_sandbox_only(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            skills_root = target.parent / ".agents" / "skills"
            command = [
                sys.executable,
                str(ROOT / "scripts" / "install.py"),
                "--apply",
                "--codex-home",
                str(target),
                "--skills-root",
                str(skills_root),
                "--validation-sandbox",
            ]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["status"], "INSTALLED")
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            second_result = json.loads(second.stdout)
            self.assertEqual(second_result["status"], "IDEMPOTENT_PASS")
            self.assertEqual(second_result["effective_changes"], 0)

    def test_cli_migrates_fake_legacy_32_without_creating_state(self):
        with sandbox() as directory:
            target = Path(directory) / ".codex"
            skills_root = target.parent / ".agents" / "skills"
            materialize_legacy_fixture(target)
            command = [
                sys.executable,
                str(ROOT / "scripts" / "install.py"),
                "--apply",
                "--migrate-v3",
                "--codex-home",
                str(target),
                "--skills-root",
                str(skills_root),
                "--validation-sandbox",
            ]
            completed = subprocess.run(
                command, cwd=ROOT, capture_output=True, text=True
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "INSTALLED")
            self.assertEqual(result["migration"]["source_version"], "3.2")
            self.assertEqual(result["migration"]["cleanup_status"], "complete")
            self.assertFalse((target / "sol-luna-v4" / "state").exists())


if __name__ == "__main__":
    unittest.main()

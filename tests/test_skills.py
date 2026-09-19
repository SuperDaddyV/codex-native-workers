import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "payload" / "skills"
SKILL_PATHS = {
    name: SKILLS_ROOT / name / "SKILL.md"
    for name in ("sol-luna-delegate", "sol-luna-status", "sol-luna-upgrade")
}


def read_frontmatter(path):
    content = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        raise AssertionError(f"missing valid frontmatter: {path}")

    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('"\'')
    return content, values


class SkillPayloadTests(unittest.TestCase):
    def test_only_three_named_skills_have_valid_frontmatter(self):
        self.assertEqual(
            {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()},
            set(SKILL_PATHS),
        )
        for name, path in SKILL_PATHS.items():
            with self.subTest(name=name):
                content, frontmatter = read_frontmatter(path)
                self.assertEqual(frontmatter.get("name"), name)
                description = frontmatter.get("description", "")
                self.assertTrue(description)
                self.assertLessEqual(len(description), 240)
                self.assertGreater(len(content), len(description))
                self.assertIsNone(re.search(r"\b(?:TODO|FIXME|TBD)\b", content))
                self.assertIsNone(re.search(r"\[\s*placeholder\s*\]", content, re.I))

    def test_delegate_uses_one_profile_snapshot_and_only_native_roles(self):
        content, _ = read_frontmatter(SKILL_PATHS["sol-luna-delegate"])
        self.assertEqual(content.count("<SELECTOR_COMMAND>"), 1)
        for invariant in (
            "exactly once for the whole delegation workflow",
            "--ensure-daily --print-selection --workers",
            "worker_profile_schema_version",
            "selection_date_bjt",
            '"luna"',
            '"sol"',
            "allowed_roles",
            "selected_role",
            "native custom agent `agent_type`",
            "task-specific risk or evidence need",
            "general",
            "backend",
            "frontend",
            "reasoning",
            "Do not automatically switch worker family",
            "write sets do not overlap",
            "current runtime supports",
            "After planning",
            "Profiles set `[agents] enabled = false`",
            "must not spawn or delegate",
            "host-enforced tool/invocation isolation",
            "strict recursive isolation scenarios remain unsupported",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, content)
        self.assertNotIn("<STATUS_COMMAND>", content)

    def test_status_supports_schemas_two_three_four_and_legacy_without_mutation(self):
        content, _ = read_frontmatter(SKILL_PATHS["sol-luna-status"])
        self.assertEqual(content.count("<STATUS_COMMAND>"), 1)
        for invariant in (
            "exactly once",
            "read-only",
            "diagnostic_schema_version` 2, 3, or 4",
            "workers.sol",
            "workers.luna",
            "leaf_config",
            "native_delegation",
            "native_tool_isolation",
            "native_delegation_guard",
            "runtime_max_parallel",
            "configured thread limit and runtime capacity separately",
            "diagnostic paths",
            "TODAY_SELECTION_NOT_INITIALIZED",
            "Preserve any returned `Misconfigured`, `Unavailable`, or `Degraded` health",
            "Unknown",
            "`Not checked`",
            "`PASS`",
            "Legacy `native_leaf` `Ready` is configuration-only",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, content)
        for restriction in (
            "fetch",
            "select",
            "write state",
            "take a selector lock",
            "spawn or probe an agent",
        ):
            with self.subTest(restriction=restriction):
                self.assertIn(restriction, content)
        schema4 = content.split("- Schema 4:", 1)[1].split("- Schema 3:", 1)[0]
        self.assertNotIn("native_leaf", schema4)
        self.assertNotIn("native_runtime", schema4)
        self.assertIn("Schema 4 omits the legacy leaf/runtime keys", schema4)

    def test_upgrade_requires_immutable_target_and_authorized_apply(self):
        content, _ = read_frontmatter(SKILL_PATHS["sol-luna-upgrade"])
        for invariant in (
            "explicitly authorizes",
            "including prereleases",
            "strict project SemVer",
            "SemVer precedence",
            "TAG_MOVED",
            "detached `HEAD`",
            "--source-commit <40hex>",
            "zero writes and zero backups",
            "never downgrade automatically",
            "fail closed",
            "Codex Native Workers",
            "legacy Sol/Luna invocation remains supported",
            "authorization covers this product upgrade only",
            "one two-root transaction",
            "prevalidate every backup and rollback entry",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, content)
        notice = (
            "目标：<version>",
            "渠道：Prerelease / Public Beta",
            "此版本可能包含尚未完成的变化，外部真实运行验证少于稳定版。",
            "修改托管文件前会创建事务备份；不会有意覆盖与本项目无关的用户配置。",
        )
        positions = [content.index(line) for line in notice]
        self.assertEqual(positions, sorted(positions))

    def test_placeholders_belong_only_to_their_skill(self):
        for name, path in SKILL_PATHS.items():
            content, _ = read_frontmatter(path)
            with self.subTest(name=name):
                self.assertEqual(content.count("<SELECTOR_COMMAND>"), int(name == "sol-luna-delegate"))
                self.assertEqual(content.count("<STATUS_COMMAND>"), int(name == "sol-luna-status"))
                self.assertFalse((SKILLS_ROOT / name / "agents" / "openai.yaml").exists())


if __name__ == "__main__":
    unittest.main()

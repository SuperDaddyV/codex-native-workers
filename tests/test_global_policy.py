import unittest
from pathlib import Path

from scripts.install import (
    AGENTS_BEGIN,
    AGENTS_END,
    GLOBAL_POLICY_MAX_BYTES,
    render_delegate_skill,
    render_global_policy,
    render_status_skill,
)


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates" / "AGENTS.global.md").read_text(encoding="utf-8")
STATUS_SKILL = (
    ROOT / "payload" / "skills" / "sol-luna-status" / "SKILL.md"
).read_text(encoding="utf-8")
DELEGATE_SKILL = (
    ROOT / "payload" / "skills" / "sol-luna-delegate" / "SKILL.md"
).read_text(encoding="utf-8")
UPGRADE_SKILL = (
    ROOT / "payload" / "skills" / "sol-luna-upgrade" / "SKILL.md"
).read_text(encoding="utf-8")


class GlobalPolicyTests(unittest.TestCase):
    def test_managed_global_block_fits_the_byte_budget(self):
        self.assertEqual(GLOBAL_POLICY_MAX_BYTES, 2048)
        for platform, home in (
            ("Windows", r"C:\Program Data\Codex Home"),
            ("Linux", "/opt/Codex Home"),
        ):
            rendered = render_global_policy(
                TEMPLATE, home, platform_name=platform
            )
            block = f"{AGENTS_BEGIN}\n{rendered.rstrip()}\n{AGENTS_END}\n"
            with self.subTest(platform=platform):
                self.assertLessEqual(len(block.encode("utf-8")), 2048)

    def test_global_policy_routes_before_delegation_and_keeps_coordinator_authority(self):
        for invariant in (
            "Codex Native Workers",
            "model-agnostic",
            "`Coordinator`",
            "After planning",
            "worthwhile independent bounded work",
            "small tasks remain Coordinator-owned",
            "Sol handles difficult bounded work",
            "Luna handles clear, repetitive work",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, TEMPLATE)
        self.assertIn("load `sol-luna-delegate`", TEMPLATE)
        self.assertIn("returned native `agent_type` roles", TEMPLATE)
        self.assertIn("sol-luna-status", TEMPLATE)
        self.assertIn("sol-luna-upgrade", TEMPLATE)
        self.assertIn("retain the affected work", TEMPLATE)
        self.assertNotIn("<SELECTOR_COMMAND>", TEMPLATE)
        self.assertNotIn("<STATUS_COMMAND>", TEMPLATE)
        for delegated_detail in (
            "published_at",
            "TAG_MOVED",
            "--workers",
            "diagnostic_schema_version",
        ):
            with self.subTest(detail=delegated_detail):
                self.assertNotIn(delegated_detail, TEMPLATE)

    def test_concurrency_policy_uses_runtime_capacity_and_allows_bounded_expansion(self):
        for invariant in (
            "0–3 workers",
            "4–6",
            "non-overlapping writes",
            "actual runtime capacity",
            "no fixed Sol quota",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, TEMPLATE)

    def test_receipts_are_short_evidence_only_and_use_no_extra_tools(self):
        for invariant in (
            "short evidence-only final line",
            "actual direct role/count pair each",
            "visible overlap",
            "Coordinator/Workers: Coordinator-only",
            "current-task selection/agent/spawn failure",
            "per-turn receipt skill/tool",
            "receipt-only file, selector, probe, network, or state access",
        ):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, TEMPLATE)
        self.assertNotIn("reference_cost_comparison", TEMPLATE)
        self.assertNotIn("Luna ref-cost", TEMPLATE)

    def test_worker_and_status_commands_are_rendered_only_in_their_skills(self):
        windows_home = r"C:\Program Data\Codex Home"
        command = "python 'C:\\Program Data\\Codex Home\\sol-luna-v4\\selector.py'"
        delegate = render_delegate_skill(
            DELEGATE_SKILL, windows_home, platform_name="Windows"
        )
        status = render_status_skill(
            STATUS_SKILL, windows_home, platform_name="Windows"
        )
        self.assertIn(command, delegate)
        self.assertIn("--ensure-daily --print-selection --workers", delegate)
        self.assertNotIn("<SELECTOR_COMMAND>", delegate)
        self.assertIn(command, status)
        self.assertIn("--status-json", status)
        self.assertNotIn("<STATUS_COMMAND>", status)
        self.assertNotIn("--workers", status)

    def test_release_discovery_stays_outside_installer(self):
        installer = (ROOT / "scripts" / "install.py").read_text(encoding="utf-8")
        self.assertIn("Release discovery is a semantic workflow outside the installer", UPGRADE_SKILL)
        self.assertNotIn("/repos/SuperDaddyV/codex-sol-luna-worker/releases", installer)
        self.assertNotIn("target_commitish", installer)
        self.assertNotIn("urllib", installer)


if __name__ == "__main__":
    unittest.main()

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
PREVIEW = ROOT / "NATIVE_WORKERS_PREVIEW.md"
INSTALLATION = ROOT / "INSTALLATION.md"
INSTALLATION_ZH = ROOT / "INSTALLATION.zh-CN.md"
ASSIST = ROOT / "CODEX_SOL_LUNA_INSTALL_ASSIST.md"
ASSIST_ZH = ROOT / "CODEX_SOL_LUNA_INSTALL_ASSIST.zh-CN.md"
SETUP = ROOT / "CODEX_SOL_LUNA_SETUP.md"
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
ISSUE_FORMS = {
    "bug-report.yml": {
        "summary", "expected", "os", "codex_client_version", "python_version",
        "install_type", "version", "receipt", "luna_run", "minimal_logs",
        "reproduction", "context", "privacy_confirmation",
        "release_channel", "configuration_status", "sol_run", "legacy_receipt",
    },
    "compatibility-report.yml": {
        "os", "codex_client_version", "python_version", "install_type",
        "from_version", "installed_version", "installation_result", "daily_role",
        "sol_only_receipt", "delegated_receipt", "luna_delegation",
        "parallel_delegation", "usage_duration", "problems_found",
        "overall_result", "privacy_confirmation",
        "release_channel", "configuration_status", "sol_delegation", "sol_role",
        "coordinator_workers_receipt",
    },
    "feature-feedback.yml": {
        "type", "improvement", "reason", "suggested_behavior", "context",
        "privacy_confirmation",
        "release_channel", "version", "evidence_status",
    },
}
PUBLIC_DOCS = (
    README,
    README_ZH,
    PREVIEW,
    INSTALLATION,
    INSTALLATION_ZH,
    ASSIST,
    ASSIST_ZH,
    SETUP,
    ROOT / "ARCHITECTURE.md",
    ROOT / "RUNTIME_TESTS.md",
    ROOT / "SECURITY.md",
    ROOT / "CHANGELOG.md",
)
LEGACY_DEFAULT_SETUP_COMMIT = "e1967f8fc957904e3f90b0dd6140430f792d9956"
PREVIOUS_STABLE_ASSIST_COMMIT = "39594139eaeeda705528733fc383333504546fb6"
PREVIOUS_STABLE_SETUP_COMMIT = "2c912b1e1a0fdbd115eb605517fde9385b633745"
PREVIOUS_STABLE_RUNTIME_SOURCE_COMMIT = "67a72f8accc5d53ef04ff8d64d8838e397ceecda"
V411_ASSIST_CONTRACT_COMMIT = "17eb1d370929e884f91c5f1920a2e0868ce4a421"
V411_SETUP_CONTRACT_COMMIT = "d4a044a04df509285ef38c6afc28b5a68a48a0f9"
V412_ASSIST_CONTRACT_COMMIT = "a130c676fa5924e44034dc8c27f3dc0abfc3bcad"
V412_SETUP_CONTRACT_COMMIT = "4b2a6004fb92b6661166cb73e656cc2888b0a2ef"
V413_ASSIST_CONTRACT_COMMIT = "23eeba1a5fb21e0483f4140aeca18b483f3e85bf"
V413_SETUP_CONTRACT_COMMIT = "5c29abc9aed340f4a7c45c22a0f8b36242b920bb"
V414_RELEASE_ASSIST_CONTRACT_COMMIT = "5e1ce80d3ed444834f700ac0154bfe444dec8cd3"
PINNED_ASSIST_COMMIT = "7494d47574ac751e76a231033a0ed91686899a07"
PINNED_SETUP_COMMIT = "bf01c438eae66f5ef9a27d401c6ee845f89d5d59"
PINNED_ASSIST_BLOB_URL = (
    "https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/"
    f"{PINNED_ASSIST_COMMIT}/CODEX_SOL_LUNA_INSTALL_ASSIST.md"
)
PINNED_SETUP_BLOB_URL = (
    "https://github.com/SuperDaddyV/codex-sol-luna-worker/blob/"
    f"{PINNED_SETUP_COMMIT}/CODEX_SOL_LUNA_SETUP.md"
)
RC5_RUNTIME_SOURCE_COMMIT = "5ae88ff9190b31174c55a6136c0c8c8611d0b34c"
RC5_SETUP_CONTRACT_COMMIT = "ccd9d84da2f74df9ca2d919729b75eebf2dac27a"
RC5_STALE_SETUP_CONTRACT_COMMIT = "7affbcda6f68cd125aaf6eec3c0e3ff04ebd60d9"
RC6_RUNTIME_SOURCE_COMMIT = "50ff886d1004ac3dd43b1f4ce531a2a8af8f7a49"
RC6_SETUP_CONTRACT_COMMIT = "3e19e2f547c6fca2a888a176767e8dc69240acbc"
RC6_STALE_SETUP_CONTRACT_COMMIT = "86424ea4d6f6630a34b6e4daa22d2d93a5576ddf"
V411_RUNTIME_SOURCE_COMMIT = "ca8e9e4caf5564ffe8d0a11fe376047594f8a748"
V412_RUNTIME_SOURCE_COMMIT = "551520c2435aca94d60132f292edbd53cc975cbe"
V412_EXACT_CI_RUN = "32717295801"
V412_MASTER_EVIDENCE_COMMIT = "fac118ac5ca096aaf1ef8d68b79bfc1372998a5a"
V412_MASTER_CI_RUN = "32717520585"
V413_RUNTIME_SOURCE_COMMIT = "71894e2ef5007c9ba3e6f9d9efbf91cbdad302b4"
V413_EXACT_CI_RUN = "33253340074"
V413_MASTER_EVIDENCE_COMMIT = "bafc41b50269a0b65aba64594e850f6171a714ac"
V413_MASTER_CI_RUN = "33253429974"
V414_RUNTIME_SOURCE_COMMIT = "6a537b445ad6f17a9600c05e655f51a2844bfcc8"
RC1_RUNTIME_SOURCE_COMMIT = "527b174df13643a38bfe29652208eaa00f63fbf7"
V414_EXACT_CI_RUN = "33264634602"
V414_SETUP_CONTRACT_COMMIT = PINNED_SETUP_COMMIT
V412_BASELINE_RUNTIME_SOURCE_COMMIT = (
    "50ff886d1004ac3dd43b1f4ce531a2a8af8f7a49"
)
ASSIST_RAW_PATTERN = re.compile(
    r"https://raw\.githubusercontent\.com/"
    r"SuperDaddyV/codex-sol-luna-worker/([0-9a-f]{40})/"
    r"CODEX_SOL_LUNA_INSTALL_ASSIST\.md"
)
SETUP_RAW_PATTERN = re.compile(
    r"https://raw\.githubusercontent\.com/"
    r"SuperDaddyV/codex-sol-luna-worker/([0-9a-f]{40})/"
    r"CODEX_SOL_LUNA_SETUP\.md"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def local_markdown_targets(content: str):
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", content):
        target = match.group(1).split("#", 1)[0]
        if not target or "://" in target or target.startswith(("#", "mailto:")):
            continue
        yield target


class DocumentationTests(unittest.TestCase):
    def test_bilingual_navigation_and_setup_contract(self):
        self.assertTrue(ASSIST.is_file())
        self.assertTrue(ASSIST_ZH.is_file())
        self.assertTrue(SETUP.is_file())
        self.assertIn("[简体中文](README.zh-CN.md)", text(README))
        self.assertIn("[English](README.md)", text(README_ZH))
        self.assertIn(
            "[Chinese translation](CODEX_SOL_LUNA_INSTALL_ASSIST.zh-CN.md)",
            text(README),
        )
        self.assertIn(
            "[中文审阅版](CODEX_SOL_LUNA_INSTALL_ASSIST.zh-CN.md)",
            text(README_ZH),
        )

    def test_required_badges_and_homepage_sections(self):
        for path, headings in (
            (
                README,
                (
                    "What it is",
                    "Choose your version",
                    "v4.2.0-rc1 preview",
                    "How Coordinator and workers collaborate",
                    "Core value",
                    "Requirements",
                    "Stable installation (default)",
                    "Daily use",
                    "Confirm it is working",
                    "Upgrade, rollback, and uninstall",
                    "Technical documentation",
                    "Feedback",
                    "License",
                ),
            ),
            (
                README_ZH,
                (
                    "这是什么",
                    "选择版本",
                    "v4.2.0-rc1 预览版",
                    "Coordinator 与 worker 如何协作",
                    "核心价值",
                    "系统要求",
                    "Stable 安装（默认）",
                    "日常使用",
                    "如何确认生效",
                    "升级、回滚与卸载",
                    "技术文档",
                    "反馈",
                    "License",
                ),
            ),
        ):
            content = text(path)
            self.assertIn("actions/workflows/validate.yml/badge.svg", content)
            self.assertIn("releases/tag/v4.1.4", content)
            self.assertIn("img.shields.io/badge/stable-v4.1.4", content)
            self.assertIn("github/license", content)
            self.assertEqual(
                re.findall(r"(?m)^## (.+)$", content),
                list(headings),
            )
            self.assertGreaterEqual(len(content.splitlines()), 180)
            self.assertLessEqual(len(content.splitlines()), 260)
            self.assertEqual(content.count("> [!WARNING]"), 1)
            self.assertNotIn("historical_preview", content)

    def test_readmes_explain_native_worker_routing_parallelism_and_receipts(self):
        english = text(README)
        chinese = text(README_ZH)

        for content in (english, chinese):
            self.assertTrue(content.startswith("# Codex Native Workers\n"))
            self.assertEqual(content.count("```mermaid"), 1)
            self.assertIn("flowchart TD", content)
            self.assertIn("Task Contract", content)
            self.assertIn("Daily Selector", content)
            self.assertIn("`ultra`", content)
            self.assertIn(
                "Coordinator/Workers: delegated · sol_high ×1", content
            )
            self.assertIn(
                "Coordinator/Workers: delegated · luna_high ×2 · parallel",
                content,
            )
            self.assertIn(
                "Coordinator/Workers: Coordinator-only · too small", content
            )
            self.assertIn(
                "Coordinator/Workers: Coordinator-only · no independent work",
                content,
            )
            self.assertNotIn("Sol/Luna: delegated", content)
            self.assertNotIn("Sol/Luna: Sol-only", content)
            self.assertIn("[agents] enabled = false", content)
            self.assertIn("0–3", content)
            self.assertIn("4–6", content)

        for phrase in (
            "user-selected **Coordinator**",
            "Astra is one Coordinator example",
            "Sol handles difficult bounded execution",
            "Luna handles clear bounded execution",
            "independent bounded task is worthwhile",
            "There is no fixed Sol quota",
            "**Parallel:**",
            "**Sequential:**",
            "**Coordinator-only:**",
            "share the current workspace",
            "configuration alone is not runtime enforcement",
            "do not use `ultra`",
        ):
            self.assertIn(phrase, english)

        for phrase in (
            "用户选择的 **Coordinator**",
            "Astra 只是 Coordinator 的一个示例",
            "Sol 执行复杂的边界任务",
            "Luna 执行清楚的边界任务",
            "值得执行的独立边界任务",
            "Sol 没有固定配额",
            "**并行：**",
            "**串行：**",
            "**Coordinator-only：**",
            "共享当前工作区",
            "配置本身不等于 runtime enforcement",
            "不使用 `ultra`",
        ):
            self.assertIn(phrase, chinese)

    def test_rc1_preview_contract_is_prominent_bilingual_and_fail_closed(self):
        english = text(README)
        chinese = text(README_ZH)
        preview = text(PREVIEW)
        release_url = (
            "https://github.com/SuperDaddyV/codex-sol-luna-worker/"
            "releases/tag/v4.2.0-rc1"
        )

        for content in (english, chinese):
            self.assertIn("img.shields.io/badge/preview-v4.2.0--rc1", content)
            self.assertIn(release_url, content)
            self.assertGreaterEqual(content.count("NATIVE_WORKERS_PREVIEW.md"), 3)
            self.assertIn("40-hex commit", content)
            self.assertIn("detached checkout", " ".join(content.split()))
            self.assertIn("sol-luna-upgrade", content)
            self.assertNotIn("<PREVIEW", content)
            self.assertNotIn("<RC1", content)

        for phrase in (
            "non-draft GitHub Prerelease",
            "Published preview",
            "read the remote tag again",
            "moving branch",
            "Strong recursive isolation therefore remains unsupported",
            "not a measured installation success rate",
        ):
            self.assertIn(phrase, english)
        for phrase in (
            "已发布、非 draft 的 GitHub Prerelease",
            "再次读取远端 tag",
            "可变分支",
            "强递归隔离仍不受支持",
            "已发布预览版",
        ):
            self.assertIn(phrase, chinese)

        for content, start, end in (
            (
                english,
                "## v4.2.0-rc1 preview",
                "## How Coordinator and workers collaborate",
            ),
            (
                chinese,
                "## v4.2.0-rc1 预览版",
                "## Coordinator 与 worker 如何协作",
            ),
        ):
            section = content[content.index(start) : content.index(end)]
            self.assertEqual(
                set(re.findall(r"\b[0-9a-f]{40}\b", section)),
                {RC1_RUNTIME_SOURCE_COMMIT},
            )
            prompts = re.findall(r"```text\n(.*?)\n```", section, re.S)
            self.assertEqual(len(prompts), 1)
            self.assertIn(
                "https://raw.githubusercontent.com/SuperDaddyV/"
                f"codex-sol-luna-worker/{RC1_RUNTIME_SOURCE_COMMIT}/"
                "NATIVE_WORKERS_PREVIEW.md",
                prompts[0],
            )
            self.assertIn("dry-run", prompts[0])
            self.assertIn("apply", prompts[0])
            self.assertIn("python", prompts[0])
            self.assertIn("tomllib", prompts[0])
            self.assertNotIn("already published", section)
            self.assertNotIn("不声称预览版 Release 已经发布", section)
            self.assertNotRegex(section, r"\b20\d{2}-\d{2}-\d{2}\b")
            self.assertNotRegex(section, r"<[^>]*(?:SHA|COMMIT|DATE)[^>]*>")

        for content in (
            preview,
            text(ROOT / "ARCHITECTURE.md"),
            text(ROOT / "CHANGELOG.md"),
            text(ROOT / "RUNTIME_TESTS.md"),
        ):
            self.assertIn("v4.2.0-rc1", content)
        security = text(ROOT / "SECURITY.md")
        self.assertIn("Codex Native Workers v4.2 preview scope", security)
        self.assertIn("Strict recursive isolation is unsupported", security)
        self.assertIn("published, non-draft GitHub", preview)
        self.assertIn("TAG_MOVED", preview)
        self.assertIn("Strong prevention of recursive worker delegation", preview)

    def test_readmes_bound_preview_capabilities_and_reference_claims(self):
        english = text(README)
        chinese = text(README_ZH)

        for content in (english, chinese):
            self.assertIn("0.155.0-alpha.9.2", content)
            self.assertIn("[agents] enabled = false", content)
            self.assertIn("benchmark reference data", content)
            self.assertIn("reference_only", content)
            self.assertIn("quality-only", content)
            self.assertIn("**FAIL**", content)
            self.assertIn("**UNKNOWN**", content)
            self.assertIn("**NOT RUN**", content)
            self.assertIn("2 KiB", content)
            for skill_name in (
                "sol-luna-delegate",
                "sol-luna-status",
                "sol-luna-upgrade",
            ):
                self.assertIn(skill_name, content)

        for phrase in (
            "Three-worker overlap has been observed",
            "configured maximum of six is unverified",
            "with pre-rc1 installed roles",
            "FAIL** for Sol tool visibility",
            "post-install Luna child",
            "Nested invocation was **NOT RUN**",
            "invocation enforcement remains **UNKNOWN**",
            "without a Hook Router or custom orchestration engine",
            "never a billing or quota-savings claim",
        ):
            self.assertIn(phrase, english)
        for phrase in (
            "已观察到三个 worker 重叠执行",
            "配置上限六个尚未验证",
            "rc1 之前安装的角色",
            "Sol tool visibility 为 **FAIL**",
            "安装后的 Luna child",
            "调用防护为 **UNKNOWN**",
            "nested invocation 为 **NOT RUN**",
            "不需要 Hook Router 或自建编排引擎",
            "绝不据此声称实际账单或额度节省",
        ):
            self.assertIn(phrase, chinese)

    def test_stable_installation_entry_declares_hard_prerequisites(self):
        english = text(README)
        chinese = text(README_ZH)
        assist = text(ASSIST)
        for phrase in (
            "Sol/Luna Assisted Installation",
            "Codex CLI: PASS <version> / MISSING_OR_UNUSABLE",
            "Python: PASS <version> / MISSING_OR_UNSUPPORTED",
            "Git: PASS <version> / MISSING",
            "GitHub HTTPS: PASS / BLOCKED / NOT_CHECKED (Git required)",
            "Recovery: NONE / SAFE / AWAITING_APPROVAL / NEEDS_USER_ACTION",
            "Ready: YES / NO",
            "codex --version",
            "git --version",
            "git ls-remote",
        ):
            self.assertIn(phrase, assist)
        for content in (english, chinese):
            self.assertIn(PINNED_ASSIST_COMMIT, content)
            self.assertIn(PINNED_SETUP_COMMIT, content)

        self.assertIn("Codex Desktop alone is not sufficient", english)
        self.assertIn("Git for the required immutable exact-commit checkout", english)
        self.assertIn("仅安装 Codex Desktop 还不够", chinese)
        self.assertIn("用于不可变精确 commit checkout 的 Git", chinese)

    def test_installation_help_covers_actual_launcher_roots_and_recovery(self):
        python_check = (
            'python -c "import sys, tomllib; '
            'assert sys.version_info >= (3, 11); print(sys.version)"'
        )
        for path in (README, README_ZH):
            prompts = re.findall(r"```text\n(.*?)\n```", text(path), re.S)
            stable = [p for p in prompts if "CODEX_SOL_LUNA_INSTALL_ASSIST.md" in p]
            self.assertEqual(len(stable), 1)
            self.assertIn(python_check, stable[0])

        for guide, homepage in ((INSTALLATION, README), (INSTALLATION_ZH, README_ZH)):
            content = text(guide)
            self.assertIn(f"]({guide.name})", text(homepage))
            self.assertIn(python_check, content)
            self.assertIn(RC1_RUNTIME_SOURCE_COMMIT, content)
            self.assertIn("CODEX_HOME", content)
            self.assertIn("<SKILLS_ROOT>", content)
            self.assertIn("AGENTS.override.md", content)
            self.assertIn("OWNERSHIP_CONFLICT", content)
            self.assertIn("IDEMPOTENT_PASS", content)
            self.assertIn("Today Selection not initialized", content)
            self.assertIn("Not checked", content)
            self.assertIn("--source-commit", content)
            self.assertIn("native-workers-rc1-validation.json", content)
            self.assertNotIn("raw.githubusercontent.com/SuperDaddyV/"
                             "codex-sol-luna-worker/master/", content)
            self.assertEqual(content.count("```") % 2, 0)

        self.assertIn("not native installation proof on all platforms or a measured user",
                      " ".join(text(INSTALLATION).split()))
        self.assertIn("不是用户安装成功率统计", text(INSTALLATION_ZH))

    def test_readme_uses_single_v414_immutable_installation_entry(self):
        english = text(README)
        chinese = text(README_ZH)
        for content in (english, chinese):
            assist_url = (
                "https://raw.githubusercontent.com/SuperDaddyV/"
                f"codex-sol-luna-worker/{PINNED_ASSIST_COMMIT}/"
                "CODEX_SOL_LUNA_INSTALL_ASSIST.md"
            )
            self.assertEqual(content.count(assist_url), 1)
            self.assertEqual(content.count(PINNED_ASSIST_BLOB_URL), 1)
            self.assertEqual(content.count(PINNED_SETUP_BLOB_URL), 3)
            self.assertNotIn("](CODEX_SOL_LUNA_INSTALL_ASSIST.md)", content)
            self.assertNotIn("](CODEX_SOL_LUNA_SETUP.md)", content)
            self.assertNotIn(LEGACY_DEFAULT_SETUP_COMMIT, content)
            self.assertIn(PINNED_ASSIST_COMMIT, content)
            self.assertIn(PINNED_SETUP_COMMIT, content)
            self.assertIn(V414_RUNTIME_SOURCE_COMMIT, content)
            for historical in ("RC3", "RC4", "RC5", "RC6"):
                self.assertNotIn(historical, content)
        assist = text(ASSIST)
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, assist)
        self.assertEqual(
            SETUP_RAW_PATTERN.findall(assist),
            [V414_SETUP_CONTRACT_COMMIT],
        )
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, text(SETUP))
        self.assertIn("single prompt", english)
        self.assertIn("只粘贴下面这一个提示词", chinese)
        for stale in (
            PREVIOUS_STABLE_ASSIST_COMMIT,
            PREVIOUS_STABLE_SETUP_COMMIT,
            PREVIOUS_STABLE_RUNTIME_SOURCE_COMMIT,
            "unreleased candidate",
            "未发布候选",
        ):
            self.assertNotIn(stale, english + chinese)

    def test_setup_preflight_stops_missing_dependencies_before_writes(self):
        content = text(SETUP)
        preflight = content.index("## 0A. Installation Preflight")
        source = content.index("## 5. Source Acquisition")
        capability = content.index("## 6. Codex Capability")
        dry_run = content.index("## 8. Dry Run")
        self.assertLess(preflight, source)
        self.assertLess(source, capability)
        self.assertLess(capability, dry_run)
        self.assertLess(preflight, dry_run)
        for phrase in (
            "Before cloning or downloading source",
            "before any filesystem write",
            "`Ready: YES` requires every hard prerequisite above to pass",
            "do not create or modify files",
            "BLOCKED: CODEX_CLI_REQUIRED",
            "BLOCKED: PYTHON_3_11_WITH_TOMLLIB_REQUIRED",
            "BLOCKED: GIT_REQUIRED_FOR_IMMUTABLE_SOURCE",
            "BLOCKED: GITHUB_HTTPS_REQUIRED",
            "Do not install system dependencies, modify `PATH`",
            "`curl` and other download tools are not required",
        ):
            self.assertIn(phrase, content)

    def test_assisted_installation_recovery_is_bounded_and_preserves_setup_gates(self):
        content = text(ASSIST)
        setup_url = (
            "https://raw.githubusercontent.com/SuperDaddyV/"
            f"codex-sol-luna-worker/{V414_SETUP_CONTRACT_COMMIT}/"
            "CODEX_SOL_LUNA_SETUP.md"
        )

        for identity in (
            "Stable release: `v4.1.4`",
            V414_RUNTIME_SOURCE_COMMIT,
            V414_SETUP_CONTRACT_COMMIT,
            setup_url,
            "`v4.1.0-rc6` remains an immutable historical",
        ):
            self.assertIn(identity, content)

        for boundary in (
            "Do not stop at the first missing",
            "Safe automatic recovery",
            "Approval-required recovery",
            "request to install Sol/Luna is not approval",
            "Persistent `PATH` changes require separate inclusion",
            "Guided user action",
            "SOL_LUNA_ASSIST_RESUME",
            "Run a deterministic remediation command at most once",
            "at most three total attempts for a transient GitHub HTTPS check",
            "No output for 30 seconds is not by itself a product failure",
            "Any setup result containing",
            "fresh-task smoke",
            "--dangerously-bypass-approvals-and-sandbox",
        ):
            self.assertIn(boundary, content)

        for protected in (
            "authentication",
            "proxy",
            "certificate trust",
            "sandbox",
            "organization policy",
            "ownership",
            "transaction",
        ):
            self.assertIn(protected, content.lower())

        self.assertNotIn(
            "raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/master/",
            content,
        )

    def test_v414_stable_assistance_is_deterministic_and_bounded(self):
        content = text(ASSIST)
        stable = content.index("## 11. v4.1.4 deterministic Stable assistance")
        capability = content.index("### 11.6 Early capability and installer handoff")
        dry_run = content.index("installer's non-mutating dry-run", capability)
        self.assertLess(stable, capability)
        self.assertLess(capability, dry_run)
        for phrase in (
            "P3 standalone bootstrap is explicitly out of scope",
            "scripts/install_assist.py check",
            "scripts/install_assist.py plan",
            "scripts/install_assist.py recover",
            "scripts/install_assist.py install",
            "scripts/install_assist.py report",
            "RECOVERY_PLAN_CHANGED",
            "scripts/install_recovery_catalog.json",
            "approval_required",
            "user_action",
            "IDEMPOTENT_PASS",
            "run the five Luna efforts through ephemeral",
            "Codex executions with user config ignored",
            "whitelist-only",
            "Installation Complete",
            "Reload Required",
            "Selector Initialization Required",
            "Needs User Action",
            "Blocked",
        ):
            self.assertIn(phrase, content)
        for phase in (
            "CHECKING",
            "SAFE_RECOVERY",
            "AWAITING_APPROVAL",
            "RECHECKING",
            "CAPABILITY_PRECHECK",
            "DRY_RUN",
            "INSTALLING",
            "RELOAD_REQUIRED",
            "SELECTOR_INITIALIZATION",
            "FRESH_TASK_SMOKE",
            "COMPLETE",
            "NEEDS_USER_ACTION",
            "BLOCKED",
        ):
            self.assertIn(phase, content)
        self.assertIn("This section specifies the deterministic installation experience", content)
        self.assertIn("Source Commit A above", content)
        self.assertNotIn("Source Commit A2 above", content)
        self.assertIn("exact immutable documentation commit", content)
        self.assertIn("No preflight state file is created", content)
        self.assertIn("DAILY_SELECTION_PROOF_REQUIRED", content)
        self.assertIn("--ensure-daily --print-selection", content)
        self.assertIn("The smoke remains status-only", content)
        self.assertNotIn("unreleased `v4.1.4`", content)
        self.assertNotIn("assistance candidate", content)
        self.assertNotIn(PREVIOUS_STABLE_RUNTIME_SOURCE_COMMIT, content)
        self.assertNotIn(PREVIOUS_STABLE_SETUP_COMMIT, content)
        self.assertEqual(
            content.count(f"--source-commit {V414_RUNTIME_SOURCE_COMMIT}"), 2
        )

    def test_chinese_assistance_document_is_review_only_and_covers_same_boundaries(self):
        content = text(ASSIST_ZH)
        self.assertIn("本文件只用于中文审阅，不是可执行安装权威", content)
        self.assertIn("英文 `CODEX_SOL_LUNA_INSTALL_ASSIST.md`", content)
        self.assertIn("不能执行可变 `master` 上的中文译文", content)
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, content)
        self.assertIn(V414_SETUP_CONTRACT_COMMIT, content)
        for phrase in (
            "`v4.1.0-rc6` 继续作为",
            "不可变的历史 Prerelease",
            "P3 排除边界",
            "scripts/install_assist.py check",
            "RECOVERY_PLAN_CHANGED",
            "scripts/install_recovery_catalog.json",
            "IDEMPOTENT_PASS",
            "Capability 前置门禁",
            "Installer 唯一写入权威",
            "脱敏支持报告",
            "Installation Complete",
            "Reload Required",
            "Selector Initialization Required",
            "Needs User Action",
            "Blocked",
            "SELECTOR_INITIALIZATION",
            "DAILY_SELECTION_PROOF_REQUIRED",
            "--ensure-daily --print-selection",
            "--dangerously-bypass-approvals-and-sandbox",
        ):
            self.assertIn(phrase, content)
        self.assertNotIn(
            "raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/master/",
            content,
        )
        self.assertNotIn("安装助手候选", content)
        self.assertNotIn(PREVIOUS_STABLE_RUNTIME_SOURCE_COMMIT, content)
        self.assertNotIn(PREVIOUS_STABLE_SETUP_COMMIT, content)

    def test_setup_records_v414_stable_evidence_and_handoff(self):
        content = text(SETUP)
        architecture = text(ROOT / "ARCHITECTURE.md")
        security = text(ROOT / "SECURITY.md")
        handoff = content.index("## 22. v4.1.4 Stable assisted installation handoff")
        self.assertGreater(handoff, content.index("## 21. Final Report"))
        for phrase in (
            "Sections 0–21 are the reviewed `v4.1.4` Stable transactional setup contract",
            "scripts/install_assist.py",
            "scripts/install_recovery_catalog.json",
            "clean detached Stable Source Commit A checkout",
            "runs the five",
            "ephemeral read-only Luna capability checks",
            "Without `--apply`, it stops at `DRY_RUN`",
            "zero-write, zero-backup fast path",
            "`SELECTOR_INITIALIZATION` gate",
            "--ensure-daily --print-selection",
            "must not initialize Daily selection",
            "P3 standalone bootstrap remains out of scope",
        ):
            self.assertIn(phrase, content)
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, content[:handoff])
        self.assertNotIn("<V4_1_4_SOURCE_COMMIT>", content)
        self.assertIn("pins this Setup contract", content)
        self.assertIn("The public README pins this contract", content)
        for phrase in (
            "v4.1.4",
            "exact recovery plan + SHA-256 Plan ID",
            "scripts/install_recovery_catalog.json",
            "explicit Daily selector initialization and proof",
            "compatibility smoke remains read-only and status-only",
        ):
            self.assertIn(phrase, architecture + content)
        for phrase in (
            "v4.1.4 Stable boundary",
            "executes approved recovery as argument vectors without a",
            "five-effort Luna probe is ephemeral",
            "P3",
            "standalone bootstrap is excluded",
            "controls do not change the installed selector",
            "Stable assistant adds an explicit post-reload `SELECTOR_INITIALIZATION` handoff",
            "cannot initialize Daily selection itself",
        ):
            self.assertIn(phrase, security)
        for value in (
            V414_RUNTIME_SOURCE_COMMIT,
            V414_EXACT_CI_RUN,
            "366",
            "V414_FAKE_HOME_LIFECYCLE = PASS",
            "V414_UNINSTALL_TRANSACTION = PASS",
            "V414_REAL_GLOBAL_APPLY = NOT_RUN",
            "V414_FRESH_TASK_COMPATIBILITY = NOT_RUN",
        ):
            self.assertIn(value, content + text(ROOT / "RUNTIME_TESTS.md"))

    def test_stable_and_preview_feedback_forms_and_guidance(self):
        self.assertEqual(
            text(ISSUE_TEMPLATE_DIR / "config.yml").strip(),
            "blank_issues_enabled: false",
        )
        for filename, expected_ids in ISSUE_FORMS.items():
            path = ISSUE_TEMPLATE_DIR / filename
            with self.subTest(form=filename):
                self.assertTrue(path.is_file())
                content = text(path)
                ids = re.findall(r"(?m)^\s+id:\s+([A-Za-z0-9_-]+)\s*$", content)
                field_ids = set(ids)
                self.assertEqual(field_ids, expected_ids)
                self.assertEqual(len(ids), len(field_ids))
                for key in ("name:", "description:", "title:", "body:"):
                    self.assertIn(key, content)
                self.assertIn("validations:", content)
                self.assertIn("type: dropdown", content)
                self.assertIn("options:", content)
                labels = re.findall(r"(?m)^      label: (.+)$", content)
                self.assertEqual(len(labels), len(set(labels)))
                self.assertNotIn("labels:", content)
                self.assertNotIn("contact_links:", content)
                self.assertIn("Stable (v4.1.4)", content)
                self.assertIn("Prerelease / preview (v4.2.0-rc1)", content)
                self.assertIn('"NOT RUN"', content)
                self.assertIn('"BLOCKED"', content)
                self.assertNotIn("public beta", content.lower())
                self.assertNotIn("public-beta", content.lower())
                self.assertNotIn("v4.1.0-rc4", content)

        bug = text(ISSUE_TEMPLATE_DIR / "bug-report.yml")
        for phrase in (
            "API keys", "access tokens", "cookies", "passwords",
            "private repository credentials", "personal email", "home-directory",
            "proprietary source/code", "minimum relevant logs",
            "unless specifically requested during later troubleshooting",
        ):
            self.assertIn(phrase, bug)
        self.assertIn("placeholder: v4.1.4", bug)
        self.assertNotIn("placeholder: v4.1.1", bug)
        self.assertIn("`Sol/Luna: Sol-only · no independent bounded work`", bug)
        self.assertIn("`Sol/Luna: delegated · luna_max ×2 · parallel`", bug)
        self.assertIn("`No Receipt`", bug)
        self.assertIn("Coordinator/Workers: delegated · sol_high ×1", bug)
        self.assertIn("Stable / legacy format", bug)
        self.assertIn('- "Yes"\n        - "No"\n        - "Not sure"', bug)

        compatibility = text(ISSUE_TEMPLATE_DIR / "compatibility-report.yml")
        for phrase in (
            "Success reports are welcome", "OS compatibility", "fresh installs",
            "upgrades", "Luna delegation", "Delegation Receipt behavior",
            "public GitHub Issues only", "write None if no problems were found",
            "placeholder: luna_max / Unknown",
            "placeholder: Works normally on my environment",
        ):
            self.assertIn(phrase, compatibility)
        for option in (
            "PASS", "PASS with minor issue", "FAIL", "Not tested",
            "Just installed", "Less than 1 day", "1–3 days", "4–7 days",
            "More than 1 week",
        ):
            self.assertIn(option, compatibility)
        self.assertIn("placeholder: v4.1.4 / v4.1.3 / Unknown", compatibility)
        self.assertIn("placeholder: sol_max / Unknown", compatibility)
        self.assertIn("Coordinator/Workers: delegated", compatibility)
        self.assertIn("sequential execution is not parallel", compatibility)
        self.assertIn("placeholder: v4.1.4", compatibility)
        self.assertNotIn("placeholder: v4.1.1", compatibility)

        feature = text(ISSUE_TEMPLATE_DIR / "feature-feedback.yml")
        self.assertIn("name: Feature request / feedback", feature)
        self.assertIn("Non-guarantee notice", feature)
        for option in (
            "Feature request", "Documentation", "UX / usability",
            "Installation experience", "Delegation behavior", "Other",
        ):
            self.assertIn(f"- {option}", feature)

        english = text(README)
        chinese = text(README_ZH)
        templates = (
            "bug-report.yml",
            "compatibility-report.yml",
            "feature-feedback.yml",
        )
        for content, feedback_heading, whole_warning in (
            (english, "## Feedback", "the entire `CODEX_HOME`"),
            (chinese, "## 反馈", "整个 `CODEX_HOME`"),
        ):
            self.assertIn(feedback_heading, content)
            self.assertGreater(
                content.index(feedback_heading), content.index("GitHub Releases")
            )
            for filename in templates:
                self.assertIn(
                    "https://github.com/SuperDaddyV/codex-sol-luna-worker/"
                    f"issues/new?template={filename}",
                    content,
                )
            self.assertIn("CODEX_HOME", content)
            self.assertIn(whole_warning, content)
        self.assertIn("v4.1.4", english)
        self.assertIn("v4.1.4", chinese)
        self.assertIn("[Bug Report]", english)
        self.assertIn("[Compatibility Report]", chinese)

    def test_stable_contract_and_specialized_history_docs_are_explicit(self):
        source_docs = (
            ROOT / "RUNTIME_TESTS.md",
            ROOT / "ARCHITECTURE.md",
            ROOT / "SECURITY.md",
            ROOT / "CHANGELOG.md",
        )
        combined = "\n".join(
            text(path)
            for path in (
                README,
                README_ZH,
                ASSIST,
                SETUP,
                ROOT / "ARCHITECTURE.md",
                ROOT / "SECURITY.md",
            )
        )
        default_assist_url = (
            "https://raw.githubusercontent.com/SuperDaddyV/"
            f"codex-sol-luna-worker/{PINNED_ASSIST_COMMIT}/"
            "CODEX_SOL_LUNA_INSTALL_ASSIST.md"
        )
        for path in (README, README_ZH):
            content = text(path)
            self.assertEqual(content.count(default_assist_url), 1)
            self.assertIn(PINNED_ASSIST_COMMIT, content)
            self.assertIn(PINNED_SETUP_COMMIT, content)
            self.assertIn("releases/tag/v4.1.4", content)
            self.assertIn("img.shields.io/badge/stable-v4.1.4", content)
            self.assertNotIn("historical_preview", content)
            self.assertNotIn(LEGACY_DEFAULT_SETUP_COMMIT, content)
            self.assertNotRegex(content, r"\bRC[3-6]\b")
            for removed in (
                "O4/O9",
                "Runtime Cases",
                "No confirmed product-runtime regression",
                "Luna ref-cost",
                "ModelDial API",
                "LKG fallback",
                "Advanced / Manual",
                "Optional parallel self-test",
                "## FAQ",
            ):
                self.assertNotIn(removed, content)
            self.assertNotIn("O1–O10", content)
            for link in (
                "CODEX_SOL_LUNA_SETUP.md",
                "ARCHITECTURE.md",
                "RUNTIME_TESTS.md",
                "SECURITY.md",
                "CHANGELOG.md",
                "codex-sol-luna-worker/releases",
            ):
                self.assertIn(link, content)
            for placeholder in ("<APPROVED_40_HEX_COMMIT>", "<TBD>", "pending"):
                self.assertNotIn(placeholder, content)

        setup = text(SETUP)
        self.assertIn("Contract version: `v4.1.4`", setup)
        self.assertIn(
            "`v4.1.4` is the Stable release target and default installation target",
            setup,
        )
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, setup)
        self.assertIn("`v4.1.3` remains the previous immutable Stable release", setup)
        self.assertIn("`v4.1.2`, `v4.1.1`, and `v4.1.0` remain older immutable Stable releases", setup)
        self.assertIn("`v4.1.0-rc6` remains an immutable historical Prerelease", setup)
        self.assertIn("`v4.1.0-rc5` is an older historical Preview", setup)
        for path in source_docs:
            content = text(path)
            self.assertIn("RC4", content)
            self.assertIn("v4.1.0-rc5", content)
            self.assertIn(V411_RUNTIME_SOURCE_COMMIT, content)
            self.assertIn("stable", content.lower())
            self.assertIn("prerelease", content.lower())
            for stale in (
                "RC6 is not tagged",
                "RC6 is an unpublished",
                "RC6 remains the unpublished",
                "Published/default Preview remains `v4.1.0-rc5`",
                "release pending",
            ):
                self.assertNotIn(stale, content)

        historical_evidence = text(ROOT / "RUNTIME_TESTS.md") + text(
            ROOT / "CHANGELOG.md"
        )
        self.assertIn(RC5_RUNTIME_SOURCE_COMMIT, historical_evidence)
        self.assertIn(RC5_SETUP_CONTRACT_COMMIT, historical_evidence)

        self.assertIn("v4.1.0-rc3", text(ROOT / "CHANGELOG.md"))
        self.assertIn(
            "FRESH_REPO_CONTEXT_DELEGATION_PASS",
            text(ROOT / "ARCHITECTURE.md"),
        )
        self.assertIn(
            "For v4.1.4 Stable, the directly validated upgrade baseline is a repository",
            setup,
        )
        self.assertNotIn("REAL GLOBAL RUNTIME NOT RUN", combined)
        self.assertIn("Global Runtime G1-G7", combined)
        self.assertIn("v4.1.4 Stable", text(README))
        self.assertIn("v4.1.4 Stable", text(README_ZH))
        self.assertNotRegex(combined, r"v4\.1\.0-rc3[^\n]*(?:—|is|是)\s*STABLE")
        self.assertNotIn(
            "RC2 repository-context delegation validation remains pending", combined
        )
        self.assertNotIn("RC3 Receipt runtime acceptance has not run", combined)
        runtime = text(ROOT / "RUNTIME_TESTS.md")
        self.assertIn(
            "v4.1.4 — CURRENT STABLE RELEASE / DEFAULT INSTALLATION TARGET",
            runtime,
        )
        self.assertIn(
            "They do not imply runtime validation across every operating system, "
            "Codex client, account, or user environment.",
            runtime,
        )
        self.assertNotIn("CURRENT PREVIEW / RUNTIME ACCEPTANCE PASS", runtime)
        self.assertIn(
            "v4.1.0-rc6 historical Preview — recorded fresh-task runtime acceptance",
            runtime,
        )
        self.assertIn(V411_RUNTIME_SOURCE_COMMIT, runtime)
        self.assertIn(RC6_RUNTIME_SOURCE_COMMIT, runtime)
        self.assertIn(
            "Compatibility smoke, O1-O10 acceptance, Final O4/O9 re-certification",
            runtime,
        )
        self.assertIn("are recorded `PASS`", runtime)
        self.assertIn("`RC6_RUNTIME_ACCEPTANCE_COMPLETED = YES`", runtime)
        self.assertIn("`RC6_FINAL_O4_O9_RECERTIFICATION = PASS`", runtime)
        self.assertIn("Real RC3 → RC4 Global upgrade — `PASS`", runtime)
        self.assertIn("Result: `UPGRADED`; effective changes: `2`", runtime)
        for case in ("Runtime Case A", "Runtime Case B", "Runtime Case C", "Runtime Case D"):
            self.assertIn(case, runtime)
        self.assertIn("Sol/Luna: Sol-only · reasoning/architecture task", runtime)
        self.assertIn("Sol/Luna: delegated · luna_max ×3 · parallel", runtime)
        self.assertIn("Sol/Luna: Sol-only · no independent bounded work", runtime)
        self.assertIn("Selector result: `NO_LUNA_PROFILE_AVAILABLE`", runtime)
        self.assertIn("availability evidence `NONE`; `Luna unavailable` is forbidden", runtime)
        self.assertIn("RC1 → RC3 Global upgrade — `PASS`", runtime)
        self.assertIn("Sol-only Receipt — `PASS`", runtime)
        self.assertIn("Delegated Receipt — `PASS`", runtime)
        self.assertNotIn("planned Receipt acceptance — `NOT RUN`", runtime)
        for status in (
            "DAY_2_CROSS_DAY_END_TO_END_PASS",
            "DAY_2_SAME_DAY_NEW_SESSION_PERSISTENCE_PASS",
            "SELECTOR_URL_EXCEPTION_HARDENING = DEFERRED_TO_PRE_STABLE",
        ):
            self.assertIn(status, runtime)
            self.assertIn(status, text(ROOT / "CHANGELOG.md"))
        self.assertIn(
            "CURRENT_TEST_OBSERVED_REFRESH_EVENT_DIRECTLY = NO", runtime
        )
        self.assertIn("CURRENT_TEST_VERIFIED_REFRESH_RESULT = YES", runtime)

        security = text(ROOT / "SECURITY.md")
        self.assertIn("For this public repository", security)
        self.assertNotIn("For a future public repository", security)

    def test_v414_stable_publication_uses_v414_immutable_installation_chain(self):
        changelog = text(ROOT / "CHANGELOG.md")
        security = text(ROOT / "SECURITY.md")
        public_installation = "\n".join(
            text(path)
            for path in (
                README,
                README_ZH,
                SETUP,
                ASSIST,
                ASSIST_ZH,
            )
        )

        self.assertIn("## v4.1.4 (published Stable release)", changelog)
        self.assertIn("## v4.1.4 Stable boundary", security)
        stable_docs = (
            changelog,
            security,
            text(ROOT / "ARCHITECTURE.md"),
            text(ROOT / "RUNTIME_TESTS.md"),
        )
        stable_evidence = "\n".join(stable_docs)
        for value in (
            V414_RUNTIME_SOURCE_COMMIT,
            V414_EXACT_CI_RUN,
            "366",
            "V414_FAKE_HOME_LIFECYCLE = PASS",
            "V414_UNINSTALL_TRANSACTION = PASS",
            "V414_REAL_GLOBAL_APPLY = NOT_RUN",
            "V414_FRESH_TASK_COMPATIBILITY = NOT_RUN",
            "V414_PUBLIC_RELEASE = STABLE",
            PINNED_SETUP_COMMIT,
            PINNED_ASSIST_COMMIT,
        ):
            self.assertIn(value, stable_evidence)
        self.assertIn(
            "`v4.1.4` is the current Stable release and default installation target.",
            security,
        )
        self.assertIn("releases/tag/v4.1.4", public_installation)
        self.assertIn("img.shields.io/badge/stable-v4.1.4", public_installation)
        self.assertIn("Stable release: `v4.1.4`", text(ASSIST))
        self.assertNotIn("releases/tag/v4.1.3", text(README) + text(README_ZH))
        self.assertNotIn("img.shields.io/badge/stable-v4.1.3", public_installation)
        stable_public_claims = "\n".join(
            (text(README), text(README_ZH), text(ROOT / "RUNTIME_TESTS.md"))
        ).lower()
        for unresolved in (
            "unreleased `v4.1.4`",
            "v4.1.4 candidate",
            "v4.1.4 not_established",
        ):
            self.assertNotIn(unresolved, stable_public_claims)
        self.assertIn("## v4.1.3 (published Stable release)", changelog)
        self.assertIn(V413_RUNTIME_SOURCE_COMMIT, stable_evidence)
        self.assertIn(V413_SETUP_CONTRACT_COMMIT, stable_evidence)
        self.assertIn(V413_ASSIST_CONTRACT_COMMIT, stable_evidence)

    def test_stable_setup_contract_pins_runtime_source_without_self_reference(self):
        architecture = text(ROOT / "ARCHITECTURE.md")
        security = text(ROOT / "SECURITY.md")
        runtime = text(ROOT / "RUNTIME_TESTS.md")
        changelog = text(ROOT / "CHANGELOG.md")
        setup = text(SETUP)
        readmes = text(README) + "\n" + text(README_ZH)

        for required in (
            "structured selection metadata boundary",
            "read-only health reader",
            "fail-soft",
            "single state authority",
        ):
            self.assertIn(required, architecture)
        for required in (
            "exact whitelist",
            "symbolic locations",
            "immutable commit",
            "no auto-updater",
        ):
            self.assertIn(required, security)
        for number in range(1, 11):
            self.assertRegex(setup, rf"(?m)^- O{number} .* — `PASS`[;.]$")
        self.assertIn("v4.1.4 (published Stable release)", changelog)
        self.assertIn("Source Commit A", changelog)
        for content in (architecture, security):
            self.assertIn(
                "`v4.1.4` is the current Stable release and default installation target.",
                content,
            )
        self.assertIn(
            "v4.1.4 — CURRENT STABLE RELEASE / DEFAULT INSTALLATION TARGET",
            architecture,
        )
        self.assertIn("Contract version: `v4.1.4`", setup)
        self.assertGreaterEqual(setup.count(V414_RUNTIME_SOURCE_COMMIT), 7)
        self.assertNotIn(RC6_SETUP_CONTRACT_COMMIT, setup)
        self.assertIn("`v4.1.3` remains the previous immutable Stable release", setup)
        self.assertIn("`v4.1.2`, `v4.1.1`, and `v4.1.0` remain older immutable Stable releases", setup)
        self.assertIn("`v4.1.0-rc6` remains an immutable historical Prerelease", setup)
        self.assertIn("`v4.1.0-rc5` is an older historical Preview", setup)
        self.assertIn(
            "`v4.1.4` is the Stable release target and default installation target",
            setup,
        )
        self.assertNotIn("RC6 is not tagged", setup)
        self.assertNotIn("RC6 is not published", setup)
        self.assertIn("No real Global v4.1.4 transaction result is claimed", setup)
        self.assertIn("Final O4/O9 re-certification", setup)
        self.assertIn(
            "only `sol-luna-v4/selector.py`",
            setup,
        )
        self.assertNotRegex(readmes, r"\bRC[3-6]\b")
        self.assertIn(
            "Install the pinned v4.1.4 Stable target",
            text(README),
        )
        self.assertIn(
            "安装固定的 v4.1.4 Stable 目标",
            text(README_ZH),
        )
        self.assertIn(f"checkout --detach {V414_RUNTIME_SOURCE_COMMIT}", setup)
        self.assertIn(
            f"Require `git rev-parse HEAD` to equal `{V414_RUNTIME_SOURCE_COMMIT}` exactly",
            setup,
        )
        installer_commands = [
            line
            for line in setup.splitlines()
            if "scripts/install.py" in line
            and ("--dry-run" in line or "--apply" in line)
        ]
        self.assertEqual(len(installer_commands), 4)
        for command in installer_commands:
            self.assertIn(f"--source-commit {V414_RUNTIME_SOURCE_COMMIT}", command)

        for placeholder in (
            "<APPROVED_40_HEX_COMMIT>",
            "<RC6_SOURCE_SHA>",
            "<STABLE_SOURCE_SHA>",
            "<TBD_SHA>",
            "PIN_PENDING",
            "<SETUP_COMMIT>",
            "<SETUP_COMMIT_SHA>",
            "SELF_SHA",
            "CURRENT_DOC_SHA",
        ):
            self.assertNotIn(placeholder, setup)
        self.assertNotRegex(
            setup,
            r"(?m)^(?:git|<PYTHON>)[^\n]*(?:\bmaster\b|\bmain\b|"
            r"origin/master|target_commitish)",
        )
        self.assertNotIn(
            "raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/master/",
            setup,
        )
        self.assertIn("a separate documentation anchor", setup)
        self.assertIn("not the runtime payload source", setup)
        self.assertIn("SETUP_CONTRACT_SELF_REFERENCE_REQUIRED = NO", setup)
        for placeholder in ("<source-sha>", "TBD", "TODO-for-release"):
            self.assertNotIn(placeholder, "\n".join((architecture, security, runtime, changelog)))

    def test_readme_status_guidance_is_bilingual_and_bounded(self):
        english = text(README)
        chinese = text(README_ZH)
        architecture = text(ROOT / "ARCHITECTURE.md")
        security = text(ROOT / "SECURITY.md")

        self.assertIn("## Confirm it is working", english)
        self.assertIn("## 如何确认生效", chinese)
        self.assertEqual(english.count("Check Sol/Luna status."), 1)
        self.assertEqual(chinese.count("检查 Sol/Luna 状态"), 1)
        for content in (english, chinese):
            self.assertIn("Status Healthy", content)
            self.assertIn("diagnostic schema 4", content)
            self.assertIn("Agents 10/10 Ready", content)
            self.assertIn("Skills 3/3 Ready", content)
            self.assertIn("Agents 5/5 Ready", content)
            self.assertNotIn("Native leaf Ready", content)
            self.assertIn("leaf_config Ready", content)
            self.assertIn("tool isolation", content)
            self.assertIn("invocation", content)
            self.assertIn("Luna-only", content)
            self.assertIn("RUNTIME_TESTS.md", content)
        self.assertIn("Diagnostic schema 4", architecture)
        self.assertIn("native_tool_isolation", architecture)
        self.assertIn("leaf_config=Ready", security)
        self.assertIn("adds no selector or network call", security)

    def test_setup_execution_urls_are_coordinated_and_immutable_when_pinned(self):
        english = text(README)
        chinese = text(README_ZH)
        combined = english + "\n" + chinese
        for content in (english, chinese):
            self.assertNotIn(RC5_STALE_SETUP_CONTRACT_COMMIT, content)
            self.assertNotIn(RC6_STALE_SETUP_CONTRACT_COMMIT, content)
        self.assertNotIn(
            "raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/master/"
            "CODEX_SOL_LUNA_SETUP.md",
            combined,
        )
        self.assertNotIn(
            "raw.githubusercontent.com/SuperDaddyV/codex-sol-luna-worker/master/"
            "CODEX_SOL_LUNA_INSTALL_ASSIST.md",
            combined,
        )

        english_shas = ASSIST_RAW_PATTERN.findall(english)
        chinese_shas = ASSIST_RAW_PATTERN.findall(chinese)
        self.assertEqual(len(english_shas), 1)
        self.assertEqual(len(chinese_shas), 1)
        self.assertEqual(english_shas, chinese_shas)
        self.assertNotIn(LEGACY_DEFAULT_SETUP_COMMIT, combined)
        self.assertEqual(
            english_shas,
            [PINNED_ASSIST_COMMIT],
        )
        self.assertNotIn(RC6_SETUP_CONTRACT_COMMIT, english_shas)
        for sha in english_shas:
            self.assertRegex(sha, r"^[0-9a-f]{40}$")

        self.assertEqual(SETUP_RAW_PATTERN.findall(english), [])
        self.assertEqual(SETUP_RAW_PATTERN.findall(chinese), [])
        self.assertEqual(
            SETUP_RAW_PATTERN.findall(text(ASSIST)),
            [V414_SETUP_CONTRACT_COMMIT],
        )

    def test_all_local_documentation_links_exist(self):
        for document in (
            README,
            README_ZH,
            PREVIEW,
            INSTALLATION,
            INSTALLATION_ZH,
            ASSIST,
            SETUP,
            ROOT / "SECURITY.md",
        ):
            for target in local_markdown_targets(text(document)):
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target).exists())

    def test_public_docs_contain_no_private_paths_runtime_ids_or_secrets(self):
        private_path = re.compile(
            r"(?:\b[A-Z]:\\" + "Users" + r"\\[^\s\\/:]+|"
            r"(?<![A-Za-z0-9_])/" + "Users" + r"/[^\s/]+|"
            r"(?<![A-Za-z0-9_])/" + "home" + r"/[^\s/]+)",
            re.I,
        )
        uuid_value = re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
            r"[0-9a-f]{4}-[0-9a-f]{12}\b",
            re.I,
        )
        labelled_runtime_id = re.compile(
            r"\b(?:session|child|installation|rollout)[_-]?id\b\s*[:=]\s*"
            r"[A-Za-z0-9][A-Za-z0-9._-]{7,}",
            re.I,
        )
        secrets = (
            re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
            re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
            re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----"),
        )
        for path in PUBLIC_DOCS:
            content = text(path)
            self.assertIsNone(private_path.search(content), path)
            self.assertIsNone(uuid_value.search(content), path)
            self.assertIsNone(labelled_runtime_id.search(content), path)
            for pattern in secrets:
                self.assertIsNone(pattern.search(content), path)

    def test_hooks_are_not_a_current_install_requirement(self):
        content = "\n".join(text(path) for path in (README, README_ZH, SETUP))
        stale_requirements = (
            re.compile(
                r"(?im)^(?![^\n]*\b(?:no|not|do not|does not|without)\b)"
                r"[^\n]*must install[^\n]*(?:Hook Router|PreToolUse)"
            ),
            re.compile(
                r"(?im)^(?![^\n]*\b(?:no|not|do not|does not|without)\b)"
                r"[^\n]*requires?[^\n]*(?:Hook Router|PreToolUse)"
            ),
            re.compile(
                r"(?im)^(?![^\n]*\b(?:no|not|do not|does not|without)\b)"
                r"[^\n]*(?:Hook Router|PreToolUse)[^\n]*is required"
            ),
        )
        for pattern in stale_requirements:
            self.assertIsNone(pattern.search(content))
        self.assertIn("without a Hook Router", text(README))
        self.assertIn("Do not install or introduce", text(SETUP))

    def test_setup_contract_orchestrates_real_cli(self):
        content = text(SETUP)
        for command in (
            "scripts/install.py --dry-run --codex-home <CODEX_HOME> "
            f"--source-commit {V414_RUNTIME_SOURCE_COMMIT}",
            "scripts/install.py --apply --codex-home <CODEX_HOME> "
            f"--source-commit {V414_RUNTIME_SOURCE_COMMIT}",
            "scripts/install.py --apply --migrate-v3 --codex-home <CODEX_HOME> "
            f"--source-commit {V414_RUNTIME_SOURCE_COMMIT}",
            "scripts/install.py --rollback <BACKUP_PATH> --codex-home <CODEX_HOME>",
            "scripts/install.py --uninstall --codex-home <CODEX_HOME>",
        ):
            self.assertIn(command, content)
        self.assertIn("Python 3.11 or newer", content)
        self.assertIn("INSTALL_RUNTIME_PASS", content)
        self.assertIn("Fresh Session Requirement", content)
        for required in (
            "--print-selection",
            "--status-json",
            "Luna ref-cost ↓X.X%",
            "LKG",
            "capability <source_effort>→<selected_effort>",
            "STATUS_NETWORK = 0",
            "STATUS_SELECTOR_LOCK = 0",
            "STATUS_STATE_WRITES = 0",
            "STATUS_LUNA_SPAWN = 0",
            "Healthy / TODAY_SELECTION_NOT_INITIALIZED",
            "Unavailable / DAILY_PROFILE_INVALID",
            "Misconfigured / DAILY_PROFILE_READ_FAILED",
            "OLD_SAME_DAY_PROFILE_FORCE_REFRESH = NO",
            "STATE_MIGRATION_REQUIRED = NO",
            "Upgrade to the Latest Published Version",
        ):
            self.assertIn(required, content)
        self.assertNotIn("--validation-sandbox --codex-home <CODEX_HOME>", content)

    def test_v414_stable_boundary_is_explicit_and_published(self):
        architecture = text(ROOT / "ARCHITECTURE.md")
        changelog = text(ROOT / "CHANGELOG.md")
        security = text(ROOT / "SECURITY.md")
        runtime = text(ROOT / "RUNTIME_TESTS.md")
        setup = text(SETUP)
        combined = "\n".join((architecture, changelog, security, runtime, setup))

        self.assertIn(
            "v4.1.4 — CURRENT STABLE RELEASE / DEFAULT INSTALLATION TARGET",
            architecture,
        )
        self.assertIn("## v4.1.4 (published Stable release)", changelog)
        self.assertIn("## v4.1.4 Stable boundary", security)
        self.assertIn("schemas `1.0` and `1.1`", combined)
        self.assertIn("`rankings` backend axis", architecture)
        self.assertIn("`overallRankings`, `overallBatch`", architecture)
        self.assertIn("v4.1.3-to-v4.1.4", changelog)
        self.assertIn(
            "v4.1.3 — PREVIOUS IMMUTABLE STABLE",
            architecture,
        )
        self.assertIn("Setup and Assisted", architecture)
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, combined)
        self.assertIn(V414_EXACT_CI_RUN, combined)
        self.assertIn("366", combined)
        self.assertRegex(security, r"[Nn]o real Global\s+v4\.1\.4 installer apply")
        self.assertIn("Contract version: `v4.1.4`", setup)
        self.assertIn("V414_PUBLIC_RELEASE = STABLE", runtime)
        self.assertIn("V414_UNINSTALL_TRANSACTION = PASS", runtime)
        self.assertIn(V414_RELEASE_ASSIST_CONTRACT_COMMIT, combined)
        self.assertIn(PINNED_ASSIST_COMMIT, combined)
        self.assertIn("`v4.1.3` remains the previous immutable", text(ASSIST))
        self.assertIn("`v4.1.2`, `v4.1.1`, and `v4.1.0` remain older", text(ASSIST))
        self.assertIn("`v4.1.3` 继续作为上一版不可变 Stable", text(ASSIST_ZH))
        self.assertNotIn("`v4.1.2` 继续作为上一版", text(ASSIST_ZH))
        self.assertNotRegex(combined, r"v4\.1\.2[^\n]*previous .*Stable")
        self.assertNotRegex(combined, r"v4\.1\.1[^\n]*previous .*Stable")
        self.assertNotIn("v4.1.4 — UNRELEASED CANDIDATE", combined)
        self.assertNotIn("## v4.1.4 (unreleased candidate)", combined)


if __name__ == "__main__":
    unittest.main()

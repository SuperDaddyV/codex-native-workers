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
STABLE_SETUP = ROOT / "NATIVE_WORKERS_SETUP.md"
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
    STABLE_SETUP,
    ROOT / "ARCHITECTURE.md",
    ROOT / "RUNTIME_TESTS.md",
    ROOT / "SECURITY.md",
    ROOT / "CHANGELOG.md",
    ROOT / "VERSIONS.md",
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
SETUP_RAW_PATTERN = re.compile(
    r"https://raw\.githubusercontent\.com/"
    r"SuperDaddyV/codex-sol-luna-worker/([0-9a-f]{40})/"
    r"CODEX_SOL_LUNA_SETUP\.md"
)
STABLE_API_URL = (
    "https://api.github.com/repos/SuperDaddyV/"
    "codex-native-workers/releases/tags/v4.3.0"
)
STABLE_RELEASE_URL = (
    "https://github.com/SuperDaddyV/codex-native-workers/releases/tag/v4.3.0"
)
STABLE_PYTHON_CHECK = (
    'python -c "import sys, tomllib; '
    'assert sys.version_info >= (3, 11); print(sys.version)"'
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
        for home, other, guide in ((README, README_ZH, INSTALLATION), (README_ZH, README, INSTALLATION_ZH)):
            for destination in (other, guide, STABLE_SETUP, ROOT / 'VERSIONS.md'):
                self.assertIn('](' + destination.name + ')', text(home))
        history = text(ROOT / 'VERSIONS.md')
        for value in (PINNED_ASSIST_BLOB_URL, PINNED_SETUP_BLOB_URL, V414_RUNTIME_SOURCE_COMMIT, RC1_RUNTIME_SOURCE_COMMIT):
            self.assertIn(value, history)


    def test_homepages_are_concise_and_installation_is_easy_to_find(self):
        for home, headings in ((README, ('What it does','Install or upgrade','Daily use','Check that it works','Common questions','More information')), (README_ZH, ('有什么用','安装或升级','日常怎么用','如何确认生效','常见问题','更多信息'))):
            content = text(home)
            self.assertEqual(re.findall(r'(?m)^## (.+)$', content), list(headings))
            self.assertLessEqual(len(content.splitlines()), 110)
            self.assertIn('actions/workflows/validate.yml/badge.svg', content)
            self.assertIn('github/license', content)
            self.assertIn('VERSIONS.md', content)
            self.assertIn('v4.3.0', content)
            self.assertNotRegex(content, r'\b[0-9a-f]{40}\b')
            self.assertEqual(content.count('```') % 2, 0)


    def test_readmes_explain_native_worker_routing_parallelism_and_receipts(self):
        for path in (README, README_ZH):
            content = text(path)
            for token in ('Coordinator','GPT-6 Sol','GPT-6 Luna','0–3','4–6','2 KiB','sol-luna-delegate','sol-luna-status','sol-luna-upgrade','Coordinator/Workers: delegated · sol_high ×1 · luna_high ×1 · parallel'):
                self.assertIn(token, content)
        self.assertIn('You choose the model', text(README))
        self.assertIn('主模型由你选择', text(README_ZH))
        self.assertIn('no fixed Sol quota', text(README))
        self.assertIn('Sol 没有固定配额', text(README_ZH))


    def test_historical_preview_keeps_immutable_contract_and_limitations(self):
        history = text(ROOT / 'VERSIONS.md')
        self.assertIn('v4.2.0-rc1', history)
        self.assertIn(RC1_RUNTIME_SOURCE_COMMIT + '/NATIVE_WORKERS_PREVIEW.md', history)
        self.assertIn('native-workers-rc1-validation.json', history)
        for required in ('published, non-draft GitHub','TAG_MOVED','Strong prevention of recursive worker delegation'):
            self.assertIn(required, text(PREVIEW))
        self.assertIn('Strict recursive isolation is unsupported', text(ROOT / 'SECURITY.md'))


    def test_readmes_bound_runtime_and_savings_claims(self):
        for token in ('six-worker capacity is unverified','does not guarantee host-enforced recursive isolation','do not establish local performance or guarantee quota savings'):
            self.assertIn(token, text(README))
        for token in ('六 worker 容量未验证','不提供宿主强制递归隔离保证','不保证节省额度'):
            self.assertIn(token, text(README_ZH))
        historical = text(ROOT / 'RUNTIME_TESTS.md')
        for token in ('FAIL','NOT RUN','UNKNOWN'):
            self.assertIn(token, historical)


    def test_installation_entry_supports_each_client_and_platform(self):
        for path in (README,README_ZH,INSTALLATION,INSTALLATION_ZH):
            content=text(path)
            for token in ('Windows','macOS','CLI','python3','python','Git','WSL'):
                self.assertIn(token,content)
        for path in (INSTALLATION,INSTALLATION_ZH):
            for token in (STABLE_PYTHON_CHECK, STABLE_PYTHON_CHECK.replace('python ', 'python3 '), '--client desktop', '--client cli'):
                self.assertIn(token,text(path))


    def test_installation_help_covers_actual_launcher_roots_and_recovery(self):
        for guide in (INSTALLATION,INSTALLATION_ZH):
            content=text(guide)
            for token in ('CODEX_HOME','<SKILLS_ROOT>','AGENTS.override.md','OWNERSHIP_CONFLICT','IDEMPOTENT_PASS','Today Selection not initialized','Not checked','--source-commit','scripts/install_assist.py','PATH','404','hash','NATIVE_WORKERS_SETUP.md#assistance-and-recovery'):
                self.assertIn(token,content)
        self.assertIn('not native installation proof on all platforms',text(INSTALLATION))
        self.assertIn('不是用户安装成功率统计',text(INSTALLATION_ZH))
        contract=text(STABLE_SETUP)
        for token in ('at most three','normally launched client','smallest user action','resume prompt','not user authorization','capability `NOT_CHECKED`'):
            self.assertIn(token,contract)


    def test_single_prompt_follows_verified_current_release_contract(self):
        for path in (README, README_ZH):
            prompts=re.findall(r'```text\n(.*?)\n```',text(path),re.S)
            install=[value for value in prompts if STABLE_API_URL in value]
            self.assertEqual(len(install),1)
            for token in ('NATIVE_WORKERS_SETUP.md','commit','dry-run','CODEX_HOME'):
                self.assertIn(token,install[0])
            self.assertNotRegex(install[0],r'\b[0-9a-f]{40}\b')
        self.assertIn('immutable tag',text(README))
        self.assertIn('不可变 tag',text(README_ZH))
        for token in (PINNED_ASSIST_BLOB_URL,PINNED_SETUP_BLOB_URL,V414_RUNTIME_SOURCE_COMMIT):
            self.assertIn(token,text(ROOT/'VERSIONS.md'))


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
                self.assertIn("Current Stable (v4.3.0)", content)
                self.assertIn("Previous Stable (v4.2.0)", content)
                self.assertIn("Previous Preview (v4.2.0-rc1)", content)
                self.assertIn("Legacy Stable (v4.1.4)", content)
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
        self.assertIn("placeholder: v4.3.0", bug)
        self.assertNotIn("placeholder: v4.1.1", bug)
        self.assertIn("`Sol/Luna: Sol-only · no independent bounded work`", bug)
        self.assertIn("`Sol/Luna: delegated · luna_max ×2 · parallel`", bug)
        self.assertIn("`No Receipt`", bug)
        self.assertIn("Coordinator/Workers: delegated · sol_high ×1", bug)
        self.assertIn("v4.1.4 legacy format", bug)
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
        self.assertIn("placeholder: v4.3.0 / v4.2.0 / Unknown", compatibility)
        self.assertIn("placeholder: sol_max / Unknown", compatibility)
        self.assertIn("Coordinator/Workers: delegated", compatibility)
        self.assertIn("sequential execution is not parallel", compatibility)
        self.assertIn("placeholder: v4.3.0", compatibility)
        self.assertNotIn("placeholder: v4.1.1", compatibility)

        feature = text(ISSUE_TEMPLATE_DIR / "feature-feedback.yml")
        self.assertIn("name: Feature request / feedback", feature)
        self.assertIn("Non-guarantee notice", feature)
        for option in (
            "Feature request", "Documentation", "UX / usability",
            "Installation experience", "Delegation behavior", "Other",
        ):
            self.assertIn(f"- {option}", feature)

        for path in (README,README_ZH):
            for filename in ('bug-report.yml','compatibility-report.yml','feature-feedback.yml'):
                self.assertIn('issues/new?template='+filename,text(path))
            self.assertIn('CODEX_HOME',text(path))


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
                STABLE_SETUP,
                ROOT / "ARCHITECTURE.md",
                ROOT / "SECURITY.md",
            )
        )
        for path in (README, README_ZH):
            for link in ('NATIVE_WORKERS_SETUP.md','VERSIONS.md','ARCHITECTURE.md','RUNTIME_TESTS.md','SECURITY.md','CHANGELOG.md'):
                self.assertIn(link,text(path))

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
        for value in (PINNED_ASSIST_COMMIT,PINNED_SETUP_COMMIT):
            self.assertIn(value,text(ROOT/'VERSIONS.md'))
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
        historical_readmes = [text(ROOT / 'VERSIONS.md')]
        public_installation = "\n".join(
            historical_readmes
            + [
                text(SETUP),
                text(ASSIST),
                text(ASSIST_ZH),
            ]
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
        self.assertIn(PINNED_ASSIST_BLOB_URL, public_installation)
        self.assertIn(PINNED_SETUP_BLOB_URL, public_installation)
        self.assertIn(V414_RUNTIME_SOURCE_COMMIT, public_installation)
        self.assertIn("Stable release: `v4.1.4`", text(ASSIST))
        self.assertIn(STABLE_API_URL, text(README) + text(README_ZH))
        self.assertIn("v4.3.0", text(README) + text(README_ZH))
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
        setup = text(STABLE_SETUP)
        readmes = text(README) + "\n" + text(README_ZH)

        self.assertIn("# Codex Native Workers — v4.3.0 Stable installation contract", setup)
        for required in (
            "/repos/SuperDaddyV/codex-native-workers/releases/tags/v4.3.0",
            "draft=false",
            "prerelease=false",
            "published_at",
            "40-hex commit",
            "clean detached checkout",
            "remote tag again",
            "TAG_MOVED",
            'VERSION == "v4.3.0"',
            "--source-commit",
            "two-root transaction",
            "no file is\n   required to embed its own SHA",
        ):
            self.assertIn(required, setup)
        self.assertNotRegex(setup, r"\b[0-9a-f]{40}\b")
        self.assertIn("Stable does not mean", setup)
        self.assertIn("Strong recursive isolation is unsupported", setup)
        self.assertIn(
            "Installation can be complete while a native check is NOT RUN",
            " ".join(setup.split()),
        )

        for content in (text(README), text(README_ZH)):
            prompts = re.findall(r"```text\n(.*?)\n```", content, re.S)
            stable = [prompt for prompt in prompts if STABLE_API_URL in prompt]
            self.assertEqual(len(stable), 1)
            self.assertIn(STABLE_PYTHON_CHECK, text(STABLE_SETUP))
            self.assertNotRegex(stable[0], r"\b[0-9a-f]{40}\b")

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
        self.assertIn("v4.2.0", changelog)
        self.assertIn("immutable source verification", changelog)
        self.assertIn("v4.2.0 Stable product contract", architecture)
        self.assertIn("v4.2 Stable scope", security)
        self.assertNotRegex(readmes, r"\bRC[3-6]\b")
        installer_commands = [
            line
            for line in setup.splitlines()
            if "scripts/install.py" in line
            and ("--dry-run" in line or "--apply" in line)
        ]
        self.assertEqual(len(installer_commands), 2)
        for command in installer_commands:
            self.assertIn("--source-commit <VERIFIED_40_HEX_COMMIT>", command)

        for placeholder in (
            "<APPROVED_40_HEX_COMMIT>",
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
            r"(?m)^(?:git|python)[^\n]*\b(?:master|main)\b",
        )
        self.assertNotIn(
            "raw.githubusercontent.com/",
            setup,
        )
        for placeholder in ("<source-sha>", "TBD", "TODO-for-release"):
            self.assertNotIn(placeholder, "\n".join((architecture, security, runtime, changelog)))

    def test_legacy_v414_setup_contract_integrity_guards_remain_explicit(self):
        setup = text(SETUP)
        architecture = text(ROOT / "ARCHITECTURE.md")
        security = text(ROOT / "SECURITY.md")

        for number in range(1, 11):
            self.assertRegex(setup, rf"(?m)^- O{number} .* — `PASS`[;.]$")
        for required in (
            "Contract version: `v4.1.4`",
            "`v4.1.4` is the Stable release target and default installation target",
            "`v4.1.3` remains the previous immutable Stable release",
            "`v4.1.2`, `v4.1.1`, and `v4.1.0` remain older immutable Stable releases",
            "`v4.1.0-rc6` remains an immutable historical Prerelease",
            "`v4.1.0-rc5` is an older historical Preview",
            "No real Global v4.1.4 transaction result is claimed",
            "Final O4/O9 re-certification",
            "only `sol-luna-v4/selector.py`",
            "a separate documentation anchor",
            "not the runtime payload source",
            "SETUP_CONTRACT_SELF_REFERENCE_REQUIRED = NO",
            f"checkout --detach {V414_RUNTIME_SOURCE_COMMIT}",
            f"Require `git rev-parse HEAD` to equal `{V414_RUNTIME_SOURCE_COMMIT}` exactly",
        ):
            self.assertIn(required, setup)
        self.assertGreaterEqual(setup.count(V414_RUNTIME_SOURCE_COMMIT), 7)
        self.assertNotIn(RC6_SETUP_CONTRACT_COMMIT, setup)
        self.assertNotIn("RC6 is not tagged", setup)
        self.assertNotIn("RC6 is not published", setup)

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
        self.assertIn(
            "`v4.1.4` is the current Stable release and default installation target.",
            architecture,
        )
        self.assertIn(
            "`v4.1.4` is the current Stable release and default installation target.",
            security,
        )

    def test_readme_status_guidance_is_bilingual_and_bounded(self):
        for path in (README,README_ZH):
            for token in ('10/10','3/3','Today Selection not initialized','Not checked','RUNTIME_TESTS.md'):
                self.assertIn(token,text(path))
        self.assertIn('Healthy configuration is not runtime acceptance',text(README))
        self.assertIn('配置健康不等于运行验收通过',text(README_ZH))
        self.assertIn('native_tool_isolation',text(ROOT/'ARCHITECTURE.md'))
        self.assertIn('adds no selector or network call',text(ROOT/'SECURITY.md'))


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

        for content in (english, chinese):
            prompts = re.findall(r"```text\n(.*?)\n```", content, re.S)
            stable = [prompt for prompt in prompts if STABLE_API_URL in prompt]
            self.assertEqual(len(stable), 1)
            self.assertIn(STABLE_PYTHON_CHECK, text(STABLE_SETUP))
            self.assertIn("NATIVE_WORKERS_SETUP.md", stable[0])
            self.assertNotRegex(stable[0], r"\b[0-9a-f]{40}\b")
        self.assertNotIn(LEGACY_DEFAULT_SETUP_COMMIT, combined)

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
            STABLE_SETUP,
            ROOT / "SECURITY.md",
            ROOT / "VERSIONS.md",
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
        self.assertIn("not a custom orchestration engine", text(ROOT / "ARCHITECTURE.md"))
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

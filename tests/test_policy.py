import unittest
from pathlib import Path


POLICY = (Path(__file__).resolve().parents[1] / "AGENTS.md").read_text(
    encoding="utf-8"
)
NORMALIZED_POLICY = " ".join(POLICY.split())


class PolicyTests(unittest.TestCase):
    def test_repository_policy_is_a_development_only_delta(self):
        self.assertIn("Repository development rules", POLICY)
        self.assertIn("currently installed Global policy", POLICY)
        self.assertIn("Codex Native Workers", POLICY)
        self.assertIn("candidate concurrency is not runtime proof", NORMALIZED_POLICY)
        self.assertIn("The Coordinator owns scope, architecture and final acceptance.", NORMALIZED_POLICY)
        for deployment_detail in (
            "sol-luna-delegate",
            "--workers",
            "sol_low",
            "luna_low",
        ):
            with self.subTest(detail=deployment_detail):
                self.assertNotIn(deployment_detail, NORMALIZED_POLICY)

    def test_project_rules_preserve_protected_runtime_and_git_boundaries(self):
        for boundary in (
            "Real",
            "explicit authorization",
            "Git mutations",
            "historical evidence",
            "Keep implementation, tests and documentation inside this repository",
            "full prevalidation of rollback",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, NORMALIZED_POLICY)


if __name__ == "__main__":
    unittest.main()

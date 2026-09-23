import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / ".codex" / "agents"
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
MODELS = {"sol": "gpt-6-sol", "luna": "gpt-6-luna"}


class AgentConfigTests(unittest.TestCase):
    def test_exactly_five_fixed_effort_profiles_per_family(self):
        configs = {
            path.name: tomllib.loads(path.read_text(encoding="utf-8"))
            for path in AGENT_DIR.glob("*.toml")
        }
        self.assertEqual(len(configs), 10)
        for family, model in MODELS.items():
            seen_efforts = set()
            for effort in sorted(EFFORTS):
                filename = f"{family}-{effort}.toml"
                self.assertIn(filename, configs)
                config = configs[filename]
                role = f"{family}_{effort}"
                with self.subTest(role=role):
                    self.assertEqual(config["name"], role)
                    self.assertEqual(config["model"], model)
                    self.assertEqual(config["model_reasoning_effort"], effort)
                    self.assertNotEqual(config["model_reasoning_effort"], "ultra")
                    self.assertTrue(config["description"].strip())
                    instructions = config["developer_instructions"]
                    self.assertIn("bounded task assigned by the parent Coordinator", instructions)
                    self.assertIn("Do not expand scope", instructions)
                    self.assertIn("Do not spawn, organize, or delegate", instructions)
                    self.assertFalse(config["agents"]["enabled"])
                    seen_efforts.add(config["model_reasoning_effort"])
            self.assertEqual(seen_efforts, EFFORTS)

    def test_coordinator_model_remains_session_selected_and_capacity_is_a_ceiling(self):
        with (ROOT / ".codex" / "config.toml").open("rb") as handle:
            config = tomllib.load(handle)
        agents = config["agents"]
        self.assertTrue(agents["enabled"])
        self.assertEqual(agents["max_concurrent_threads_per_session"], 6)
        self.assertNotIn("default_subagent_model", agents)
        self.assertNotIn("default_subagent_reasoning_effort", agents)


if __name__ == "__main__":
    unittest.main()

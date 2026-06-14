import unittest
from unittest import mock

from aiku.agents.orchestrator import AutonomousOrchestrator, ExecutionEngine


class TestExecutionEngine(unittest.TestCase):
    def test_no_match_returns_none(self):
        self.assertIsNone(ExecutionEngine.execute_action("just some text"))

    def test_write_requires_pipe(self):
        out = ExecutionEngine.execute_action("ACTION: WRITE ARGS: only-path-no-pipe")
        self.assertIn("expects", out)

    def test_image_action(self):
        out = ExecutionEngine.execute_action("ACTION: IMAGE ARGS: a sunset")
        self.assertIn("image.pollinations.ai", out)

    def test_unknown_action(self):
        out = ExecutionEngine.execute_action("ACTION: FLYTOMARS ARGS: now")
        self.assertIn("Unknown action", out)


class FakeMemory:
    def __init__(self):
        self.saved = []

    def query_memory(self, *a, **k):
        return []

    def add_memory(self, text):
        self.saved.append(text)
        return "ok"


class TestOrchestrator(unittest.TestCase):
    def test_run_task_finishes(self):
        orch = AutonomousOrchestrator()
        fake_mem = FakeMemory()
        with mock.patch("aiku.agents.orchestrator.memory_instance", fake_mem), \
             mock.patch.object(orch, "call_llm") as call_llm:
            call_llm.side_effect = [
                "1. do thing",  # plan
                "ACTION: FINISH ARGS: All done successfully.",  # first iteration
            ]
            result = orch.run_task("test task")
            self.assertEqual(result, "All done successfully.")
            self.assertTrue(fake_mem.saved)

    def test_run_task_finish_without_args(self):
        orch = AutonomousOrchestrator()
        with mock.patch("aiku.agents.orchestrator.memory_instance", FakeMemory()), \
             mock.patch.object(orch, "call_llm") as call_llm:
            call_llm.side_effect = ["plan", "I think we should FINISH here"]
            result = orch.run_task("t")
            self.assertIn("FINISH", result)


if __name__ == "__main__":
    unittest.main()

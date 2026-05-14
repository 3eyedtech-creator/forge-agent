import unittest
from pathlib import Path

from forge_agent.approval_mode import ApprovalMode
from forge_agent.terminal_ui import build_ready_text


class TerminalUiTests(unittest.TestCase):
    def test_ready_text_includes_workspace_models_and_mode(self) -> None:
        output = build_ready_text(
            Path("D:/work"),
            fast_model="fast",
            reasoning_model="reasoning",
            approval_mode=ApprovalMode.AUTO,
        )

        self.assertIn("Workspace:", output)
        self.assertIn("work", output)
        self.assertIn("Fast model: fast", output)
        self.assertIn("Reasoning model: reasoning", output)
        self.assertIn("Approval mode: auto", output)
        self.assertIn("/mode auto", output)


if __name__ == "__main__":
    unittest.main()

import unittest

from policy_engine import PolicyDecision, decide_shell_command


class PolicyEngineTests(unittest.TestCase):
    def test_allows_safe_read_only_shell_commands(self) -> None:
        decision = decide_shell_command("git status")

        self.assertEqual(decision, PolicyDecision.ALLOW)

    def test_blocks_destructive_shell_commands(self) -> None:
        decision = decide_shell_command("git reset --hard")

        self.assertEqual(decision, PolicyDecision.BLOCK)

    def test_requires_approval_for_other_shell_commands(self) -> None:
        decision = decide_shell_command("pip install rich")

        self.assertEqual(decision, PolicyDecision.REQUIRE_APPROVAL)


if __name__ == "__main__":
    unittest.main()

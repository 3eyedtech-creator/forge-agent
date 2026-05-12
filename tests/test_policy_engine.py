import unittest

from forge_agent.policy_engine import ApprovalResponse, PolicyDecision, decide_shell_command, resolve_policy_decision


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

    def test_approved_action_is_allowed(self) -> None:
        decision = resolve_policy_decision(PolicyDecision.REQUIRE_APPROVAL, ApprovalResponse.APPROVE)

        self.assertEqual(decision, PolicyDecision.ALLOW)

    def test_denied_action_is_blocked(self) -> None:
        decision = resolve_policy_decision(PolicyDecision.REQUIRE_APPROVAL, ApprovalResponse.DENY)

        self.assertEqual(decision, PolicyDecision.BLOCK)

    def test_blocked_action_stays_blocked_even_if_approved(self) -> None:
        decision = resolve_policy_decision(PolicyDecision.BLOCK, ApprovalResponse.APPROVE)

        self.assertEqual(decision, PolicyDecision.BLOCK)


if __name__ == "__main__":
    unittest.main()

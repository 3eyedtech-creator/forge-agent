import unittest

from forge_agent.approval_mode import ApprovalMode, build_interrupt_policy, parse_approval_mode


class ApprovalModeTests(unittest.TestCase):
    def test_parse_approval_mode_accepts_manual_and_auto(self) -> None:
        self.assertEqual(parse_approval_mode("manual"), ApprovalMode.MANUAL)
        self.assertEqual(parse_approval_mode("auto"), ApprovalMode.AUTO)

    def test_parse_approval_mode_rejects_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            parse_approval_mode("dangerous")

    def test_manual_policy_requires_review_for_file_mutations(self) -> None:
        policy = build_interrupt_policy(ApprovalMode.MANUAL)

        self.assertEqual(policy["create_workspace_file"], {"allowed_decisions": ["approve", "reject"]})
        self.assertEqual(policy["write_workspace_file"], {"allowed_decisions": ["approve", "reject"]})
        self.assertEqual(policy["edit_workspace_file"], {"allowed_decisions": ["approve", "reject"]})

    def test_auto_policy_skips_review_for_file_mutations(self) -> None:
        policy = build_interrupt_policy(ApprovalMode.AUTO)

        self.assertFalse(policy["create_workspace_file"])
        self.assertFalse(policy["write_workspace_file"])
        self.assertFalse(policy["edit_workspace_file"])


if __name__ == "__main__":
    unittest.main()

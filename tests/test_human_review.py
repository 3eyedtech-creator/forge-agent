import unittest

from forge_agent.human_review import decisions_from_approvals, has_rejection


class HumanReviewTests(unittest.TestCase):
    def test_builds_approve_and_reject_decisions(self) -> None:
        decisions = decisions_from_approvals([True, False])

        self.assertEqual(
            decisions,
            [
                {"type": "approve"},
                {"type": "reject", "message": "User rejected this tool call."},
            ],
        )

    def test_detects_rejection(self) -> None:
        decisions = [{"type": "approve"}, {"type": "reject", "message": "No"}]

        self.assertTrue(has_rejection(decisions))

    def test_detects_no_rejection(self) -> None:
        decisions = [{"type": "approve"}]

        self.assertFalse(has_rejection(decisions))


if __name__ == "__main__":
    unittest.main()

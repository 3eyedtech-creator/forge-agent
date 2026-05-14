import unittest

from forge_agent.human_review import decisions_from_approvals, format_action_arguments, has_rejection


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

    def test_formats_file_write_arguments_without_full_content(self) -> None:
        output = format_action_arguments(
            "write_workspace_file",
            {"path": "app.py", "content": "line 1\nline 2"},
        )

        self.assertIn("Path: app.py", output)
        self.assertIn("Content: 2 lines, 13 characters", output)
        self.assertNotIn("line 1", output)

    def test_formats_file_edit_arguments_without_full_text(self) -> None:
        output = format_action_arguments(
            "edit_workspace_file",
            {"path": "app.py", "old_text": "old\ntext", "new_text": "new text"},
        )

        self.assertIn("Path: app.py", output)
        self.assertIn("Old text: 2 lines, 8 characters", output)
        self.assertIn("New text: 1 line, 8 characters", output)
        self.assertNotIn("old\ntext", output)

    def test_formats_non_file_arguments_normally(self) -> None:
        output = format_action_arguments("search_workspace_text", {"query": "login"})

        self.assertEqual(output, "Arguments: {'query': 'login'}")


if __name__ == "__main__":
    unittest.main()

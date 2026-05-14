import unittest

from forge_agent.task_report import format_task_report


class TaskReportTests(unittest.TestCase):
    def test_formats_empty_task_report(self) -> None:
        output = format_task_report(changed_files=[], commands_run=[], risks=[])

        self.assertIn("Summary", output)
        self.assertIn("No file changes recorded.", output)
        self.assertIn("No terminal commands recorded.", output)
        self.assertIn("Verification not recorded yet.", output)

    def test_formats_changed_files_commands_and_risks(self) -> None:
        output = format_task_report(
            changed_files=[
                {"path": "app.py", "action": "edited"},
                {"path": "README.md", "action": "created"},
            ],
            commands_run=[
                {"command": "python -m unittest", "exit_code": 0},
                {"command": "pytest", "exit_code": 1},
            ],
            risks=["Tests failed before final verification."],
        )

        self.assertIn("edited: app.py", output)
        self.assertIn("created: README.md", output)
        self.assertIn("python -m unittest (exit 0)", output)
        self.assertIn("pytest (exit 1)", output)
        self.assertIn("Tests failed before final verification.", output)


if __name__ == "__main__":
    unittest.main()

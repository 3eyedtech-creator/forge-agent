import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.policy_engine import ApprovalResponse
from forge_agent.shell_command_tool import ShellCommandError, run_shell_command


class ShellCommandToolTests(unittest.TestCase):
    def test_runs_allowed_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_shell_command(Path(temp_dir), "git status")

        self.assertEqual(result.command, "git status")
        self.assertIn("not a git repository", result.stderr.lower())

    def test_blocks_destructive_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(ShellCommandError):
                run_shell_command(Path(temp_dir), "git reset --hard", approval=ApprovalResponse.APPROVE)

    def test_requires_approval_for_risky_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(ShellCommandError):
                run_shell_command(Path(temp_dir), "echo hello")

    def test_runs_approved_risky_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_shell_command(Path(temp_dir), "echo hello", approval=ApprovalResponse.APPROVE)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("hello", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()

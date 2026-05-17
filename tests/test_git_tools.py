import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.git_tools import (
    run_git_add,
    run_git_branch,
    run_git_commit,
    run_git_diff,
    run_git_log,
    run_git_status,
)


class GitToolsTests(unittest.TestCase):
    def test_git_status_returns_command_output(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))

            output = run_git_status(workspace)

        self.assertIn("Command: git status --short", output)
        self.assertIn("Exit code: 0", output)

    def test_git_diff_returns_command_output(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))
            (workspace / "app.py").write_text("print('changed')\n", encoding="utf-8")

            output = run_git_diff(workspace)

        self.assertIn("Command: git diff", output)
        self.assertIn("print('changed')", output)

    def test_git_branch_returns_current_branch(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))

            output = run_git_branch(workspace)

        self.assertIn("Command: git branch --show-current", output)
        self.assertIn("Exit code: 0", output)

    def test_git_log_returns_recent_commits(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))

            output = run_git_log(workspace)

        self.assertIn("Command: git log --oneline -5", output)
        self.assertIn("initial commit", output)

    def test_git_add_and_commit_run_successfully(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))
            (workspace / "notes.txt").write_text("notes\n", encoding="utf-8")

            add_output = run_git_add(workspace, "notes.txt")
            commit_output = run_git_commit(workspace, "add notes")

        self.assertIn("Command: git add -- notes.txt", add_output)
        self.assertIn("Exit code: 0", add_output)
        self.assertIn("Command: git commit -m add notes", commit_output)
        self.assertIn("Exit code: 0", commit_output)


def init_git_repo(workspace: Path) -> Path:
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "forge@example.com"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Forge Tests"], cwd=workspace, check=True)
    (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=workspace, check=True, capture_output=True, text=True)
    return workspace


if __name__ == "__main__":
    unittest.main()

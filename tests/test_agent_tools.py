import unittest
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.agent_tools import (
    build_tools,
    run_git_branch_tool,
    run_git_diff_tool,
    run_git_log_tool,
    run_git_status_tool,
    run_create_file_tool,
    run_edit_file_tool,
    run_list_files_tool,
    run_read_file_tool,
    run_retrieve_memories_tool,
    run_retrieve_context_tool,
    run_python_sandbox_tool,
    run_terminal_command_tool,
    run_search_text_tool,
    run_write_file_tool,
)


class AgentToolsTests(unittest.TestCase):
    def test_list_files_tool_returns_readable_file_list(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("", encoding="utf-8")
            (workspace / "README.md").write_text("", encoding="utf-8")

            output = run_list_files_tool(workspace)

        self.assertEqual(output, "README.md\nagent.py")

    def test_read_file_tool_returns_line_numbered_content(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("print('hello')\n", encoding="utf-8")

            output = run_read_file_tool(workspace, "agent.py")

        self.assertEqual(output, "1: print('hello')")

    def test_search_text_tool_returns_readable_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("print('hello')\n", encoding="utf-8")

            output = run_search_text_tool(workspace, "hello")

        self.assertEqual(output, "agent.py:1: print('hello')")

    def test_create_file_tool_returns_success_message(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            output = run_create_file_tool(workspace, "notes.txt", "hello")

            self.assertEqual((workspace / "notes.txt").read_text(encoding="utf-8"), "hello")
        self.assertEqual(output, "File created: notes.txt")

    def test_write_file_tool_returns_success_message(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("old", encoding="utf-8")

            output = run_write_file_tool(workspace, "notes.txt", "new")

            self.assertEqual((workspace / "notes.txt").read_text(encoding="utf-8"), "new")
        self.assertEqual(output, "File written: notes.txt")

    def test_write_file_tool_returns_error_message_for_missing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            output = run_write_file_tool(workspace, "backend/requirements.txt", "fastapi")

        self.assertEqual(output, "File write failed: File does not exist: backend/requirements.txt")

    def test_langchain_write_file_tool_returns_error_message_for_missing_file(self) -> None:
        if importlib.util.find_spec("langchain") is None:
            self.skipTest("langchain is not installed in this test runtime")

        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            tools = build_tools(workspace)
            write_tool = next(tool for tool in tools if tool.name == "write_workspace_file")

            output = write_tool.invoke({"path": "backend/requirements.txt", "content": "fastapi"})

        self.assertEqual(output, "File write failed: File does not exist: backend/requirements.txt")

    def test_edit_file_tool_returns_success_message(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("old text", encoding="utf-8")

            output = run_edit_file_tool(workspace, "notes.txt", "old", "new")

            self.assertEqual((workspace / "notes.txt").read_text(encoding="utf-8"), "new text")
        self.assertEqual(output, "File edited: notes.txt")

    def test_create_file_tool_returns_error_message_for_existing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("old", encoding="utf-8")

            output = run_create_file_tool(workspace, "notes.txt", "new")

        self.assertEqual(output, "File write failed: File already exists: notes.txt")

    def test_edit_file_tool_returns_error_message_for_missing_text(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("old text", encoding="utf-8")

            output = run_edit_file_tool(workspace, "notes.txt", "missing", "new")

        self.assertEqual(output, "File write failed: Text to replace was not found in: notes.txt")

    def test_retrieve_context_tool_builds_index_and_returns_context(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "auth.py").write_text("def login_user():\n    pass\n", encoding="utf-8")

            output = run_retrieve_context_tool(workspace, "login")

        self.assertIn("Relevant repository context:", output)
        self.assertIn("File: auth.py", output)
        self.assertIn("login_user", output)

    def test_retrieve_context_tool_handles_no_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "auth.py").write_text("def login_user():\n    pass\n", encoding="utf-8")

            output = run_retrieve_context_tool(workspace, "billing")

        self.assertEqual(output, "No relevant repository context was retrieved.")

    def test_retrieve_memories_tool_returns_matching_memory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            from forge_agent.long_term_memory import add_memory

            add_memory(workspace, "Use pip instead of uv.", kind="preference")

            output = run_retrieve_memories_tool(workspace, "pip install")

        self.assertIn("Use pip instead of uv.", output)

    def test_retrieve_memories_tool_handles_no_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            from forge_agent.long_term_memory import add_memory

            add_memory(workspace, "Frontend uses React.")

            output = run_retrieve_memories_tool(workspace, "database")

        self.assertEqual(output, "No relevant memories found.")

    def test_terminal_command_tool_runs_safe_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            output = run_terminal_command_tool(workspace, "git status")

        self.assertIn("Exit code:", output)
        self.assertIn("not a git repository", output.lower())

    def test_terminal_command_tool_blocks_destructive_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            output = run_terminal_command_tool(workspace, "git reset --hard")

        self.assertIn("blocked", output.lower())

    def test_python_sandbox_tool_returns_readable_output(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            output = run_python_sandbox_tool(workspace, "print('hello')")

        self.assertIn("Exit code: 0", output)
        self.assertIn("STDOUT:\nhello", output)

    def test_git_status_tool_returns_command_output(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))

            output = run_git_status_tool(workspace)

        self.assertIn("Command: git status --short", output)

    def test_git_read_tools_are_registered_when_langchain_is_available(self) -> None:
        if importlib.util.find_spec("langchain") is None:
            self.skipTest("langchain is not installed in this test runtime")

        with TemporaryDirectory() as temp_dir:
            tools = build_tools(Path(temp_dir))

        tool_names = {tool.name for tool in tools}
        self.assertIn("git_status", tool_names)
        self.assertIn("git_diff", tool_names)
        self.assertIn("git_log", tool_names)
        self.assertIn("git_branch", tool_names)


if __name__ == "__main__":
    unittest.main()


def init_git_repo(workspace: Path) -> Path:
    import subprocess

    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "forge@example.com"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Forge Tests"], cwd=workspace, check=True)
    (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=workspace, check=True, capture_output=True, text=True)
    return workspace

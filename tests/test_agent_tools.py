import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.agent_tools import (
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

    def test_edit_file_tool_returns_success_message(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("old text", encoding="utf-8")

            output = run_edit_file_tool(workspace, "notes.txt", "old", "new")

            self.assertEqual((workspace / "notes.txt").read_text(encoding="utf-8"), "new text")
        self.assertEqual(output, "File edited: notes.txt")

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


if __name__ == "__main__":
    unittest.main()

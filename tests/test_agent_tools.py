import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.agent_tools import (
    run_create_file_tool,
    run_edit_file_tool,
    run_list_files_tool,
    run_read_file_tool,
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


if __name__ == "__main__":
    unittest.main()

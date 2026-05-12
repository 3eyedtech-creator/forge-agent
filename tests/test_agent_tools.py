import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_tools import run_list_files_tool, run_read_file_tool, run_search_text_tool


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


if __name__ == "__main__":
    unittest.main()

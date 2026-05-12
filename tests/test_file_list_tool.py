import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.file_list_tool import list_files


class FileListToolTests(unittest.TestCase):
    def test_lists_workspace_files_recursively(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("", encoding="utf-8")
            (workspace / "docs").mkdir()
            (workspace / "docs" / "notes.md").write_text("", encoding="utf-8")

            result = list_files(workspace)

        self.assertEqual(result.paths, ["agent.py", "docs/notes.md"])

    def test_excludes_common_dependency_and_cache_directories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("", encoding="utf-8")
            (workspace / ".venv").mkdir()
            (workspace / ".venv" / "ignored.py").write_text("", encoding="utf-8")
            (workspace / ".forge-agent").mkdir()
            (workspace / ".forge-agent" / "index.sqlite").write_text("", encoding="utf-8")
            (workspace / "__pycache__").mkdir()
            (workspace / "__pycache__" / "ignored.pyc").write_text("", encoding="utf-8")

            result = list_files(workspace)

        self.assertEqual(result.paths, ["agent.py"])

    def test_filters_by_extension(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("", encoding="utf-8")
            (workspace / "README.md").write_text("", encoding="utf-8")

            result = list_files(workspace, extensions={".py"})

        self.assertEqual(result.paths, ["agent.py"])


if __name__ == "__main__":
    unittest.main()

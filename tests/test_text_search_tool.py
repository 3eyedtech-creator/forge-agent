import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from text_search_tool import search_text


class TextSearchToolTests(unittest.TestCase):
    def test_finds_matching_lines(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("alpha\nneedle here\nomega\n", encoding="utf-8")

            result = search_text(workspace, "needle")

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].path, "agent.py")
        self.assertEqual(result.matches[0].line_number, 2)
        self.assertEqual(result.matches[0].line, "needle here")

    def test_includes_context_lines(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("before\nneedle\nnext\n", encoding="utf-8")

            result = search_text(workspace, "needle", context_lines=1)

        self.assertEqual(result.matches[0].before, ["before"])
        self.assertEqual(result.matches[0].after, ["next"])

    def test_skips_excluded_directories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "agent.py").write_text("needle\n", encoding="utf-8")
            (workspace / ".venv").mkdir()
            (workspace / ".venv" / "ignored.py").write_text("needle\n", encoding="utf-8")

            result = search_text(workspace, "needle")

        self.assertEqual([match.path for match in result.matches], ["agent.py"])

    def test_limits_number_of_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "a.txt").write_text("needle\n", encoding="utf-8")
            (workspace / "b.txt").write_text("needle\n", encoding="utf-8")

            result = search_text(workspace, "needle", max_matches=1)

        self.assertEqual(len(result.matches), 1)


if __name__ == "__main__":
    unittest.main()

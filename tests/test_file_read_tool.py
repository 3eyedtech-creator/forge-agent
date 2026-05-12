import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from file_read_tool import FileReadError, read_text_file
from path_utils import PathOutsideWorkspaceError


class FileReadToolTests(unittest.TestCase):
    def test_reads_text_file_with_line_numbers(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "notes.txt"
            file_path.write_text("alpha\nbeta\n", encoding="utf-8")

            result = read_text_file(workspace, "notes.txt")

        self.assertEqual(result.path, "notes.txt")
        self.assertEqual(result.content, "1: alpha\n2: beta")

    def test_blocks_path_outside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()

            with self.assertRaises(PathOutsideWorkspaceError):
                read_text_file(workspace, "../secret.txt")

    def test_rejects_missing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            with self.assertRaises(FileReadError):
                read_text_file(workspace, "missing.txt")

    def test_rejects_oversized_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "big.txt"
            file_path.write_text("too large", encoding="utf-8")

            with self.assertRaises(FileReadError):
                read_text_file(workspace, "big.txt", max_bytes=3)


if __name__ == "__main__":
    unittest.main()

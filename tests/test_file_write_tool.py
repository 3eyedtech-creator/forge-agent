import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from file_write_tool import FileWriteError, create_file, edit_file, write_file
from path_utils import PathOutsideWorkspaceError


class FileWriteToolTests(unittest.TestCase):
    def test_create_file_writes_new_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            result = create_file(workspace, "notes.txt", "hello")

            self.assertEqual((workspace / "notes.txt").read_text(encoding="utf-8"), "hello")
        self.assertEqual(result.path, "notes.txt")

    def test_create_file_refuses_to_overwrite(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("existing", encoding="utf-8")

            with self.assertRaises(FileWriteError):
                create_file(workspace, "notes.txt", "new")

    def test_write_file_updates_existing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "notes.txt"
            file_path.write_text("old", encoding="utf-8")

            result = write_file(workspace, "notes.txt", "new")

            self.assertEqual(file_path.read_text(encoding="utf-8"), "new")
        self.assertEqual(result.path, "notes.txt")

    def test_write_file_requires_existing_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            with self.assertRaises(FileWriteError):
                write_file(workspace, "missing.txt", "new")

    def test_edit_file_replaces_exact_text_once(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "notes.txt"
            file_path.write_text("alpha\nbeta\n", encoding="utf-8")

            result = edit_file(workspace, "notes.txt", "beta", "gamma")

            self.assertEqual(file_path.read_text(encoding="utf-8"), "alpha\ngamma\n")
        self.assertEqual(result.path, "notes.txt")

    def test_edit_file_requires_exact_text_match(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "notes.txt").write_text("alpha", encoding="utf-8")

            with self.assertRaises(FileWriteError):
                edit_file(workspace, "notes.txt", "missing", "new")

    def test_blocks_writes_outside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()

            with self.assertRaises(PathOutsideWorkspaceError):
                create_file(workspace, "../outside.txt", "secret")


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from path_utils import PathOutsideWorkspaceError, resolve_workspace_path


class PathUtilsTests(unittest.TestCase):
    def test_resolves_relative_path_inside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            resolved = resolve_workspace_path(workspace, "README.md")

        self.assertEqual(resolved, workspace.resolve() / "README.md")

    def test_allows_absolute_path_inside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            inside_path = workspace / "agent.py"

            resolved = resolve_workspace_path(workspace, inside_path)

        self.assertEqual(resolved, inside_path.resolve())

    def test_blocks_relative_path_outside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()

            with self.assertRaises(PathOutsideWorkspaceError):
                resolve_workspace_path(workspace, "../outside.txt")

    def test_blocks_absolute_path_outside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workspace = root / "workspace"
            workspace.mkdir()
            outside_path = root / "outside.txt"

            with self.assertRaises(PathOutsideWorkspaceError):
                resolve_workspace_path(workspace, outside_path)


if __name__ == "__main__":
    unittest.main()

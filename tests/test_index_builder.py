import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.index_builder import build_index
from forge_agent.index_store import IndexStore


class IndexBuilderTests(unittest.TestCase):
    def test_build_index_scans_chunks_and_persists_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")

            result = build_index(workspace)

            store = IndexStore(workspace / ".forge-agent" / "index.sqlite")
            files = store.load_files()
            chunks = store.load_chunks()

        self.assertEqual(result.file_count, 1)
        self.assertEqual(result.chunk_count, 1)
        self.assertEqual(files[0].path, "app.py")
        self.assertEqual(chunks[0].path, "app.py")

    def test_build_index_replaces_old_index(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            old_file = workspace / "old.py"
            old_file.write_text("old\n", encoding="utf-8")

            build_index(workspace)
            old_file.unlink()
            (workspace / "new.py").write_text("new\n", encoding="utf-8")

            build_index(workspace)

            store = IndexStore(workspace / ".forge-agent" / "index.sqlite")
            files = store.load_files()

        self.assertEqual([file.path for file in files], ["new.py"])


if __name__ == "__main__":
    unittest.main()

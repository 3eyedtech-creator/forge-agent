import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.index_store import IndexStore
from forge_agent.repository_scanner import FileMetadata
from forge_agent.text_chunker import TextChunk


class IndexStoreTests(unittest.TestCase):
    def test_saves_and_loads_files_and_chunks(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "index.sqlite"
            store = IndexStore(db_path)
            store.initialize()

            file_metadata = FileMetadata(
                path="app.py",
                extension=".py",
                size_bytes=12,
                modified_time=123.0,
                language="python",
                kind="source",
            )
            chunk = TextChunk(
                path="app.py",
                start_line=1,
                end_line=1,
                content="1: print('hi')",
                language="python",
                chunk_type="line_range",
                token_estimate=4,
            )

            store.replace_index([file_metadata], [chunk])

            files = store.load_files()
            chunks = store.load_chunks()

        self.assertEqual(files, [file_metadata])
        self.assertEqual(chunks, [chunk])

    def test_replace_index_removes_old_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "index.sqlite"
            store = IndexStore(db_path)
            store.initialize()

            old_file = make_file("old.py")
            new_file = make_file("new.py")

            store.replace_index([old_file], [])
            store.replace_index([new_file], [])

            files = store.load_files()

        self.assertEqual(files, [new_file])


def make_file(path: str) -> FileMetadata:
    return FileMetadata(
        path=path,
        extension=Path(path).suffix,
        size_bytes=1,
        modified_time=1.0,
        language="python",
        kind="source",
    )


if __name__ == "__main__":
    unittest.main()

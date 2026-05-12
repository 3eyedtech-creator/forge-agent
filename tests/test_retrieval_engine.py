import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.index_store import IndexStore
from forge_agent.repository_scanner import FileMetadata
from forge_agent.retrieval_engine import retrieve_context
from forge_agent.text_chunker import TextChunk


class RetrievalEngineTests(unittest.TestCase):
    def test_retrieves_matching_chunk_content(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = make_store(Path(temp_dir))
            store.replace_index(
                [make_file("auth.py"), make_file("billing.py")],
                [
                    make_chunk("auth.py", "1: def login_user(): pass"),
                    make_chunk("billing.py", "1: def create_invoice(): pass"),
                ],
            )

            results = retrieve_context(store, "login")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].path, "auth.py")
        self.assertGreater(results[0].score, 0)
        self.assertIn("content", results[0].reason)

    def test_scores_filename_matches(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = make_store(Path(temp_dir))
            store.replace_index(
                [make_file("auth.py")],
                [make_chunk("auth.py", "1: def unrelated(): pass")],
            )

            results = retrieve_context(store, "auth")

        self.assertEqual(results[0].path, "auth.py")
        self.assertIn("path", results[0].reason)

    def test_limits_results_by_count(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = make_store(Path(temp_dir))
            store.replace_index(
                [make_file("a.py"), make_file("b.py")],
                [
                    make_chunk("a.py", "1: login"),
                    make_chunk("b.py", "1: login"),
                ],
            )

            results = retrieve_context(store, "login", max_items=1)

        self.assertEqual(len(results), 1)

    def test_uses_likely_path_for_scoring(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = make_store(Path(temp_dir))
            store.replace_index(
                [make_file("src/auth/login.py"), make_file("src/other.py")],
                [
                    make_chunk("src/auth/login.py", "1: def unrelated(): pass"),
                    make_chunk("src/other.py", "1: login login login"),
                ],
            )

            results = retrieve_context(store, "open src/auth/login.py")

        self.assertEqual(results[0].path, "src/auth/login.py")
        self.assertIn("likely path", results[0].reason)

    def test_prefers_test_files_for_test_queries(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = make_store(Path(temp_dir))
            store.replace_index(
                [make_file("app.py"), make_file("test_app.py", kind="test")],
                [
                    make_chunk("app.py", "1: login"),
                    make_chunk("test_app.py", "1: login"),
                ],
            )

            results = retrieve_context(store, "fix login test")

        self.assertEqual(results[0].path, "test_app.py")


def make_store(root: Path) -> IndexStore:
    store = IndexStore(root / "index.sqlite")
    store.initialize()
    return store


def make_file(path: str, kind: str = "source") -> FileMetadata:
    return FileMetadata(
        path=path,
        extension=Path(path).suffix,
        size_bytes=1,
        modified_time=1.0,
        language="python",
        kind=kind,
    )


def make_chunk(path: str, content: str) -> TextChunk:
    return TextChunk(
        path=path,
        start_line=1,
        end_line=1,
        content=content,
        language="python",
        chunk_type="line_range",
        token_estimate=5,
    )


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.repository_scanner import FileMetadata
from forge_agent.text_chunker import chunk_file


class TextChunkerTests(unittest.TestCase):
    def test_chunks_file_by_line_range(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "app.py"
            file_path.write_text("one\ntwo\nthree\n", encoding="utf-8")
            metadata = make_metadata(file_path, workspace, language="python")

            chunks = chunk_file(workspace, metadata, max_lines=2)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].path, "app.py")
        self.assertEqual(chunks[0].start_line, 1)
        self.assertEqual(chunks[0].end_line, 2)
        self.assertEqual(chunks[0].content, "1: one\n2: two")
        self.assertEqual(chunks[1].start_line, 3)
        self.assertEqual(chunks[1].end_line, 3)

    def test_includes_language_type_and_token_estimate(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "README.md"
            file_path.write_text("hello world\n", encoding="utf-8")
            metadata = make_metadata(file_path, workspace, language="markdown", kind="doc")

            chunks = chunk_file(workspace, metadata)

        self.assertEqual(chunks[0].language, "markdown")
        self.assertEqual(chunks[0].chunk_type, "line_range")
        self.assertGreaterEqual(chunks[0].token_estimate, 1)

    def test_skips_oversized_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            file_path = workspace / "big.txt"
            file_path.write_text("too large", encoding="utf-8")
            metadata = make_metadata(file_path, workspace, size_bytes=9)

            chunks = chunk_file(workspace, metadata, max_file_bytes=3)

        self.assertEqual(chunks, [])


def make_metadata(
    file_path: Path,
    workspace: Path,
    language: str = "text",
    kind: str = "source",
    size_bytes: int | None = None,
) -> FileMetadata:
    return FileMetadata(
        path=file_path.relative_to(workspace).as_posix(),
        extension=file_path.suffix,
        size_bytes=file_path.stat().st_size if size_bytes is None else size_bytes,
        modified_time=file_path.stat().st_mtime,
        language=language,
        kind=kind,
    )


if __name__ == "__main__":
    unittest.main()

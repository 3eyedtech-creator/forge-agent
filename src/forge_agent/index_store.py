import sqlite3
from contextlib import closing
from pathlib import Path

from forge_agent.repository_scanner import FileMetadata
from forge_agent.text_chunker import TextChunk


class IndexStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    extension TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    modified_time REAL NOT NULL,
                    language TEXT NOT NULL,
                    kind TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    token_estimate INTEGER NOT NULL
                )
                """
            )
            connection.commit()

    def replace_index(self, files: list[FileMetadata], chunks: list[TextChunk]) -> None:
        with closing(self._connect()) as connection:
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM files")
            connection.executemany(
                """
                INSERT INTO files (path, extension, size_bytes, modified_time, language, kind)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        file.path,
                        file.extension,
                        file.size_bytes,
                        file.modified_time,
                        file.language,
                        file.kind,
                    )
                    for file in files
                ],
            )
            connection.executemany(
                """
                INSERT INTO chunks (path, start_line, end_line, content, language, chunk_type, token_estimate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.path,
                        chunk.start_line,
                        chunk.end_line,
                        chunk.content,
                        chunk.language,
                        chunk.chunk_type,
                        chunk.token_estimate,
                    )
                    for chunk in chunks
                ],
            )
            connection.commit()

    def load_files(self) -> list[FileMetadata]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT path, extension, size_bytes, modified_time, language, kind
                FROM files
                ORDER BY path
                """
            ).fetchall()

        return [
            FileMetadata(
                path=row["path"],
                extension=row["extension"],
                size_bytes=row["size_bytes"],
                modified_time=row["modified_time"],
                language=row["language"],
                kind=row["kind"],
            )
            for row in rows
        ]

    def load_chunks(self) -> list[TextChunk]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT path, start_line, end_line, content, language, chunk_type, token_estimate
                FROM chunks
                ORDER BY path, start_line
                """
            ).fetchall()

        return [
            TextChunk(
                path=row["path"],
                start_line=row["start_line"],
                end_line=row["end_line"],
                content=row["content"],
                language=row["language"],
                chunk_type=row["chunk_type"],
                token_estimate=row["token_estimate"],
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

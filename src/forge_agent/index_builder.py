from dataclasses import dataclass
from pathlib import Path

from forge_agent.index_store import IndexStore
from forge_agent.repository_scanner import scan_repository
from forge_agent.text_chunker import TextChunk, chunk_file


@dataclass
class IndexBuildResult:
    file_count: int
    chunk_count: int
    db_path: Path


def build_index(workspace_root: Path) -> IndexBuildResult:
    root = workspace_root.resolve()
    scan_result = scan_repository(root)
    chunks: list[TextChunk] = []

    for file_metadata in scan_result.files:
        chunks.extend(chunk_file(root, file_metadata))

    db_path = root / ".forge-agent" / "index.sqlite"
    store = IndexStore(db_path)
    store.initialize()
    store.replace_index(scan_result.files, chunks)

    return IndexBuildResult(
        file_count=len(scan_result.files),
        chunk_count=len(chunks),
        db_path=db_path,
    )

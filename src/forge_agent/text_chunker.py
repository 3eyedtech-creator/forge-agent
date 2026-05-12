from dataclasses import dataclass
from pathlib import Path

from forge_agent.repository_scanner import FileMetadata


@dataclass
class TextChunk:
    path: str
    start_line: int
    end_line: int
    content: str
    language: str
    chunk_type: str
    token_estimate: int


def chunk_file(
    workspace_root: Path,
    file_metadata: FileMetadata,
    max_lines: int = 40,
    max_file_bytes: int = 100_000,
) -> list[TextChunk]:
    if file_metadata.size_bytes > max_file_bytes:
        return []

    file_path = workspace_root / file_metadata.path

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []

    chunks: list[TextChunk] = []
    for start_index in range(0, len(lines), max_lines):
        chunk_lines = lines[start_index : start_index + max_lines]
        start_line = start_index + 1
        end_line = start_index + len(chunk_lines)
        content = "\n".join(
            f"{line_number}: {line}"
            for line_number, line in enumerate(chunk_lines, start=start_line)
        )

        chunks.append(
            TextChunk(
                path=file_metadata.path,
                start_line=start_line,
                end_line=end_line,
                content=content,
                language=file_metadata.language,
                chunk_type="line_range",
                token_estimate=estimate_tokens(content),
            )
        )

    return chunks


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

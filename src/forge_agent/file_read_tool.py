from dataclasses import dataclass
from pathlib import Path

from forge_agent.path_utils import resolve_workspace_path


class FileReadError(ValueError):
    pass


@dataclass
class FileReadResult:
    path: str
    content: str


def read_text_file(workspace_root: Path, user_path: str | Path, max_bytes: int = 50_000) -> FileReadResult:
    resolved_path = resolve_workspace_path(workspace_root, user_path)

    if not resolved_path.exists():
        raise FileReadError(f"File does not exist: {user_path}")

    if not resolved_path.is_file():
        raise FileReadError(f"Path is not a file: {user_path}")

    if resolved_path.stat().st_size > max_bytes:
        raise FileReadError(f"File is too large to read safely: {user_path}")

    try:
        text = resolved_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise FileReadError(f"File is not valid UTF-8 text: {user_path}") from error

    numbered_lines = [f"{line_number}: {line}" for line_number, line in enumerate(text.splitlines(), start=1)]

    return FileReadResult(
        path=str(Path(user_path)),
        content="\n".join(numbered_lines),
    )

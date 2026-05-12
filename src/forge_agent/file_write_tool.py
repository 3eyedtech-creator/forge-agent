from dataclasses import dataclass
from pathlib import Path

from forge_agent.path_utils import resolve_workspace_path


class FileWriteError(ValueError):
    pass


@dataclass
class FileWriteResult:
    path: str
    message: str


def create_file(workspace_root: Path, user_path: str | Path, content: str) -> FileWriteResult:
    resolved_path = resolve_workspace_path(workspace_root, user_path)

    if resolved_path.exists():
        raise FileWriteError(f"File already exists: {user_path}")

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(content, encoding="utf-8")

    return FileWriteResult(path=str(Path(user_path)), message="File created.")


def write_file(workspace_root: Path, user_path: str | Path, content: str) -> FileWriteResult:
    resolved_path = resolve_workspace_path(workspace_root, user_path)

    if not resolved_path.exists():
        raise FileWriteError(f"File does not exist: {user_path}")

    if not resolved_path.is_file():
        raise FileWriteError(f"Path is not a file: {user_path}")

    resolved_path.write_text(content, encoding="utf-8")

    return FileWriteResult(path=str(Path(user_path)), message="File written.")


def edit_file(workspace_root: Path, user_path: str | Path, old_text: str, new_text: str) -> FileWriteResult:
    resolved_path = resolve_workspace_path(workspace_root, user_path)

    if not resolved_path.exists():
        raise FileWriteError(f"File does not exist: {user_path}")

    if not resolved_path.is_file():
        raise FileWriteError(f"Path is not a file: {user_path}")

    text = resolved_path.read_text(encoding="utf-8")
    if old_text not in text:
        raise FileWriteError(f"Text to replace was not found in: {user_path}")

    resolved_path.write_text(text.replace(old_text, new_text, 1), encoding="utf-8")

    return FileWriteResult(path=str(Path(user_path)), message="File edited.")

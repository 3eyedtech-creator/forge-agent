from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXCLUDED_DIRS = {
    ".forge-agent",
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass
class FileListResult:
    paths: list[str]


def list_files(workspace_root: Path, extensions: set[str] | None = None) -> FileListResult:
    root = workspace_root.resolve()
    paths: list[str] = []

    for path in root.rglob("*"):
        if any(part in DEFAULT_EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue

        if not path.is_file():
            continue

        if extensions is not None and path.suffix not in extensions:
            continue

        paths.append(path.relative_to(root).as_posix())

    return FileListResult(paths=sorted(paths))

from dataclasses import dataclass
from pathlib import Path

from forge_agent.file_list_tool import DEFAULT_EXCLUDED_DIRS


@dataclass
class FileMetadata:
    path: str
    extension: str
    size_bytes: int
    modified_time: float
    language: str
    kind: str


@dataclass
class RepositoryScanResult:
    files: list[FileMetadata]


LANGUAGE_BY_EXTENSION = {
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".go": "go",
    ".html": "html",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript-react",
    ".kt": "kotlin",
    ".md": "markdown",
    ".py": "python",
    ".rs": "rust",
    ".sh": "shell",
    ".sql": "sql",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
}

CONFIG_FILENAMES = {
    ".env.example",
    ".gitignore",
    "pyproject.toml",
    "requirements.txt",
}

DOC_EXTENSIONS = {".md", ".rst", ".txt"}


def scan_repository(workspace_root: Path) -> RepositoryScanResult:
    root = workspace_root.resolve()
    files: list[FileMetadata] = []

    for path in root.rglob("*"):
        relative_path = path.relative_to(root)
        if any(part in DEFAULT_EXCLUDED_DIRS for part in relative_path.parts):
            continue

        if not path.is_file():
            continue

        extension = path.suffix
        files.append(
            FileMetadata(
                path=relative_path.as_posix(),
                extension=extension,
                size_bytes=path.stat().st_size,
                modified_time=path.stat().st_mtime,
                language=detect_language(extension),
                kind=classify_file_kind(relative_path),
            )
        )

    return RepositoryScanResult(files=sorted(files, key=lambda file: file.path))


def detect_language(extension: str) -> str:
    return LANGUAGE_BY_EXTENSION.get(extension.lower(), "unknown")


def classify_file_kind(relative_path: Path) -> str:
    filename = relative_path.name
    lowercase_name = filename.lower()
    extension = relative_path.suffix.lower()

    if filename in CONFIG_FILENAMES:
        return "config"

    if is_test_filename(lowercase_name):
        return "test"

    if extension in DOC_EXTENSIONS:
        return "doc"

    if extension in SOURCE_EXTENSIONS:
        return "source"

    return "other"


SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".py",
    ".rs",
    ".ts",
    ".tsx",
}


def is_test_filename(lowercase_name: str) -> bool:
    return (
        lowercase_name.startswith("test_")
        or "_test." in lowercase_name
        or ".test." in lowercase_name
        or ".spec." in lowercase_name
        or lowercase_name.endswith("test.java")
        or lowercase_name.endswith("tests.java")
    )

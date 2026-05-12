from dataclasses import dataclass
from pathlib import Path

from forge_agent.file_list_tool import list_files


@dataclass
class TextMatch:
    path: str
    line_number: int
    line: str
    before: list[str]
    after: list[str]


@dataclass
class TextSearchResult:
    matches: list[TextMatch]


def search_text(
    workspace_root: Path,
    query: str,
    context_lines: int = 0,
    max_matches: int = 20,
) -> TextSearchResult:
    root = workspace_root.resolve()
    matches: list[TextMatch] = []

    for relative_path in list_files(root).paths:
        path = root / relative_path

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for index, line in enumerate(lines):
            if query not in line:
                continue

            start = max(0, index - context_lines)
            end = min(len(lines), index + context_lines + 1)
            matches.append(
                TextMatch(
                    path=relative_path,
                    line_number=index + 1,
                    line=line,
                    before=lines[start:index],
                    after=lines[index + 1 : end],
                )
            )

            if len(matches) >= max_matches:
                return TextSearchResult(matches=matches)

    return TextSearchResult(matches=matches)

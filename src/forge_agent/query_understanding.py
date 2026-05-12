import re
from dataclasses import dataclass


@dataclass
class QueryUnderstanding:
    original_query: str
    task_type: str
    search_terms: list[str]
    phrases: list[str]
    likely_paths: list[str]
    test_terms: list[str]


STOP_WORDS = {
    "a",
    "an",
    "and",
    "does",
    "how",
    "in",
    "is",
    "me",
    "of",
    "the",
    "this",
    "to",
}

TASK_KEYWORDS = {
    "explain": {"explain", "understand", "describe", "how"},
    "fix": {"bug", "error", "failing", "failure", "fix", "broken"},
    "implement": {"add", "build", "create", "implement"},
    "refactor": {"extract", "refactor", "rename", "restructure"},
    "test": {"test", "tests", "coverage"},
    "review": {"review", "audit", "inspect"},
}


def understand_query(query: str) -> QueryUnderstanding:
    phrases = extract_quoted_phrases(query)
    likely_paths = extract_likely_paths(query)
    tokens = tokenize(query)
    search_terms = [token for token in tokens if token not in STOP_WORDS]
    test_terms = [term for term in search_terms if term.startswith("test_") or "test" in term]

    return QueryUnderstanding(
        original_query=query,
        task_type=detect_task_type(tokens),
        search_terms=search_terms,
        phrases=phrases,
        likely_paths=likely_paths,
        test_terms=test_terms,
    )


def detect_task_type(tokens: list[str]) -> str:
    token_set = set(tokens)

    for task_type, keywords in TASK_KEYWORDS.items():
        if token_set & keywords:
            return task_type

    return "unknown"


def extract_quoted_phrases(query: str) -> list[str]:
    return [match.strip() for match in re.findall(r'"([^"]+)"', query) if match.strip()]


def extract_likely_paths(query: str) -> list[str]:
    path_pattern = r"[\w./\\-]+\.[A-Za-z0-9]+"
    return re.findall(path_pattern, query)


def tokenize(query: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[a-zA-Z0-9_]+", query)]

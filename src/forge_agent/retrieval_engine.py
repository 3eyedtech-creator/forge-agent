import re
from dataclasses import dataclass

from forge_agent.index_store import IndexStore
from forge_agent.query_understanding import QueryUnderstanding, understand_query
from forge_agent.repository_scanner import FileMetadata
from forge_agent.text_chunker import TextChunk


@dataclass
class RetrievedContextItem:
    path: str
    start_line: int
    end_line: int
    content: str
    score: float
    reason: str
    token_estimate: int


def retrieve_context(store: IndexStore, query: str, max_items: int = 5) -> list[RetrievedContextItem]:
    understood_query = understand_query(query)
    query_terms = understood_query.search_terms + understood_query.phrases + understood_query.test_terms
    if not query_terms and not understood_query.likely_paths:
        return []

    files_by_path = {file.path: file for file in store.load_files()}
    scored_items = []
    for chunk in store.load_chunks():
        score, reasons = score_chunk(chunk, query_terms, understood_query, files_by_path.get(chunk.path))
        if score <= 0:
            continue

        scored_items.append(
            RetrievedContextItem(
                path=chunk.path,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                content=chunk.content,
                score=score,
                reason=", ".join(reasons),
                token_estimate=chunk.token_estimate,
            )
        )

    return sorted(scored_items, key=lambda item: (-item.score, item.path, item.start_line))[:max_items]


def score_chunk(
    chunk: TextChunk,
    query_terms: list[str],
    understood_query: QueryUnderstanding | None = None,
    file_metadata: FileMetadata | None = None,
) -> tuple[float, list[str]]:
    path_text = chunk.path.lower()
    content_text = chunk.content.lower()
    score = 0.0
    reasons = []

    if understood_query is not None:
        likely_path_matches = [
            path for path in understood_query.likely_paths if path.lower().replace("\\", "/") in path_text
        ]
        if likely_path_matches:
            score += 8
            reasons.append("likely path match")

    path_matches = sum(1 for term in query_terms if term in path_text)
    if path_matches:
        score += path_matches * 3
        reasons.append("path match")

    content_matches = sum(content_text.count(term) for term in query_terms)
    if content_matches:
        score += content_matches
        reasons.append("content match")

    if understood_query is not None and file_metadata is not None:
        if understood_query.task_type == "test" or "test" in understood_query.search_terms:
            if file_metadata.kind == "test":
                score += 2
                reasons.append("test file boost")

    return score, reasons


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[a-zA-Z0-9_]+", text) if len(token) > 1]

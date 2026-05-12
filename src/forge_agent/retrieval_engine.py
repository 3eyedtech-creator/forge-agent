import re
from dataclasses import dataclass

from forge_agent.index_store import IndexStore
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
    query_terms = tokenize(query)
    if not query_terms:
        return []

    scored_items = []
    for chunk in store.load_chunks():
        score, reasons = score_chunk(chunk, query_terms)
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


def score_chunk(chunk: TextChunk, query_terms: list[str]) -> tuple[float, list[str]]:
    path_text = chunk.path.lower()
    content_text = chunk.content.lower()
    score = 0.0
    reasons = []

    path_matches = sum(1 for term in query_terms if term in path_text)
    if path_matches:
        score += path_matches * 3
        reasons.append("path match")

    content_matches = sum(content_text.count(term) for term in query_terms)
    if content_matches:
        score += content_matches
        reasons.append("content match")

    return score, reasons


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[a-zA-Z0-9_]+", text) if len(token) > 1]

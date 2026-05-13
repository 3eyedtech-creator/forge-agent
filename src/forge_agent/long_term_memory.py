import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass
class Memory:
    id: str
    scope: str
    kind: str
    text: str
    confidence: float
    source: str
    created_at: str


def add_memory(
    workspace_root: Path,
    text: str,
    kind: str = "fact",
    scope: str = "workspace",
    confidence: float = 1.0,
    source: str = "user",
) -> Memory:
    memory = Memory(
        id=f"mem_{uuid4().hex}",
        scope=scope,
        kind=kind,
        text=text,
        confidence=confidence,
        source=source,
        created_at=datetime.now(UTC).isoformat(),
    )
    memory_path = get_memory_path(workspace_root)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    with memory_path.open("a", encoding="utf-8") as memory_file:
        memory_file.write(json.dumps(asdict(memory)) + "\n")

    return memory


def list_memories(workspace_root: Path) -> list[Memory]:
    memory_path = get_memory_path(workspace_root)
    if not memory_path.exists():
        return []

    memories = []
    for line in memory_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        memories.append(Memory(**json.loads(line)))

    return memories


def clear_memories(workspace_root: Path) -> None:
    memory_path = get_memory_path(workspace_root)
    if memory_path.exists():
        memory_path.unlink()


def retrieve_memories(workspace_root: Path, query: str, max_items: int = 5) -> list[Memory]:
    query_terms = tokenize(query)
    if not query_terms:
        return []

    scored_memories = []
    for memory in list_memories(workspace_root):
        searchable_text = f"{memory.scope} {memory.kind} {memory.text}".lower()
        score = sum(searchable_text.count(term) for term in query_terms)
        if score > 0:
            scored_memories.append((score, memory))

    scored_memories.sort(key=lambda item: (-item[0], item[1].created_at))
    return [memory for _, memory in scored_memories[:max_items]]


def get_memory_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".forge-agent" / "memory.jsonl"


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[a-zA-Z0-9_]+", text) if len(token) > 1]

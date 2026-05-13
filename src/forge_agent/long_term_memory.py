import json
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


def get_memory_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".forge-agent" / "memory.jsonl"

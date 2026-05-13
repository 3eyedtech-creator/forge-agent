import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass
class SessionState:
    session_id: str
    workspace_root: str
    created_at: str
    updated_at: str
    messages: list[dict[str, str]]


def load_or_create_session(workspace_root: Path) -> SessionState:
    session_path = get_session_path(workspace_root)

    if session_path.exists():
        data = json.loads(session_path.read_text(encoding="utf-8"))
        return SessionState(**data)

    now = current_timestamp()
    return SessionState(
        session_id=f"ses_{uuid4().hex}",
        workspace_root=str(workspace_root.resolve()),
        created_at=now,
        updated_at=now,
        messages=[],
    )


def save_session(session: SessionState) -> None:
    session.updated_at = current_timestamp()
    session_path = get_session_path(Path(session.workspace_root))
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(json.dumps(asdict(session), indent=2), encoding="utf-8")


def append_message(session: SessionState, role: str, content: str) -> None:
    session.messages.append({"role": role, "content": content})


def clear_messages(session: SessionState) -> None:
    session.messages.clear()


def get_session_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".forge-agent" / "sessions" / "current.json"


def current_timestamp() -> str:
    return datetime.now(UTC).isoformat()

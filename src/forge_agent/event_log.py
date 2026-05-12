import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


DEFAULT_EVENT_LOG_PATH = Path(".forge-agent") / "events.jsonl"


def create_event(event_type: str, data: dict) -> dict:
    return {
        "id": f"evt_{uuid4().hex}",
        "type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "data": data,
    }


def write_event(event: dict, log_path: Path = DEFAULT_EVENT_LOG_PATH) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

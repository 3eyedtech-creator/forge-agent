import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from forge_agent.task_planner import TaskPlan, plan_to_dict, update_task_plan


@dataclass
class SessionState:
    session_id: str
    workspace_root: str
    created_at: str
    updated_at: str
    messages: list[dict[str, str]]
    active_plan: dict | None = None
    changed_files: list[dict] | None = None
    commands_run: list[dict] | None = None
    report_risks: list[str] | None = None
    active_skill: str | None = None

    def __post_init__(self) -> None:
        if self.changed_files is None:
            self.changed_files = []
        if self.commands_run is None:
            self.commands_run = []
        if self.report_risks is None:
            self.report_risks = []


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


def set_plan(session: SessionState, plan: TaskPlan) -> None:
    session.active_plan = plan_to_dict(plan)


def update_active_plan(session: SessionState, step_id: str, status: str, notes: str = "") -> None:
    if session.active_plan is None:
        raise ValueError("No active plan.")

    session.active_plan = update_task_plan(session.active_plan, step_id, status, notes)


def clear_plan(session: SessionState) -> None:
    session.active_plan = None


def add_changed_file(session: SessionState, path: str, action: str) -> None:
    item = {"path": path, "action": action}
    if item not in session.changed_files:
        session.changed_files.append(item)


def add_command_run(session: SessionState, command: str, exit_code: int, kind: str = "command") -> None:
    session.commands_run.append({"command": command, "exit_code": exit_code, "kind": kind})


def add_report_risk(session: SessionState, risk: str) -> None:
    if risk not in session.report_risks:
        session.report_risks.append(risk)


def set_active_skill(session: SessionState, skill_name: str | None) -> None:
    session.active_skill = skill_name


def get_session_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".forge-agent" / "sessions" / "current.json"


def current_timestamp() -> str:
    return datetime.now(UTC).isoformat()

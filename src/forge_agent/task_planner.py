from dataclasses import dataclass
from datetime import UTC, datetime


VALID_STEP_STATUSES = {"pending", "in_progress", "completed", "failed"}


@dataclass
class TaskStep:
    id: str
    description: str
    status: str = "pending"
    notes: str = ""


@dataclass
class TaskPlan:
    goal: str
    steps: list[TaskStep]
    risks: list[str]
    updated_at: str


DEFAULT_COMPLEX_TASK_STEPS = [
    "Understand the request",
    "Retrieve relevant repository context",
    "Inspect related files",
    "Propose changes",
    "Apply approved changes",
    "Verify with tests or checks",
    "Summarize result",
]


def create_task_plan(goal: str) -> TaskPlan:
    return TaskPlan(
        goal=goal,
        steps=[
            TaskStep(id=f"step_{index}", description=description)
            for index, description in enumerate(DEFAULT_COMPLEX_TASK_STEPS, start=1)
        ],
        risks=[],
        updated_at=current_timestamp(),
    )


def format_task_plan(plan: TaskPlan) -> str:
    lines = [f"Plan: {plan.goal}"]

    for step in plan.steps:
        notes = f" - {step.notes}" if step.notes else ""
        lines.append(f"{step.id}. [{step.status}] {step.description}{notes}")

    return "\n".join(lines)


def plan_to_dict(plan: TaskPlan) -> dict:
    return {
        "goal": plan.goal,
        "steps": [
            {
                "id": step.id,
                "description": step.description,
                "status": step.status,
                "notes": step.notes,
            }
            for step in plan.steps
        ],
        "risks": list(plan.risks),
        "updated_at": plan.updated_at,
    }


def format_task_plan_dict(plan: dict) -> str:
    lines = [f"Plan: {plan['goal']}"]

    for index, step in enumerate(plan["steps"], start=1):
        step_id = step.get("id", f"step_{index}")
        notes = f" - {step.get('notes', '')}" if step.get("notes") else ""
        lines.append(f"{step_id}. [{step['status']}] {step['description']}{notes}")

    risks = plan.get("risks", [])
    if risks:
        lines.append("Risks:")
        lines.extend(f"- {risk}" for risk in risks)

    return "\n".join(lines)


def update_task_plan(plan: dict, step_id: str, status: str, notes: str = "") -> dict:
    if status not in VALID_STEP_STATUSES:
        raise ValueError(f"Invalid plan step status: {status}")

    updated_plan = {
        "goal": plan["goal"],
        "steps": [dict(step) for step in plan["steps"]],
        "risks": list(plan.get("risks", [])),
        "updated_at": current_timestamp(),
    }

    for index, step in enumerate(updated_plan["steps"], start=1):
        if step.get("id", f"step_{index}") == step_id:
            step["id"] = step_id
            step["status"] = status
            if notes:
                step["notes"] = notes
            else:
                step.setdefault("notes", "")

            if status == "failed" and notes:
                risk = f"{step_id} failed: {notes}"
                if risk not in updated_plan["risks"]:
                    updated_plan["risks"].append(risk)

            return updated_plan

    raise ValueError(f"Unknown plan step: {step_id}")


def current_timestamp() -> str:
    return datetime.now(UTC).isoformat()

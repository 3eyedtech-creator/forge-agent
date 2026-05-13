from dataclasses import dataclass


@dataclass
class TaskStep:
    description: str
    status: str = "pending"


@dataclass
class TaskPlan:
    goal: str
    steps: list[TaskStep]


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
        steps=[TaskStep(description=description) for description in DEFAULT_COMPLEX_TASK_STEPS],
    )


def format_task_plan(plan: TaskPlan) -> str:
    lines = [f"Plan: {plan.goal}"]

    for index, step in enumerate(plan.steps, start=1):
        lines.append(f"{index}. [{step.status}] {step.description}")

    return "\n".join(lines)

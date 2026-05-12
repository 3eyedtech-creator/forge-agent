from dataclasses import dataclass


@dataclass
class ModelSelection:
    model: str
    task_complexity: str
    should_plan: bool
    reason: str


COMPLEX_KEYWORDS = {
    "architecture",
    "debug",
    "design",
    "failing",
    "failure",
    "from scratch",
    "implement",
    "multiple files",
    "plan",
    "refactor",
}


def route_model(query: str, fast_model: str, reasoning_model: str) -> ModelSelection:
    lowered_query = query.lower()

    if any(keyword in lowered_query for keyword in COMPLEX_KEYWORDS):
        return ModelSelection(
            model=reasoning_model,
            task_complexity="complex",
            should_plan=True,
            reason="Complex implementation, debugging, design, or refactor query.",
        )

    return ModelSelection(
        model=fast_model,
        task_complexity="simple",
        should_plan=False,
        reason="Simple query can use the fast model.",
    )

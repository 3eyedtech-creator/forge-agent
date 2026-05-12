from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console


def decisions_from_approvals(approvals: list[bool]) -> list[dict]:
    decisions = []

    for approved in approvals:
        if approved:
            decisions.append({"type": "approve"})
        else:
            decisions.append({"type": "reject", "message": "User rejected this tool call."})

    return decisions


def has_rejection(decisions: list[dict]) -> bool:
    return any(decision.get("type") == "reject" for decision in decisions)


def ask_for_tool_decisions(interrupts: tuple, console: "Console") -> list[dict]:
    from rich.panel import Panel
    from rich.prompt import Confirm

    approvals = []

    for interrupt in interrupts:
        value = interrupt.value
        action_requests = value.get("action_requests", [])

        for action in action_requests:
            name = action.get("name", "unknown_tool")
            arguments = action.get("arguments", {})
            description = action.get("description", "Tool call requires approval.")
            console.print(Panel(f"{description}\n\nArguments: {arguments}", title=f"Review: {name}", border_style="yellow"))
            approvals.append(Confirm.ask("Approve this tool call?", default=False, console=console))

    return decisions_from_approvals(approvals)

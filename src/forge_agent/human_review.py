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


def summarize_text(label: str, text: str) -> str:
    line_count = text.count("\n") + 1 if text else 0
    line_word = "line" if line_count == 1 else "lines"
    char_word = "character" if len(text) == 1 else "characters"
    return f"{label}: {line_count} {line_word}, {len(text)} {char_word}"


def format_action_arguments(name: str, arguments: dict) -> str:
    if name in {"create_workspace_file", "write_workspace_file"}:
        path = arguments.get("path", "<missing>")
        content = str(arguments.get("content", ""))
        return f"Path: {path}\n{summarize_text('Content', content)}"

    if name == "edit_workspace_file":
        path = arguments.get("path", "<missing>")
        old_text = str(arguments.get("old_text", ""))
        new_text = str(arguments.get("new_text", ""))
        return (
            f"Path: {path}\n"
            f"{summarize_text('Old text', old_text)}\n"
            f"{summarize_text('New text', new_text)}"
        )

    return f"Arguments: {arguments}"


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
            argument_summary = format_action_arguments(name, arguments)
            console.print(Panel(f"{description}\n\n{argument_summary}", title=f"Review: {name}", border_style="yellow"))
            approvals.append(Confirm.ask("Approve this tool call?", default=False, console=console))

    return decisions_from_approvals(approvals)

from rich.console import Console
from rich.prompt import Confirm

from forge_agent.policy_engine import ApprovalResponse


def ask_for_approval(command: str, reason: str, console: Console) -> ApprovalResponse:
    console.print(f"[yellow]Approval required:[/yellow] {reason}")
    console.print(f"[bold]Command:[/bold] {command}")

    if Confirm.ask("Allow this action?", default=False, console=console):
        return ApprovalResponse.APPROVE

    return ApprovalResponse.DENY

from pathlib import Path

from forge_agent.approval_mode import ApprovalMode


def build_ready_text(
    workspace_root: Path,
    fast_model: str,
    reasoning_model: str,
    approval_mode: ApprovalMode,
) -> str:
    return (
        f"Workspace: {workspace_root}\n"
        f"Fast model: {fast_model}\n"
        f"Reasoning model: {reasoning_model}\n"
        f"Approval mode: {approval_mode.value}\n\n"
        "Use /help for commands, /mode auto for fewer approvals, /exit to quit."
    )

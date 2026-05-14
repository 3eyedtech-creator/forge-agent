from enum import Enum


class ApprovalMode(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"


READ_ONLY_TOOL_POLICY = {
    "list_workspace_files": False,
    "read_workspace_file": False,
    "search_workspace_text": False,
    "retrieve_workspace_context": False,
    "retrieve_workspace_memories": False,
    "run_python_sandbox_code": False,
}

FILE_MUTATION_TOOLS = {
    "create_workspace_file",
    "write_workspace_file",
    "edit_workspace_file",
}


def parse_approval_mode(value: str) -> ApprovalMode:
    normalized = value.strip().lower()

    if normalized == ApprovalMode.MANUAL.value:
        return ApprovalMode.MANUAL

    if normalized == ApprovalMode.AUTO.value:
        return ApprovalMode.AUTO

    raise ValueError(f"Unknown approval mode: {value}")


def build_interrupt_policy(mode: ApprovalMode) -> dict:
    policy = dict(READ_ONLY_TOOL_POLICY)

    for tool_name in FILE_MUTATION_TOOLS:
        if mode == ApprovalMode.AUTO:
            policy[tool_name] = False
        else:
            policy[tool_name] = {"allowed_decisions": ["approve", "reject"]}

    return policy

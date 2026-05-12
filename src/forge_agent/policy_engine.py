import shlex
from enum import Enum


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    BLOCK = "block"


class ApprovalResponse(str, Enum):
    APPROVE = "approve"
    DENY = "deny"


SAFE_READ_COMMANDS = {
    ("dir",),
    ("git", "diff"),
    ("git", "status"),
    ("ls",),
    ("pwd",),
}

DESTRUCTIVE_COMMAND_PREFIXES = {
    ("del",),
    ("git", "reset", "--hard"),
    ("rm",),
    ("rmdir",),
}


def decide_shell_command(command: str) -> PolicyDecision:
    try:
        parts = tuple(shlex.split(command, posix=False))
    except ValueError:
        return PolicyDecision.BLOCK

    lowered_parts = tuple(part.lower() for part in parts)

    if lowered_parts in SAFE_READ_COMMANDS:
        return PolicyDecision.ALLOW

    for prefix in DESTRUCTIVE_COMMAND_PREFIXES:
        if lowered_parts[: len(prefix)] == prefix:
            return PolicyDecision.BLOCK

    return PolicyDecision.REQUIRE_APPROVAL


def resolve_policy_decision(decision: PolicyDecision, approval: ApprovalResponse | None = None) -> PolicyDecision:
    if decision != PolicyDecision.REQUIRE_APPROVAL:
        return decision

    if approval == ApprovalResponse.APPROVE:
        return PolicyDecision.ALLOW

    return PolicyDecision.BLOCK

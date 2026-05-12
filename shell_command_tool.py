import subprocess
from dataclasses import dataclass
from pathlib import Path

from policy_engine import ApprovalResponse, PolicyDecision, decide_shell_command, resolve_policy_decision


class ShellCommandError(ValueError):
    pass


@dataclass
class ShellCommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def run_shell_command(
    workspace_root: Path,
    command: str,
    approval: ApprovalResponse | None = None,
    timeout_seconds: int = 30,
) -> ShellCommandResult:
    policy_decision = decide_shell_command(command)
    final_decision = resolve_policy_decision(policy_decision, approval)

    if final_decision == PolicyDecision.BLOCK:
        raise ShellCommandError(f"Command was blocked by policy: {command}")

    completed = subprocess.run(
        command,
        cwd=workspace_root,
        capture_output=True,
        shell=True,
        text=True,
        timeout=timeout_seconds,
    )

    return ShellCommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )

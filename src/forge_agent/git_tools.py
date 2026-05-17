import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitCommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def run_git_status(workspace_root: Path) -> str:
    return format_git_result(run_git(workspace_root, ["status", "--short"]))


def run_git_diff(workspace_root: Path) -> str:
    return format_git_result(run_git(workspace_root, ["diff"]))


def run_git_log(workspace_root: Path) -> str:
    return format_git_result(run_git(workspace_root, ["log", "--oneline", "-5"]))


def run_git_branch(workspace_root: Path) -> str:
    return format_git_result(run_git(workspace_root, ["branch", "--show-current"]))


def run_git_add(workspace_root: Path, path: str) -> str:
    return format_git_result(run_git(workspace_root, ["add", "--", path]))


def run_git_commit(workspace_root: Path, message: str) -> str:
    return format_git_result(run_git(workspace_root, ["commit", "-m", message]))


def run_git(workspace_root: Path, args: list[str]) -> GitCommandResult:
    completed = subprocess.run(
        ["git", *args],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return GitCommandResult(
        command=format_git_command(args),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def format_git_command(args: list[str]) -> str:
    return "git " + " ".join(args)


def format_git_result(result) -> str:
    output_parts = [f"Command: {result.command}", f"Exit code: {result.exit_code}"]
    if result.stdout:
        output_parts.append(f"STDOUT:\n{result.stdout.strip()}")
    if result.stderr:
        output_parts.append(f"STDERR:\n{result.stderr.strip()}")
    return "\n".join(output_parts)

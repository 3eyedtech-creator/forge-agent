from pathlib import Path

from forge_agent.context_builder import build_context_section
from forge_agent.file_list_tool import list_files
from forge_agent.file_read_tool import read_text_file
from forge_agent.file_write_tool import FileWriteError, create_file, edit_file, write_file
from forge_agent.git_tools import run_git_branch, run_git_diff, run_git_log, run_git_status
from forge_agent.index_builder import build_index
from forge_agent.index_store import IndexStore
from forge_agent.long_term_memory import retrieve_memories
from forge_agent.policy_engine import ApprovalResponse, PolicyDecision, decide_shell_command
from forge_agent.retrieval_engine import retrieve_context
from forge_agent.sandbox_python_tool import run_python_sandbox
from forge_agent.shell_command_tool import ShellCommandError, run_shell_command
from forge_agent.text_search_tool import search_text


def run_list_files_tool(workspace_root: Path) -> str:
    result = list_files(workspace_root)

    if not result.paths:
        return "No files found."

    return "\n".join(result.paths)


def run_read_file_tool(workspace_root: Path, path: str) -> str:
    result = read_text_file(workspace_root, path)
    return result.content


def run_search_text_tool(workspace_root: Path, query: str) -> str:
    result = search_text(workspace_root, query, context_lines=1)

    if not result.matches:
        return "No matches found."

    lines = []
    for match in result.matches:
        lines.append(f"{match.path}:{match.line_number}: {match.line}")

    return "\n".join(lines)


def run_retrieve_context_tool(workspace_root: Path, query: str) -> str:
    db_path = workspace_root / ".forge-agent" / "index.sqlite"

    if not db_path.exists():
        build_index(workspace_root)

    store = IndexStore(db_path)
    items = retrieve_context(store, query)
    return build_context_section(items)


def run_retrieve_memories_tool(workspace_root: Path, query: str) -> str:
    memories = retrieve_memories(workspace_root, query)

    if not memories:
        return "No relevant memories found."

    return "\n".join(
        f"{memory.id} [{memory.scope}/{memory.kind}] {memory.text}"
        for memory in memories
    )


def run_terminal_command_tool(
    workspace_root: Path,
    command: str,
    approval: ApprovalResponse | None = None,
) -> str:
    try:
        result = run_shell_command(workspace_root, command, approval=approval)
    except ShellCommandError as error:
        return f"Command blocked: {error}"

    output_parts = [f"Command: {result.command}", f"Exit code: {result.exit_code}"]
    if result.stdout:
        output_parts.append(f"STDOUT:\n{result.stdout.strip()}")
    if result.stderr:
        output_parts.append(f"STDERR:\n{result.stderr.strip()}")

    return "\n".join(output_parts)


def run_python_sandbox_tool(workspace_root: Path, code: str) -> str:
    result = run_python_sandbox(workspace_root, code)

    output_parts = [
        "Sandbox: Python temporary directory",
        f"Exit code: {result.exit_code}",
    ]
    if result.stdout:
        output_parts.append(f"STDOUT:\n{result.stdout.strip()}")
    if result.stderr:
        output_parts.append(f"STDERR:\n{result.stderr.strip()}")

    return "\n".join(output_parts)


def run_git_status_tool(workspace_root: Path) -> str:
    return run_git_status(workspace_root)


def run_git_diff_tool(workspace_root: Path) -> str:
    return run_git_diff(workspace_root)


def run_git_log_tool(workspace_root: Path) -> str:
    return run_git_log(workspace_root)


def run_git_branch_tool(workspace_root: Path) -> str:
    return run_git_branch(workspace_root)


def run_create_file_tool(workspace_root: Path, path: str, content: str) -> str:
    try:
        result = create_file(workspace_root, path, content)
    except FileWriteError as error:
        return f"File write failed: {error}"

    return f"{result.message.removesuffix('.')}: {result.path}"


def run_write_file_tool(workspace_root: Path, path: str, content: str) -> str:
    try:
        result = write_file(workspace_root, path, content)
    except FileWriteError as error:
        return f"File write failed: {error}"

    return f"{result.message.removesuffix('.')}: {result.path}"


def run_edit_file_tool(workspace_root: Path, path: str, old_text: str, new_text: str) -> str:
    try:
        result = edit_file(workspace_root, path, old_text, new_text)
    except FileWriteError as error:
        return f"File write failed: {error}"

    return f"{result.message.removesuffix('.')}: {result.path}"


def build_tools(workspace_root: Path, console=None) -> list:
    from langchain.tools import tool

    @tool
    def list_workspace_files() -> str:
        """List files in the current workspace."""
        return run_list_files_tool(workspace_root)

    @tool
    def read_workspace_file(path: str) -> str:
        """Read a UTF-8 text file from the current workspace with line numbers."""
        return run_read_file_tool(workspace_root, path)

    @tool
    def search_workspace_text(query: str) -> str:
        """Search workspace text files for an exact text query."""
        return run_search_text_tool(workspace_root, query)

    @tool
    def retrieve_workspace_context(query: str) -> str:
        """Retrieve relevant indexed repository context for a coding question."""
        return run_retrieve_context_tool(workspace_root, query)

    @tool
    def retrieve_workspace_memories(query: str) -> str:
        """Retrieve relevant long-term workspace memories for a query."""
        return run_retrieve_memories_tool(workspace_root, query)

    @tool
    def run_terminal_command(command: str) -> str:
        """Run a terminal command in the workspace. Safe read-only commands run directly; risky commands require approval."""
        decision = decide_shell_command(command)

        if decision == PolicyDecision.REQUIRE_APPROVAL:
            if console is None:
                return "Command requires approval, but no approval prompt is available."
            from forge_agent.approval_prompt import ask_for_approval

            approval = ask_for_approval(command, "Command is not classified as safe read-only.", console)
            return run_terminal_command_tool(workspace_root, command, approval=approval)

        return run_terminal_command_tool(workspace_root, command)

    @tool
    def run_python_sandbox_code(code: str) -> str:
        """Run a Python code snippet in a temporary sandbox directory and return stdout, stderr, and exit code."""
        return run_python_sandbox_tool(workspace_root, code)

    @tool
    def git_status() -> str:
        """Show short Git status for the current workspace."""
        return run_git_status_tool(workspace_root)

    @tool
    def git_diff() -> str:
        """Show unstaged Git diff for the current workspace."""
        return run_git_diff_tool(workspace_root)

    @tool
    def git_log() -> str:
        """Show the five most recent Git commits."""
        return run_git_log_tool(workspace_root)

    @tool
    def git_branch() -> str:
        """Show the current Git branch."""
        return run_git_branch_tool(workspace_root)

    @tool
    def create_workspace_file(path: str, content: str) -> str:
        """Create a new UTF-8 text file in the current workspace."""
        return run_create_file_tool(workspace_root, path, content)

    @tool
    def write_workspace_file(path: str, content: str) -> str:
        """Replace the full content of an existing UTF-8 text file in the current workspace."""
        return run_write_file_tool(workspace_root, path, content)

    @tool
    def edit_workspace_file(path: str, old_text: str, new_text: str) -> str:
        """Edit a workspace file by replacing one exact text occurrence."""
        return run_edit_file_tool(workspace_root, path, old_text, new_text)

    return [
        list_workspace_files,
        read_workspace_file,
        search_workspace_text,
        retrieve_workspace_context,
        retrieve_workspace_memories,
        run_terminal_command,
        run_python_sandbox_code,
        git_status,
        git_diff,
        git_log,
        git_branch,
        create_workspace_file,
        write_workspace_file,
        edit_workspace_file,
    ]

from dataclasses import dataclass
from pathlib import Path

from forge_agent.agent_tools import (
    run_python_sandbox_tool,
    run_retrieve_context_tool,
    run_terminal_command_tool,
)
from forge_agent.approval_mode import ApprovalMode, parse_approval_mode
from forge_agent.git_tools import (
    run_git_add,
    run_git_branch,
    run_git_commit,
    run_git_diff,
    run_git_log,
    run_git_status,
)
from forge_agent.index_builder import build_index
from forge_agent.long_term_memory import add_memory, clear_memories, list_memories
from forge_agent.mcp_config import McpConfigError, format_mcp_list, format_mcp_show, load_mcp_config
from forge_agent.session_memory import get_session_path
from forge_agent.skill_loader import (
    default_builtin_skills_dir,
    discover_skills,
    format_skill_list,
    format_skill_show,
)
from forge_agent.task_planner import format_task_plan_dict, update_task_plan
from forge_agent.task_report import format_task_report


@dataclass
class SlashCommandState:
    workspace_root: Path
    model: str
    message_count: int
    messages: list[dict[str, str]] | None = None
    active_plan: dict | None = None
    approval_mode: ApprovalMode = ApprovalMode.MANUAL
    changed_files: list[dict] | None = None
    commands_run: list[dict] | None = None
    report_risks: list[str] | None = None
    active_skill: str | None = None


@dataclass
class SlashCommandResult:
    output: str
    should_exit: bool = False
    should_clear_messages: bool = False
    should_clear_plan: bool = False
    next_approval_mode: ApprovalMode | None = None
    next_active_plan: dict | None = None
    command_run: dict | None = None
    next_active_skill: str | None = None


HELP_TEXT = """Available commands:
/help                 Show this help
/status               Show workspace, model, and message count
/index                Rebuild the workspace index
/retrieve <query>     Show retrieved repository context for a query
/run <command>        Run a terminal command through policy checks
/python <code>        Run Python code in a temporary sandbox directory
/mode [manual|auto]   Show or change approval mode
/skills list          List available skills
/skills show <name>   Show skill instructions
/skill <name>         Use a skill for future turns
/mcp list             List configured MCP servers
/mcp show <server>    Show MCP server configuration
/git status           Show short Git status
/git diff             Show unstaged Git diff
/git log              Show recent Git commits
/git branch           Show current Git branch
/git add <path>       Stage a path
/git commit <message> Commit staged changes
/memory add <text>    Save a workspace memory
/memory list          List workspace memories
/memory clear         Clear workspace memories
/session show        Show current short-term session messages
/session path        Show current session file path
/session clear       Clear current session messages
/report              Show current task report
/plan show           Show the active task plan
/plan update <id> <status> [notes]
/plan clear          Clear the active task plan
/clear                Clear chat memory
/exit                 Exit the agent
"""


def handle_slash_command(command: str, state: SlashCommandState) -> SlashCommandResult:
    command = command.strip()

    if command == "/help":
        return SlashCommandResult(output=HELP_TEXT)

    if command == "/status":
        return SlashCommandResult(
            output=(
                f"Workspace: {state.workspace_root}\n"
                f"Model: {state.model}\n"
                f"Messages: {state.message_count}\n"
                f"Approval mode: {state.approval_mode.value}"
            )
        )

    if command == "/mode":
        return SlashCommandResult(output=f"Approval mode: {state.approval_mode.value}")

    if command.startswith("/mode "):
        mode_text = command.removeprefix("/mode ").strip()
        try:
            next_mode = parse_approval_mode(mode_text)
        except ValueError:
            return SlashCommandResult(output="Usage: /mode [manual|auto]")

        return SlashCommandResult(
            output=f"Approval mode set to {next_mode.value}.",
            next_approval_mode=next_mode,
        )

    if command == "/skills list":
        skills = load_available_skills(state.workspace_root)
        return SlashCommandResult(output=format_skill_list(skills))

    if command.startswith("/skills show "):
        skill_name = command.removeprefix("/skills show ").strip()
        skills = load_available_skills(state.workspace_root)
        skill = skills.get(skill_name)
        if skill is None:
            return SlashCommandResult(output=f"Unknown skill: {skill_name}")
        return SlashCommandResult(output=format_skill_show(skill))

    if command.startswith("/skill "):
        skill_name = command.removeprefix("/skill ").strip()
        skills = load_available_skills(state.workspace_root)
        if skill_name not in skills:
            return SlashCommandResult(output=f"Unknown skill: {skill_name}")
        return SlashCommandResult(
            output=f"Active skill set to {skill_name}.",
            next_active_skill=skill_name,
        )

    if command == "/mcp list":
        try:
            config = load_mcp_config(state.workspace_root)
        except McpConfigError as error:
            return SlashCommandResult(output=f"MCP config error: {error}")
        return SlashCommandResult(output=format_mcp_list(config))

    if command.startswith("/mcp show "):
        server_name = command.removeprefix("/mcp show ").strip()
        try:
            config = load_mcp_config(state.workspace_root)
        except McpConfigError as error:
            return SlashCommandResult(output=f"MCP config error: {error}")
        server = config.servers.get(server_name)
        if server is None:
            return SlashCommandResult(output=f"Unknown MCP server: {server_name}")
        return SlashCommandResult(output=format_mcp_show(server))

    if command.startswith("/git"):
        return handle_git_command(command, state)

    if command == "/index":
        result = build_index(state.workspace_root)
        return SlashCommandResult(
            output=(
                f"Index rebuilt.\n"
                f"Indexed files: {result.file_count}\n"
                f"Chunks: {result.chunk_count}\n"
                f"Database: {result.db_path}"
            )
        )

    if command.startswith("/retrieve "):
        query = command.removeprefix("/retrieve ").strip()
        if not query:
            return SlashCommandResult(output="Usage: /retrieve <query>")
        return SlashCommandResult(output=run_retrieve_context_tool(state.workspace_root, query))

    if command == "/run":
        return SlashCommandResult(output="Usage: /run <command>")

    if command.startswith("/run "):
        terminal_command = command.removeprefix("/run ").strip()
        if not terminal_command:
            return SlashCommandResult(output="Usage: /run <command>")
        output = run_terminal_command_tool(state.workspace_root, terminal_command)
        return SlashCommandResult(
            output=output,
            command_run={
                "command": terminal_command,
                "exit_code": parse_exit_code(output),
                "kind": classify_command_kind(terminal_command),
            },
        )

    if command == "/python":
        return SlashCommandResult(output="Usage: /python <code>")

    if command.startswith("/python "):
        code = command.removeprefix("/python ").strip()
        if not code:
            return SlashCommandResult(output="Usage: /python <code>")
        return SlashCommandResult(output=run_python_sandbox_tool(state.workspace_root, code))

    if command.startswith("/memory add "):
        text = command.removeprefix("/memory add ").strip()
        if not text:
            return SlashCommandResult(output="Usage: /memory add <text>")
        memory = add_memory(state.workspace_root, text)
        return SlashCommandResult(output=f"Memory added: {memory.id}")

    if command == "/memory list":
        memories = list_memories(state.workspace_root)
        if not memories:
            return SlashCommandResult(output="No memories found.")

        lines = [
            f"{memory.id} [{memory.scope}/{memory.kind}] {memory.text}"
            for memory in memories
        ]
        return SlashCommandResult(output="\n".join(lines))

    if command == "/memory clear":
        clear_memories(state.workspace_root)
        return SlashCommandResult(output="Memories cleared.")

    if command == "/session show":
        if not state.messages:
            return SlashCommandResult(output="No session messages found.")

        lines = [
            f"{message.get('role', 'unknown')}: {message.get('content', '')}"
            for message in state.messages
        ]
        return SlashCommandResult(output="\n".join(lines))

    if command == "/session path":
        return SlashCommandResult(output=str(get_session_path(state.workspace_root)))

    if command == "/report":
        return SlashCommandResult(
            output=format_task_report(
                changed_files=state.changed_files or [],
                commands_run=state.commands_run or [],
                risks=state.report_risks or [],
            )
        )

    if command == "/plan show":
        if not state.active_plan:
            return SlashCommandResult(output="No active plan.")
        return SlashCommandResult(output=format_task_plan_dict(state.active_plan))

    if command.startswith("/plan update "):
        if not state.active_plan:
            return SlashCommandResult(output="No active plan.")

        parts = command.split(maxsplit=4)
        if len(parts) < 4:
            return SlashCommandResult(output="Usage: /plan update <step_id> <pending|in_progress|completed|failed> [notes]")

        step_id = parts[2]
        status = parts[3]
        notes = parts[4] if len(parts) == 5 else ""

        try:
            updated_plan = update_task_plan(state.active_plan, step_id, status, notes)
        except ValueError:
            return SlashCommandResult(output="Usage: /plan update <step_id> <pending|in_progress|completed|failed> [notes]")

        return SlashCommandResult(
            output=f"Updated {step_id} to {status}.",
            next_active_plan=updated_plan,
        )

    if command == "/plan clear":
        return SlashCommandResult(output="Plan cleared.", should_clear_plan=True)

    if command in {"/clear", "/session clear"}:
        return SlashCommandResult(output="Chat memory cleared.", should_clear_messages=True)

    if command in {"/exit", "/quit"}:
        return SlashCommandResult(output="Goodbye.", should_exit=True)

    return SlashCommandResult(output=f"Unknown slash command: {command}\nType /help to see available commands.")


def parse_exit_code(output: str) -> int:
    for line in output.splitlines():
        if line.startswith("Exit code:"):
            try:
                return int(line.removeprefix("Exit code:").strip())
            except ValueError:
                return -1

    return -1


def classify_command_kind(command: str) -> str:
    lowered = command.lower()
    verification_terms = ("test", "pytest", "unittest", "ruff", "mypy", "lint", "typecheck")

    if any(term in lowered for term in verification_terms):
        return "verification"

    return "command"


def handle_git_command(command: str, state: SlashCommandState) -> SlashCommandResult:
    if command == "/git status":
        return git_result(run_git_status(state.workspace_root), "git status --short")

    if command == "/git diff":
        return git_result(run_git_diff(state.workspace_root), "git diff")

    if command == "/git log":
        return git_result(run_git_log(state.workspace_root), "git log --oneline -5")

    if command == "/git branch":
        return git_result(run_git_branch(state.workspace_root), "git branch --show-current")

    if command.startswith("/git add "):
        path = command.removeprefix("/git add ").strip()
        if not path:
            return SlashCommandResult(output="Usage: /git add <path>")
        return git_result(run_git_add(state.workspace_root, path), f"git add -- {path}")

    if command.startswith("/git commit "):
        message = command.removeprefix("/git commit ").strip()
        if not message:
            return SlashCommandResult(output="Usage: /git commit <message>")
        return git_result(run_git_commit(state.workspace_root, message), f"git commit -m {message}")

    return SlashCommandResult(output="Usage: /git <status|diff|log|branch|add|commit>")


def git_result(output: str, command: str) -> SlashCommandResult:
    return SlashCommandResult(
        output=output,
        command_run={
            "command": command,
            "exit_code": parse_exit_code(output),
            "kind": "git",
        },
    )


def load_available_skills(workspace_root: Path) -> dict:
    return discover_skills(
        project_dir=workspace_root / ".forge-agent" / "skills",
        user_dir=Path.home() / ".forge-agent" / "skills",
        builtin_dir=default_builtin_skills_dir(),
    )

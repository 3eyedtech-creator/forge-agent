from dataclasses import dataclass
from pathlib import Path

from forge_agent.agent_tools import (
    run_python_sandbox_tool,
    run_retrieve_context_tool,
    run_terminal_command_tool,
)
from forge_agent.approval_mode import ApprovalMode, parse_approval_mode
from forge_agent.index_builder import build_index
from forge_agent.long_term_memory import add_memory, clear_memories, list_memories
from forge_agent.session_memory import get_session_path


@dataclass
class SlashCommandState:
    workspace_root: Path
    model: str
    message_count: int
    messages: list[dict[str, str]] | None = None
    active_plan: dict | None = None
    approval_mode: ApprovalMode = ApprovalMode.MANUAL


@dataclass
class SlashCommandResult:
    output: str
    should_exit: bool = False
    should_clear_messages: bool = False
    should_clear_plan: bool = False
    next_approval_mode: ApprovalMode | None = None


HELP_TEXT = """Available commands:
/help                 Show this help
/status               Show workspace, model, and message count
/index                Rebuild the workspace index
/retrieve <query>     Show retrieved repository context for a query
/run <command>        Run a terminal command through policy checks
/python <code>        Run Python code in a temporary sandbox directory
/mode [manual|auto]   Show or change approval mode
/memory add <text>    Save a workspace memory
/memory list          List workspace memories
/memory clear         Clear workspace memories
/session show        Show current short-term session messages
/session path        Show current session file path
/session clear       Clear current session messages
/plan show           Show the active task plan
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
        return SlashCommandResult(output=run_terminal_command_tool(state.workspace_root, terminal_command))

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

    if command == "/plan show":
        if not state.active_plan:
            return SlashCommandResult(output="No active plan.")
        lines = [f"Plan: {state.active_plan['goal']}"]
        for index, step in enumerate(state.active_plan["steps"], start=1):
            lines.append(f"{index}. [{step['status']}] {step['description']}")
        return SlashCommandResult(output="\n".join(lines))

    if command == "/plan clear":
        return SlashCommandResult(output="Plan cleared.", should_clear_plan=True)

    if command in {"/clear", "/session clear"}:
        return SlashCommandResult(output="Chat memory cleared.", should_clear_messages=True)

    if command in {"/exit", "/quit"}:
        return SlashCommandResult(output="Goodbye.", should_exit=True)

    return SlashCommandResult(output=f"Unknown slash command: {command}\nType /help to see available commands.")

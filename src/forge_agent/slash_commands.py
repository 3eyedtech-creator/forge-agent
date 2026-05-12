from dataclasses import dataclass
from pathlib import Path

from forge_agent.agent_tools import run_retrieve_context_tool
from forge_agent.index_builder import build_index


@dataclass
class SlashCommandState:
    workspace_root: Path
    model: str
    message_count: int


@dataclass
class SlashCommandResult:
    output: str
    should_exit: bool = False
    should_clear_messages: bool = False


HELP_TEXT = """Available commands:
/help                 Show this help
/status               Show workspace, model, and message count
/index                Rebuild the workspace index
/retrieve <query>     Show retrieved repository context for a query
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
                f"Messages: {state.message_count}"
            )
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

    if command == "/clear":
        return SlashCommandResult(output="Chat memory cleared.", should_clear_messages=True)

    if command in {"/exit", "/quit"}:
        return SlashCommandResult(output="Goodbye.", should_exit=True)

    return SlashCommandResult(output=f"Unknown slash command: {command}\nType /help to see available commands.")

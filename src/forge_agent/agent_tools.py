from pathlib import Path

from forge_agent.context_builder import build_context_section
from forge_agent.file_list_tool import list_files
from forge_agent.file_read_tool import read_text_file
from forge_agent.file_write_tool import create_file, edit_file, write_file
from forge_agent.index_builder import build_index
from forge_agent.index_store import IndexStore
from forge_agent.long_term_memory import retrieve_memories
from forge_agent.retrieval_engine import retrieve_context
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


def run_create_file_tool(workspace_root: Path, path: str, content: str) -> str:
    result = create_file(workspace_root, path, content)
    return f"{result.message.removesuffix('.')}: {result.path}"


def run_write_file_tool(workspace_root: Path, path: str, content: str) -> str:
    result = write_file(workspace_root, path, content)
    return f"{result.message.removesuffix('.')}: {result.path}"


def run_edit_file_tool(workspace_root: Path, path: str, old_text: str, new_text: str) -> str:
    result = edit_file(workspace_root, path, old_text, new_text)
    return f"{result.message.removesuffix('.')}: {result.path}"


def build_tools(workspace_root: Path) -> list:
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
        create_workspace_file,
        write_workspace_file,
        edit_workspace_file,
    ]

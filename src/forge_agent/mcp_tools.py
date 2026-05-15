import importlib.util
from dataclasses import dataclass

from forge_agent.mcp_config import McpConfig, to_langchain_mcp_config


MultiServerMCPClient = None


@dataclass
class McpToolLoadResult:
    tools: list
    warnings: list[str]


async def load_mcp_tools(config: McpConfig) -> McpToolLoadResult:
    adapter_config = to_langchain_mcp_config(config)
    if not adapter_config:
        return McpToolLoadResult(tools=[], warnings=[])

    if importlib.util.find_spec("langchain_mcp_adapters") is None:
        return McpToolLoadResult(
            tools=[],
            warnings=["langchain-mcp-adapters is not installed; MCP tools were not loaded."],
        )

    try:
        client_class = get_multiserver_mcp_client()
        client = client_class(adapter_config)
        tools = await client.get_tools()
    except Exception as error:
        return McpToolLoadResult(tools=[], warnings=[f"MCP tools failed to load: {error}"])

    return McpToolLoadResult(tools=list(tools), warnings=[])


def get_multiserver_mcp_client():
    global MultiServerMCPClient

    if MultiServerMCPClient is not None:
        return MultiServerMCPClient

    from langchain_mcp_adapters.client import MultiServerMCPClient as imported_client

    MultiServerMCPClient = imported_client
    return imported_client

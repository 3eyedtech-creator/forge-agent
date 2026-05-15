import importlib.util
import unittest
from unittest.mock import AsyncMock, patch

from forge_agent.mcp_config import McpConfig, McpServerConfig
from forge_agent.mcp_tools import load_mcp_tools


class McpToolsTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_empty_tools_when_no_servers_are_enabled(self) -> None:
        config = McpConfig(servers={"docs": McpServerConfig(name="docs", enabled=False, transport="streamable_http", url="http://localhost")})

        result = await load_mcp_tools(config)

        self.assertEqual(result.tools, [])
        self.assertEqual(result.warnings, [])

    async def test_returns_warning_when_adapter_dependency_is_missing(self) -> None:
        config = McpConfig(servers={"docs": McpServerConfig(name="docs", enabled=True, transport="streamable_http", url="http://localhost")})

        with patch("importlib.util.find_spec", return_value=None):
            result = await load_mcp_tools(config)

        self.assertEqual(result.tools, [])
        self.assertIn("langchain-mcp-adapters is not installed", result.warnings[0])

    async def test_loads_tools_through_multiserver_client_when_dependency_exists(self) -> None:
        if importlib.util.find_spec("langchain_mcp_adapters") is None:
            self.skipTest("langchain-mcp-adapters is not installed in this test runtime")

        config = McpConfig(servers={"docs": McpServerConfig(name="docs", enabled=True, transport="streamable_http", url="http://localhost")})
        fake_client = AsyncMock()
        fake_client.get_tools.return_value = ["tool"]

        with patch("forge_agent.mcp_tools.MultiServerMCPClient", return_value=fake_client):
            result = await load_mcp_tools(config)

        self.assertEqual(result.tools, ["tool"])
        self.assertEqual(result.warnings, [])


if __name__ == "__main__":
    unittest.main()

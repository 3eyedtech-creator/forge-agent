import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.mcp_config import (
    McpConfigError,
    format_mcp_list,
    format_mcp_show,
    load_mcp_config,
    to_langchain_mcp_config,
)


class McpConfigTests(unittest.TestCase):
    def test_loads_stdio_server_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps(
                    {
                        "servers": {
                            "filesystem": {
                                "enabled": True,
                                "transport": "stdio",
                                "command": "npx",
                                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
                                "env": {"TOKEN": "${TOKEN}"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            config = load_mcp_config(workspace, home)

        server = config.servers["filesystem"]
        self.assertTrue(server.enabled)
        self.assertEqual(server.transport, "stdio")
        self.assertEqual(server.command, "npx")
        self.assertEqual(server.args[-1], ".")
        self.assertEqual(server.env, {"TOKEN": "${TOKEN}"})

    def test_loads_streamable_http_server_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps(
                    {
                        "servers": {
                            "docs": {
                                "enabled": True,
                                "transport": "streamable_http",
                                "url": "http://localhost:8000/mcp",
                                "headers": {"Authorization": "${DOCS_TOKEN}"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            config = load_mcp_config(workspace, home)

        server = config.servers["docs"]
        self.assertEqual(server.transport, "streamable_http")
        self.assertEqual(server.url, "http://localhost:8000/mcp")
        self.assertEqual(server.headers, {"Authorization": "${DOCS_TOKEN}"})

    def test_project_config_overrides_user_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (home / ".forge-agent").mkdir(parents=True)
            (home / ".forge-agent" / "mcp.json").write_text(
                json.dumps({"servers": {"github": {"transport": "stdio", "command": "old"}}}),
                encoding="utf-8",
            )
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps({"servers": {"github": {"transport": "stdio", "command": "new"}}}),
                encoding="utf-8",
            )

            config = load_mcp_config(workspace, home)

        self.assertEqual(config.servers["github"].command, "new")

    def test_rejects_unsupported_transport(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps({"servers": {"bad": {"transport": "sse", "url": "http://localhost"}}}),
                encoding="utf-8",
            )

            with self.assertRaises(McpConfigError):
                load_mcp_config(workspace, home)

    def test_formats_list_and_show_with_redacted_secret_values(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps(
                    {
                        "servers": {
                            "docs": {
                                "enabled": True,
                                "transport": "streamable_http",
                                "url": "http://localhost:8000/mcp",
                                "headers": {"Authorization": "secret-token"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            config = load_mcp_config(workspace, home)

        self.assertIn("docs [enabled] streamable_http", format_mcp_list(config))
        show = format_mcp_show(config.servers["docs"])
        self.assertIn("Authorization: <redacted>", show)
        self.assertNotIn("secret-token", show)

    def test_converts_enabled_servers_to_langchain_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            home = Path(temp_dir) / "home"
            (workspace / ".forge-agent").mkdir(parents=True)
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps(
                    {
                        "servers": {
                            "filesystem": {
                                "enabled": True,
                                "transport": "stdio",
                                "command": "npx",
                                "args": ["-y", "server"],
                            },
                            "docs": {
                                "enabled": True,
                                "transport": "streamable_http",
                                "url": "http://localhost:8000/mcp",
                            },
                            "disabled": {
                                "enabled": False,
                                "transport": "stdio",
                                "command": "skip",
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )
            config = load_mcp_config(workspace, home)

        adapter_config = to_langchain_mcp_config(config)

        self.assertEqual(adapter_config["filesystem"]["transport"], "stdio")
        self.assertEqual(adapter_config["docs"]["transport"], "streamable_http")
        self.assertNotIn("disabled", adapter_config)


if __name__ == "__main__":
    unittest.main()

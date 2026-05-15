import json
import os
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_TRANSPORTS = {"stdio", "streamable_http"}


class McpConfigError(ValueError):
    pass


@dataclass
class McpServerConfig:
    name: str
    enabled: bool
    transport: str
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    url: str | None = None
    headers: dict[str, str] | None = None


@dataclass
class McpConfig:
    servers: dict[str, McpServerConfig]


def load_mcp_config(workspace_root: Path, home_dir: Path | None = None) -> McpConfig:
    home = Path.home() if home_dir is None else home_dir
    user_path = home / ".forge-agent" / "mcp.json"
    project_path = workspace_root / ".forge-agent" / "mcp.json"

    merged_servers = {}
    for path in (user_path, project_path):
        data = read_mcp_json(path)
        merged_servers.update(data.get("servers", {}))

    return McpConfig(
        servers={
            name: normalize_server_config(name, value)
            for name, value in sorted(merged_servers.items())
        }
    )


def read_mcp_json(path: Path) -> dict:
    if not path.exists():
        return {"servers": {}}

    return json.loads(path.read_text(encoding="utf-8"))


def normalize_server_config(name: str, value: dict) -> McpServerConfig:
    transport = value.get("transport")
    if transport not in SUPPORTED_TRANSPORTS:
        raise McpConfigError(f"Unsupported MCP transport for {name}: {transport}")

    enabled = bool(value.get("enabled", False))
    args = list(value.get("args", []))
    env = dict(value.get("env", {}))
    headers = dict(value.get("headers", {}))

    if transport == "stdio" and not value.get("command"):
        raise McpConfigError(f"MCP stdio server requires command: {name}")

    if transport == "streamable_http" and not value.get("url"):
        raise McpConfigError(f"MCP streamable_http server requires url: {name}")

    return McpServerConfig(
        name=name,
        enabled=enabled,
        transport=transport,
        command=value.get("command"),
        args=args,
        env=env,
        url=value.get("url"),
        headers=headers,
    )


def to_langchain_mcp_config(config: McpConfig) -> dict:
    adapter_config = {}
    for name, server in config.servers.items():
        if not server.enabled:
            continue

        if server.transport == "stdio":
            adapter_config[name] = {
                "transport": "stdio",
                "command": server.command,
                "args": server.args or [],
            }
            if server.env:
                adapter_config[name]["env"] = expand_mapping(server.env)
            continue

        if server.transport == "streamable_http":
            adapter_config[name] = {
                "transport": "streamable_http",
                "url": server.url,
            }
            if server.headers:
                adapter_config[name]["headers"] = expand_mapping(server.headers)

    return adapter_config


def expand_mapping(values: dict[str, str]) -> dict[str, str]:
    return {key: expand_env_value(value) for key, value in values.items()}


def expand_env_value(value: str) -> str:
    if value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.getenv(env_name, "")

    return value


def format_mcp_list(config: McpConfig) -> str:
    if not config.servers:
        return "No MCP servers configured."

    lines = []
    for server in config.servers.values():
        status = "enabled" if server.enabled else "disabled"
        lines.append(f"{server.name} [{status}] {server.transport}")

    return "\n".join(lines)


def format_mcp_show(server: McpServerConfig) -> str:
    lines = [
        f"Server: {server.name}",
        f"Status: {'enabled' if server.enabled else 'disabled'}",
        f"Transport: {server.transport}",
    ]

    if server.command:
        lines.append(f"Command: {server.command}")
    if server.args:
        lines.append(f"Args: {server.args}")
    if server.url:
        lines.append(f"URL: {server.url}")
    if server.env:
        lines.append("Env:")
        lines.extend(f"- {key}: <redacted>" for key in sorted(server.env))
    if server.headers:
        lines.append("Headers:")
        lines.extend(f"- {key}: <redacted>" for key in sorted(server.headers))

    return "\n".join(lines)

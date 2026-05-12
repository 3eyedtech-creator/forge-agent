# Forge Agent

This is a small learning project for building a local coding agent from scratch.

The current version is intentionally simple: it starts an interactive terminal loop, sends your messages to a LangChain agent backed by OpenAI, and prints responses with Rich.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the CLI in editable mode:

```powershell
pip install -e .
```

This makes the `forge` command available in the active Python environment.

Create a `.env` file by copying `.env.example`, then add your real OpenAI API key:

```powershell
Copy-Item .env.example .env
```

The model name is configured in `.forge-agent/config.toml`:

```toml
model = "gpt-4.1-mini"
```

Run the agent:

```powershell
forge
```

Type `exit` or `quit` to stop the chat loop.

The agent writes a local JSONL event log to `.forge-agent/events.jsonl`.

To use the agent in another repository, open a terminal in that repository and run:

```powershell
forge
```

The agent treats the current terminal directory as the workspace.

If you want `forge` available globally without activating this virtual environment, install it with `pipx`:

```powershell
pipx install -e D:\coding_agent
```

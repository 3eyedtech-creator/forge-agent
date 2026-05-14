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

Model routing is configured in `.forge-agent/config.toml`:

```toml
fast_model = "gpt-4.1-mini"
reasoning_model = "gpt-4.1"
```

Run the agent:

```powershell
forge
```

Type `exit` or `quit` to stop the chat loop.

The agent writes a local JSONL event log to `.forge-agent/events.jsonl`.
The current chat session is saved to `.forge-agent/sessions/current.json`.

## Slash Commands

Slash commands are handled locally and are not sent to the model:

```text
/help
/status
/index
/retrieve <query>
/run <command>
/memory add <text>
/memory list
/memory clear
/session show
/session path
/session clear
/plan show
/plan clear
/clear
/exit
```

To use the agent in another repository, open a terminal in that repository and run:

```powershell
forge
```

The agent treats the current terminal directory as the workspace.

If you want `forge` available globally without activating this virtual environment, install it with `pipx`:

```powershell
pipx install -e D:\coding_agent
```

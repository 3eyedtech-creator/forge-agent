# Forge Agent

Forge Agent is a local terminal coding agent that runs inside your project directory. It can chat with you about the codebase, inspect files, retrieve repository context, maintain local memory, run approved commands, and make file changes through tool calls.

This project is intentionally built in small, understandable pieces. It is useful today as a learning-focused coding agent and a foundation for building a Claude Code-style developer assistant from scratch.

## Features

- Interactive CLI experience with the `forge` command.
- OpenAI-backed LangChain agent loop.
- Repository file listing, file reading, and text search tools.
- SQLite-backed codebase indexing and retrieval.
- Short-term session memory stored locally.
- Long-term workspace memory with slash commands.
- Model routing between fast and reasoning models.
- Structured planning for complex tasks.
- File create, write, and exact edit tools.
- Policy-guarded terminal command execution.
- Lightweight Python snippet sandbox with `/python`.
- Rich terminal output.

## Requirements

- Python 3.11 or newer.
- An OpenAI API key.
- `pipx` for the recommended global install path.

## Install

### macOS/Linux

```bash
curl -fsSL https://raw.githubusercontent.com/3eyedtech-creator/forge-agent/main/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/3eyedtech-creator/forge-agent/main/install.ps1 | iex
```

The installer uses `pipx`, so the `forge` command is available from any repository after installation.

You can also install directly with `pipx`:

```bash
pipx install git+https://github.com/3eyedtech-creator/forge-agent.git
```

## Configure

Forge Agent reads your OpenAI API key from a `.env` file in the workspace where you run `forge`.

Create `.env`:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Optional model configuration lives at `.forge-agent/config.toml`:

```toml
fast_model = "gpt-4.1-mini"
reasoning_model = "gpt-4.1"
```

If the config file is missing, Forge Agent uses its built-in defaults.

## Usage

Open a terminal inside the repository you want to work on:

```bash
cd path/to/your/project
forge
```

Then ask questions or request coding tasks:

```text
Explain how authentication works in this repo.
Find where the user profile is updated.
Create a small plan for adding password reset.
Search for TODO comments.
```

Forge Agent treats the current terminal directory as the active workspace.

## Slash Commands

Slash commands are handled locally and are not sent to the model.

```text
/help                 Show available commands
/status               Show workspace, model, and message count
/index                Rebuild the workspace index
/retrieve <query>     Retrieve relevant repository context
/run <command>        Run a terminal command through policy checks
/python <code>        Run Python code in a temporary sandbox directory
/memory add <text>    Save a workspace memory
/memory list          List workspace memories
/memory clear         Clear workspace memories
/session show         Show short-term session messages
/session path         Show the session file path
/session clear        Clear short-term session messages
/plan show            Show the active task plan
/plan clear           Clear the active task plan
/clear                Alias for /session clear
/exit                 Exit the agent
```

## Safety Model

Forge Agent is designed to be local-first and explicit about risky actions.

- Repository state stays on your machine except for content sent to OpenAI during model calls.
- `.env` should contain secrets and should not be committed.
- Terminal commands run through a policy layer.
- Safe read-only commands can run directly.
- Risky commands require approval.
- Destructive commands are blocked by default.
- `/python <code>` runs in a temporary directory with a stripped environment.

The current Python sandbox is lightweight. It is useful for quick calculations and small repro scripts, but it is not a container or virtual machine security boundary.

## Local Development

Clone the repository:

```bash
git clone https://github.com/3eyedtech-creator/forge-agent.git
cd forge-agent
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install in editable mode:

```bash
pip install -e .
```

Run the agent:

```bash
forge
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Project Status

Forge Agent is under active development. The current focus is building a clear, inspectable coding agent architecture with indexing, retrieval, memory, planning, safe tools, and packaging.

Planned next areas include stronger sandbox isolation, richer command detection, better patch application, secret scanning, Git-aware workflows, and production release hardening.

## Repository

GitHub: https://github.com/3eyedtech-creator/forge-agent

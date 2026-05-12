# Forge Agent

This is a small learning project for building a local coding agent from scratch.

The current version is intentionally simple: it starts an interactive terminal loop, sends your messages to a LangChain agent backed by OpenAI, and prints responses with Rich.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

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
python agent.py
```

Type `exit` or `quit` to stop the chat loop.

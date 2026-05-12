# Forge Agent

This is a small learning project for building a local coding agent from scratch.

The first version is intentionally simple: it asks for one query, sends it to OpenAI through LangChain, and prints the response.

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

Run the agent:

```powershell
python agent.py
```

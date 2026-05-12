import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from agent_tools import build_tools
from dotenv import load_dotenv
from event_log import create_event, write_event
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from human_review import ask_for_tool_decisions, has_rejection


console = Console()
CONFIG_PATH = Path(".forge-agent") / "config.toml"
DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass
class AgentConfig:
    model: str = DEFAULT_MODEL


def load_config() -> AgentConfig:
    if not CONFIG_PATH.exists():
        return AgentConfig()

    with CONFIG_PATH.open("rb") as config_file:
        data = tomllib.load(config_file)

    return AgentConfig(model=data.get("model", DEFAULT_MODEL))


def get_last_message_text(result: dict) -> str:
    if hasattr(result, "value"):
        result = result.value

    last_message = result["messages"][-1]
    content = last_message.content

    if isinstance(content, str):
        return content

    return str(content)


def main() -> None:
    load_dotenv(override=True)

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]OPENAI_API_KEY is not set. Add it to a .env file before running the agent.[/red]")
        return

    config = load_config()
    session_event = create_event("session_started", {"model": config.model})
    write_event(session_event)

    llm = ChatOpenAI(model=config.model)
    tools = build_tools(Path.cwd())
    agent = create_agent(
        model=llm,
        tools=tools,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "list_workspace_files": False,
                    "read_workspace_file": False,
                    "search_workspace_text": False,
                    "create_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                    "write_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                    "edit_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                },
                description_prefix="Tool execution pending approval",
            )
        ],
        checkpointer=InMemorySaver(),
        system_prompt=(
            "You are a helpful coding agent. Keep answers clear and concise. "
            "Use workspace tools when you need to inspect local files."
        ),
    )
    messages = []

    console.print(Panel.fit(f"Forge Agent\nModel: {config.model}\nType 'exit' or 'quit' to stop.", title="Ready"))

    while True:
        query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()

        if query.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye.[/yellow]")
            break

        if not query:
            console.print("[yellow]Please enter a question.[/yellow]")
            continue

        write_event(create_event("user_message", {"content": query}))
        messages.append({"role": "user", "content": query})
        agent_config = {"configurable": {"thread_id": f"forge-agent-local-{uuid4().hex}"}}
        result = agent.invoke({"messages": messages}, config=agent_config, version="v2")

        while getattr(result, "interrupts", None):
            decisions = ask_for_tool_decisions(result.interrupts, console)
            if has_rejection(decisions):
                answer = "Tool call rejected. I did not run the requested action."
                break

            result = agent.invoke(
                Command(resume={"decisions": decisions}),
                config=agent_config,
                version="v2",
            )
        else:
            answer = get_last_message_text(result)

        write_event(create_event("assistant_message", {"content": answer}))
        messages.append({"role": "assistant", "content": answer})
        console.print(Panel(answer, title="Agent", border_style="green"))


if __name__ == "__main__":
    main()

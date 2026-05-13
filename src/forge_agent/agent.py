import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from forge_agent.agent_tools import build_tools
from forge_agent.event_log import create_event, write_event
from forge_agent.human_review import ask_for_tool_decisions, has_rejection
from forge_agent.model_router import ModelSelection, route_model
from forge_agent.session_memory import append_message, clear_messages, load_or_create_session, save_session
from forge_agent.slash_commands import SlashCommandState, handle_slash_command


console = Console()
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_REASONING_MODEL = "gpt-4.1"


@dataclass
class AgentConfig:
    fast_model: str = DEFAULT_MODEL
    reasoning_model: str = DEFAULT_REASONING_MODEL


def load_config(workspace_root: Path) -> AgentConfig:
    config_path = workspace_root / ".forge-agent" / "config.toml"

    if not config_path.exists():
        return AgentConfig()

    with config_path.open("rb") as config_file:
        data = tomllib.load(config_file)

    fast_model = data.get("fast_model", data.get("model", DEFAULT_MODEL))
    reasoning_model = data.get("reasoning_model", fast_model)
    return AgentConfig(fast_model=fast_model, reasoning_model=reasoning_model)


def get_last_message_text(result: dict) -> str:
    if hasattr(result, "value"):
        result = result.value

    last_message = result["messages"][-1]
    content = last_message.content

    if isinstance(content, str):
        return content

    return str(content)


def build_system_prompt(selection: ModelSelection) -> str:
    prompt = (
        "You are a helpful coding agent. Keep answers clear and concise. "
        "Use workspace tools when you need to inspect local files."
    )

    if selection.should_plan:
        prompt += " For complex tasks, first break the work into smaller steps before making changes."

    return prompt


def main() -> None:
    workspace_root = Path.cwd().resolve()
    load_dotenv(dotenv_path=workspace_root / ".env", override=True)

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]OPENAI_API_KEY is not set. Add it to a .env file before running the agent.[/red]")
        return

    config = load_config(workspace_root)
    session_event = create_event(
        "session_started",
        {"fast_model": config.fast_model, "reasoning_model": config.reasoning_model},
    )
    write_event(session_event)

    tools = build_tools(workspace_root)
    session = load_or_create_session(workspace_root)
    messages = session.messages

    console.print(
        Panel.fit(
            f"Forge Agent\nWorkspace: {workspace_root}\n"
            f"Fast model: {config.fast_model}\nReasoning model: {config.reasoning_model}\n"
            "Type 'exit' or 'quit' to stop.",
            title="Ready",
        )
    )

    while True:
        query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()

        if query.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye.[/yellow]")
            break

        if not query:
            console.print("[yellow]Please enter a question.[/yellow]")
            continue

        if query.startswith("/"):
            slash_result = handle_slash_command(
                query,
                SlashCommandState(
                    workspace_root=workspace_root,
                    model=f"{config.fast_model} / {config.reasoning_model}",
                    message_count=len(messages),
                    messages=messages,
                ),
            )
            console.print(Panel(slash_result.output, title="Command", border_style="blue"))

            if slash_result.should_clear_messages:
                clear_messages(session)
                save_session(session)

            if slash_result.should_exit:
                break

            continue

        write_event(create_event("user_message", {"content": query}))
        append_message(session, "user", query)
        save_session(session)
        selection = route_model(query, config.fast_model, config.reasoning_model)
        console.print(
            f"[dim]Using {selection.task_complexity} route: {selection.model} ({selection.reason})[/dim]"
        )

        llm = ChatOpenAI(model=selection.model)
        agent = create_agent(
            model=llm,
            tools=tools,
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "list_workspace_files": False,
                        "read_workspace_file": False,
                        "search_workspace_text": False,
                        "retrieve_workspace_context": False,
                        "retrieve_workspace_memories": False,
                        "create_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                        "write_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                        "edit_workspace_file": {"allowed_decisions": ["approve", "reject"]},
                    },
                    description_prefix="Tool execution pending approval",
                )
            ],
            checkpointer=InMemorySaver(),
            system_prompt=build_system_prompt(selection),
        )

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
        append_message(session, "assistant", answer)
        save_session(session)
        console.print(Panel(answer, title="Agent", border_style="green"))


if __name__ == "__main__":
    main()

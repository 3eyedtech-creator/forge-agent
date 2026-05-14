import os
import sys
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
from forge_agent.approval_mode import ApprovalMode, build_interrupt_policy
from forge_agent.cli_args import get_version_text, resolve_startup_command
from forge_agent.event_log import create_event, write_event
from forge_agent.human_review import ask_for_tool_decisions, has_rejection
from forge_agent.model_router import ModelSelection, route_model
from forge_agent.session_memory import (
    append_message,
    clear_messages,
    clear_plan,
    load_or_create_session,
    save_session,
    set_plan,
)
from forge_agent.slash_commands import SlashCommandState, handle_slash_command
from forge_agent.task_planner import create_task_plan, format_task_plan
from forge_agent.terminal_ui import build_ready_text


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
        prompt += " Follow the active plan step by step, update progress when work changes, and replan if a step fails."

    return prompt


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    startup_command = resolve_startup_command(args)
    if startup_command == "version":
        console.print(get_version_text())
        return

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

    tools = build_tools(workspace_root, console=console)
    session = load_or_create_session(workspace_root)
    messages = session.messages
    approval_mode = ApprovalMode.MANUAL

    console.print(
        Panel.fit(
            build_ready_text(workspace_root, config.fast_model, config.reasoning_model, approval_mode),
            title="Forge",
            border_style="cyan",
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
                    active_plan=session.active_plan,
                    approval_mode=approval_mode,
                ),
            )
            console.print(Panel(slash_result.output, title="Command", border_style="blue"))

            if slash_result.next_approval_mode is not None:
                approval_mode = slash_result.next_approval_mode

            if slash_result.next_active_plan is not None:
                session.active_plan = slash_result.next_active_plan
                save_session(session)

            if slash_result.should_clear_messages:
                clear_messages(session)
                save_session(session)

            if slash_result.should_clear_plan:
                clear_plan(session)
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

        if selection.should_plan:
            plan = create_task_plan(query)
            plan.steps[0].status = "in_progress"
            plan.steps[0].notes = "Started task planning"
            formatted_plan = format_task_plan(plan)
            console.print(Panel(formatted_plan, title="Plan", border_style="magenta"))
            set_plan(session, plan)
            append_message(session, "system", formatted_plan)
            save_session(session)

        llm = ChatOpenAI(model=selection.model)
        agent = create_agent(
            model=llm,
            tools=tools,
            middleware=[
                HumanInTheLoopMiddleware(
                    interrupt_on=build_interrupt_policy(approval_mode),
                    description_prefix="Tool execution pending approval",
                )
            ],
            checkpointer=InMemorySaver(),
            system_prompt=build_system_prompt(selection),
        )

        agent_config = {"configurable": {"thread_id": f"forge-agent-local-{uuid4().hex}"}}
        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            result = agent.invoke({"messages": messages}, config=agent_config, version="v2")

        while getattr(result, "interrupts", None):
            decisions = ask_for_tool_decisions(result.interrupts, console)
            if has_rejection(decisions):
                answer = "Tool call rejected. I did not run the requested action."
                break

            with console.status("[bold cyan]Continuing...[/bold cyan]", spinner="dots"):
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

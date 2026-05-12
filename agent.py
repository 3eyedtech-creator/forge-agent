import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


console = Console()


def get_last_message_text(result: dict) -> str:
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

    llm = ChatOpenAI(model="gpt-4.1-mini")
    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt="You are a helpful coding agent. Keep answers clear and concise.",
    )
    messages = []

    console.print(Panel.fit("Forge Agent\nType 'exit' or 'quit' to stop.", title="Ready"))

    while True:
        query = Prompt.ask("[bold cyan]You[/bold cyan]").strip()

        if query.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye.[/yellow]")
            break

        if not query:
            console.print("[yellow]Please enter a question.[/yellow]")
            continue

        messages.append({"role": "user", "content": query})
        result = agent.invoke({"messages": messages})
        answer = get_last_message_text(result)

        messages.append({"role": "assistant", "content": answer})
        console.print(Panel(answer, title="Agent", border_style="green"))


if __name__ == "__main__":
    main()

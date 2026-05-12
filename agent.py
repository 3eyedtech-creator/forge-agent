import os

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


def main() -> None:
    load_dotenv(override=True)

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set. Add it to a .env file before running the agent.")
        return

    query = input("Ask the agent: ").strip()
    if not query:
        print("No query provided.")
        return

    llm = ChatOpenAI(model="gpt-4.1-mini")
    response = llm.invoke(query)

    print()
    print(response.content)


if __name__ == "__main__":
    main()

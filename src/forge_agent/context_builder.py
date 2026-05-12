from forge_agent.retrieval_engine import RetrievedContextItem


def build_context_section(items: list[RetrievedContextItem], max_tokens: int = 2_000) -> str:
    if not items:
        return "No relevant repository context was retrieved."

    included_sections = []
    used_tokens = 0
    omitted_count = 0

    for item in items:
        if used_tokens + item.token_estimate > max_tokens:
            omitted_count += 1
            continue

        included_sections.append(format_context_item(item))
        used_tokens += item.token_estimate

    lines = ["Relevant repository context:"]
    lines.extend(included_sections)

    if omitted_count:
        lines.append(f"Some retrieved context was omitted due to the token budget. Omitted items: {omitted_count}.")

    return "\n\n".join(lines)


def format_context_item(item: RetrievedContextItem) -> str:
    return (
        f"File: {item.path} lines {item.start_line}-{item.end_line}\n"
        f"Score: {item.score}\n"
        f"Reason: {item.reason}\n"
        "Content:\n"
        f"{item.content}"
    )

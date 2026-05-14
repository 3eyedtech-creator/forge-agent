def format_task_report(
    changed_files: list[dict],
    commands_run: list[dict],
    risks: list[str],
) -> str:
    lines = ["Summary", "- Current task report for this workspace session."]

    lines.append("")
    lines.append("Files Changed")
    if changed_files:
        for item in changed_files:
            lines.append(f"- {item.get('action', 'changed')}: {item.get('path', '<unknown>')}")
    else:
        lines.append("- No file changes recorded.")

    lines.append("")
    lines.append("Commands Run")
    if commands_run:
        for item in commands_run:
            command = item.get("command", "<unknown>")
            exit_code = item.get("exit_code", "unknown")
            lines.append(f"- {command} (exit {exit_code})")
    else:
        lines.append("- No terminal commands recorded.")

    lines.append("")
    lines.append("Verification")
    verification_commands = [item for item in commands_run if item.get("kind") == "verification"]
    if verification_commands:
        for item in verification_commands:
            lines.append(f"- {item.get('command', '<unknown>')} (exit {item.get('exit_code', 'unknown')})")
    else:
        lines.append("- Verification not recorded yet.")

    lines.append("")
    lines.append("Risks")
    if risks:
        lines.extend(f"- {risk}" for risk in risks)
    else:
        lines.append("- No risks recorded.")

    lines.append("")
    lines.append("Next Steps")
    lines.append("- Review changed files and run relevant verification commands.")

    return "\n".join(lines)

from forge_agent import __version__


def get_version_text() -> str:
    return f"forge-agent {__version__}"


def resolve_startup_command(args: list[str]) -> str | None:
    if args in (["--version"], ["-V"], ["version"]):
        return "version"

    return None

from pathlib import Path


class PathOutsideWorkspaceError(ValueError):
    pass


def resolve_workspace_path(workspace_root: Path, user_path: str | Path) -> Path:
    root = workspace_root.resolve()
    requested_path = Path(user_path)

    if requested_path.is_absolute():
        resolved_path = requested_path.resolve()
    else:
        resolved_path = (root / requested_path).resolve()

    if resolved_path == root or root in resolved_path.parents:
        return resolved_path

    raise PathOutsideWorkspaceError(f"Path is outside workspace: {user_path}")

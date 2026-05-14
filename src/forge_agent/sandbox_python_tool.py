import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    sandbox_path: Path


def run_python_sandbox(
    workspace_root: Path,
    code: str,
    timeout_seconds: float = 5,
) -> SandboxResult:
    workspace_root.resolve()
    safe_env = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    }
    if "SystemRoot" in os.environ:
        safe_env["SystemRoot"] = os.environ["SystemRoot"]

    with TemporaryDirectory(prefix="forge-python-sandbox-") as temp_dir:
        sandbox_path = Path(temp_dir)
        script_path = sandbox_path / "snippet.py"
        script_path.write_text(code, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=sandbox_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=safe_env,
            )
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            return SandboxResult(
                exit_code=-1,
                stdout=stdout,
                stderr=f"{stderr}\nTimed out after {timeout_seconds} seconds.".strip(),
                sandbox_path=sandbox_path,
            )

        return SandboxResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            sandbox_path=sandbox_path,
        )

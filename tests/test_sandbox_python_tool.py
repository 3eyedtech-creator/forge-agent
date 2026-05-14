import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.sandbox_python_tool import run_python_sandbox


class SandboxPythonToolTests(unittest.TestCase):
    def test_sandbox_captures_stdout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_python_sandbox(Path(temp_dir), "print('hello sandbox')")

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "hello sandbox")
        self.assertEqual(result.stderr, "")

    def test_sandbox_captures_stderr_and_exit_code(self) -> None:
        code = "import sys\nprint('bad', file=sys.stderr)\nsys.exit(3)"

        with TemporaryDirectory() as temp_dir:
            result = run_python_sandbox(Path(temp_dir), code)

        self.assertEqual(result.exit_code, 3)
        self.assertEqual(result.stderr.strip(), "bad")

    def test_sandbox_runs_outside_workspace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            result = run_python_sandbox(workspace, "import os\nprint(os.getcwd())")

        self.assertEqual(result.exit_code, 0)
        self.assertNotEqual(Path(result.stdout.strip()).resolve(), workspace.resolve())

    def test_sandbox_enforces_timeout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            result = run_python_sandbox(
                Path(temp_dir),
                "import time\ntime.sleep(2)",
                timeout_seconds=0.1,
            )

        self.assertEqual(result.exit_code, -1)
        self.assertIn("Timed out", result.stderr)


if __name__ == "__main__":
    unittest.main()

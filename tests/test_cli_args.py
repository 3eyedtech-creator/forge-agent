import unittest

from forge_agent import __version__
from forge_agent.cli_args import get_version_text, resolve_startup_command


class CliArgsTests(unittest.TestCase):
    def test_version_text_uses_package_version(self) -> None:
        self.assertEqual(get_version_text(), f"forge-agent {__version__}")

    def test_resolve_startup_command_detects_version_flags(self) -> None:
        self.assertEqual(resolve_startup_command(["--version"]), "version")
        self.assertEqual(resolve_startup_command(["version"]), "version")

    def test_resolve_startup_command_continues_chat_for_no_args(self) -> None:
        self.assertIsNone(resolve_startup_command([]))


if __name__ == "__main__":
    unittest.main()

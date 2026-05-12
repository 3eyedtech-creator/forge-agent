import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.slash_commands import SlashCommandState, handle_slash_command


class SlashCommandsTests(unittest.TestCase):
    def test_help_command_lists_commands(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/help", state)

        self.assertFalse(result.should_exit)
        self.assertIn("/index", result.output)
        self.assertIn("/retrieve", result.output)

    def test_status_command_shows_workspace_model_and_messages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=2)

            result = handle_slash_command("/status", state)

        self.assertIn("gpt-test", result.output)
        self.assertIn("Messages: 2", result.output)

    def test_index_command_builds_index(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/index", state)

        self.assertIn("Indexed files: 1", result.output)
        self.assertIn("Chunks: 1", result.output)

    def test_retrieve_command_returns_context(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "auth.py").write_text("def login_user():\n    pass\n", encoding="utf-8")
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            handle_slash_command("/index", state)
            result = handle_slash_command("/retrieve login", state)

        self.assertIn("Relevant repository context:", result.output)
        self.assertIn("auth.py", result.output)

    def test_clear_command_requests_message_clear(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=2)

            result = handle_slash_command("/clear", state)

        self.assertTrue(result.should_clear_messages)

    def test_exit_command_requests_exit(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/exit", state)

        self.assertTrue(result.should_exit)


if __name__ == "__main__":
    unittest.main()

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

    def test_session_clear_command_requests_message_clear(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=2)

            result = handle_slash_command("/session clear", state)

        self.assertTrue(result.should_clear_messages)

    def test_session_path_command_shows_session_file_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/session path", state)

        self.assertIn(".forge-agent", result.output)
        self.assertIn("current.json", result.output)

    def test_session_show_command_lists_saved_messages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=2,
                messages=[
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "hi"},
                ],
            )

            result = handle_slash_command("/session show", state)

        self.assertIn("user: hello", result.output)
        self.assertIn("assistant: hi", result.output)

    def test_exit_command_requests_exit(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/exit", state)

        self.assertTrue(result.should_exit)

    def test_memory_add_and_list_commands(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            add_result = handle_slash_command("/memory add Use pip instead of uv.", state)
            list_result = handle_slash_command("/memory list", state)

        self.assertIn("Memory added", add_result.output)
        self.assertIn("Use pip instead of uv.", list_result.output)

    def test_memory_clear_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            handle_slash_command("/memory add Remember this.", state)
            clear_result = handle_slash_command("/memory clear", state)
            list_result = handle_slash_command("/memory list", state)

        self.assertIn("Memories cleared", clear_result.output)
        self.assertIn("No memories found", list_result.output)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.approval_mode import ApprovalMode
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

    def test_mode_command_shows_current_approval_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                approval_mode=ApprovalMode.AUTO,
            )

            result = handle_slash_command("/mode", state)

        self.assertIn("Approval mode: auto", result.output)

    def test_mode_auto_command_requests_auto_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/mode auto", state)

        self.assertEqual(result.next_approval_mode, ApprovalMode.AUTO)
        self.assertIn("Approval mode set to auto", result.output)

    def test_mode_manual_command_requests_manual_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/mode manual", state)

        self.assertEqual(result.next_approval_mode, ApprovalMode.MANUAL)
        self.assertIn("Approval mode set to manual", result.output)

    def test_mode_command_rejects_unknown_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/mode dangerous", state)

        self.assertEqual(result.output, "Usage: /mode [manual|auto]")

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

    def test_run_command_executes_safe_terminal_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/run git status", state)

        self.assertIn("Command: git status", result.output)
        self.assertIn("Exit code:", result.output)

    def test_run_command_requires_command_text(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/run", state)

        self.assertEqual(result.output, "Usage: /run <command>")

    def test_python_command_runs_code_in_sandbox(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/python print('hello')", state)

        self.assertIn("Exit code: 0", result.output)
        self.assertIn("STDOUT:\nhello", result.output)

    def test_python_command_requires_code(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/python", state)

        self.assertEqual(result.output, "Usage: /python <code>")

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

    def test_plan_show_command_displays_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                active_plan={
                    "goal": "fix login",
                    "steps": [{"description": "Inspect files", "status": "pending"}],
                },
            )

            result = handle_slash_command("/plan show", state)

        self.assertIn("Plan: fix login", result.output)
        self.assertIn("Inspect files", result.output)

    def test_plan_clear_command_requests_plan_clear(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/plan clear", state)

        self.assertTrue(result.should_clear_plan)

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

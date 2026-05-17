import unittest
import json
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

    def test_skills_list_command_displays_available_skills(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/skills list", state)

        self.assertIn("bugfix", result.output)
        self.assertIn("explain-code", result.output)
        self.assertIn("git", result.output)
        self.assertIn("github", result.output)

    def test_skills_show_command_displays_skill_body(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/skills show bugfix", state)

        self.assertIn("Skill: bugfix", result.output)
        self.assertIn("When fixing a bug", result.output)

    def test_skill_command_selects_active_skill(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/skill bugfix", state)

        self.assertEqual(result.next_active_skill, "bugfix")
        self.assertIn("Active skill set to bugfix", result.output)

    def test_skill_command_reports_unknown_skill(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/skill missing", state)

        self.assertEqual(result.output, "Unknown skill: missing")

    def test_mcp_list_command_displays_configured_servers(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / ".forge-agent").mkdir()
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps({"servers": {"docs": {"enabled": True, "transport": "streamable_http", "url": "http://localhost:8000/mcp"}}}),
                encoding="utf-8",
            )
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/mcp list", state)

        self.assertIn("docs [enabled] streamable_http", result.output)

    def test_mcp_show_command_redacts_secret_values(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / ".forge-agent").mkdir()
            (workspace / ".forge-agent" / "mcp.json").write_text(
                json.dumps(
                    {
                        "servers": {
                            "docs": {
                                "enabled": True,
                                "transport": "streamable_http",
                                "url": "http://localhost:8000/mcp",
                                "headers": {"Authorization": "secret"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/mcp show docs", state)

        self.assertIn("Server: docs", result.output)
        self.assertIn("Authorization: <redacted>", result.output)
        self.assertNotIn("secret", result.output)

    def test_mcp_show_command_reports_unknown_server(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/mcp show missing", state)

        self.assertEqual(result.output, "Unknown MCP server: missing")

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
        self.assertIsNotNone(result.command_run)
        self.assertEqual(result.command_run["command"], "git status")

    def test_run_command_requires_command_text(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/run", state)

        self.assertEqual(result.output, "Usage: /run <command>")

    def test_git_status_command_runs_and_records_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/git status", state)

        self.assertIn("Command: git status --short", result.output)
        self.assertEqual(result.command_run["command"], "git status --short")

    def test_git_add_command_runs_and_records_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))
            (workspace / "notes.txt").write_text("notes\n", encoding="utf-8")
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/git add notes.txt", state)

        self.assertIn("Command: git add -- notes.txt", result.output)
        self.assertEqual(result.command_run["command"], "git add -- notes.txt")

    def test_git_commit_command_runs_and_records_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = init_git_repo(Path(temp_dir))
            (workspace / "notes.txt").write_text("notes\n", encoding="utf-8")
            handle_slash_command("/git add notes.txt", SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0))
            state = SlashCommandState(workspace_root=workspace, model="gpt-test", message_count=0)

            result = handle_slash_command("/git commit add notes", state)

        self.assertIn("Command: git commit -m add notes", result.output)
        self.assertEqual(result.command_run["command"], "git commit -m add notes")

    def test_git_command_rejects_unsupported_operation(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/git reset --hard", state)

        self.assertEqual(result.output, "Usage: /git <status|diff|log|branch|add|commit>")

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

    def test_report_command_displays_session_report(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                changed_files=[{"path": "app.py", "action": "edited"}],
                commands_run=[{"command": "python -m unittest", "exit_code": 0, "kind": "verification"}],
                report_risks=["No integration test yet."],
            )

            result = handle_slash_command("/report", state)

        self.assertIn("Files Changed", result.output)
        self.assertIn("edited: app.py", result.output)
        self.assertIn("python -m unittest (exit 0)", result.output)
        self.assertIn("No integration test yet.", result.output)

    def test_plan_show_command_displays_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                active_plan={
                    "goal": "fix login",
                    "steps": [{"id": "step_1", "description": "Inspect files", "status": "pending", "notes": ""}],
                    "risks": [],
                    "updated_at": "now",
                },
            )

            result = handle_slash_command("/plan show", state)

        self.assertIn("Plan: fix login", result.output)
        self.assertIn("step_1. [pending]", result.output)
        self.assertIn("Inspect files", result.output)

    def test_plan_update_command_updates_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                active_plan={
                    "goal": "fix login",
                    "steps": [{"id": "step_1", "description": "Inspect files", "status": "pending", "notes": ""}],
                    "risks": [],
                    "updated_at": "now",
                },
            )

            result = handle_slash_command("/plan update step_1 completed Read auth files", state)

        self.assertIsNotNone(result.next_active_plan)
        self.assertEqual(result.next_active_plan["steps"][0]["status"], "completed")
        self.assertEqual(result.next_active_plan["steps"][0]["notes"], "Read auth files")
        self.assertIn("Updated step_1 to completed", result.output)

    def test_plan_update_command_reports_missing_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(workspace_root=Path(temp_dir), model="gpt-test", message_count=0)

            result = handle_slash_command("/plan update step_1 completed", state)

        self.assertEqual(result.output, "No active plan.")

    def test_plan_update_command_reports_invalid_usage(self) -> None:
        with TemporaryDirectory() as temp_dir:
            state = SlashCommandState(
                workspace_root=Path(temp_dir),
                model="gpt-test",
                message_count=0,
                active_plan={
                    "goal": "fix login",
                    "steps": [{"id": "step_1", "description": "Inspect files", "status": "pending", "notes": ""}],
                    "risks": [],
                    "updated_at": "now",
                },
            )

            result = handle_slash_command("/plan update step_1 started", state)

        self.assertEqual(result.output, "Usage: /plan update <step_id> <pending|in_progress|completed|failed> [notes]")

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


def init_git_repo(workspace: Path) -> Path:
    import subprocess

    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "forge@example.com"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Forge Tests"], cwd=workspace, check=True)
    (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=workspace, check=True, capture_output=True, text=True)
    return workspace

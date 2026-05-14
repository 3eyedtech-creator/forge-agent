import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.session_memory import (
    append_message,
    add_changed_file,
    add_command_run,
    add_report_risk,
    clear_messages,
    clear_plan,
    load_or_create_session,
    save_session,
    set_plan,
    update_active_plan,
)
from forge_agent.task_planner import create_task_plan


class SessionMemoryTests(unittest.TestCase):
    def test_creates_new_session_when_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            session = load_or_create_session(workspace)

        self.assertTrue(session.session_id.startswith("ses_"))
        self.assertEqual(session.workspace_root, str(workspace.resolve()))
        self.assertEqual(session.messages, [])
        self.assertEqual(session.changed_files, [])
        self.assertEqual(session.commands_run, [])
        self.assertEqual(session.report_risks, [])

    def test_appends_and_persists_messages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)
            append_message(session, "user", "hello")
            save_session(session)

            loaded = load_or_create_session(workspace)

        self.assertEqual(loaded.messages, [{"role": "user", "content": "hello"}])

    def test_clear_messages_persists_empty_messages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)
            append_message(session, "user", "hello")
            clear_messages(session)
            save_session(session)

            loaded = load_or_create_session(workspace)

        self.assertEqual(loaded.messages, [])

    def test_stores_and_clears_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)
            plan = create_task_plan("fix login")

            set_plan(session, plan)
            save_session(session)
            loaded = load_or_create_session(workspace)

            self.assertEqual(loaded.active_plan["goal"], "fix login")
            self.assertEqual(loaded.active_plan["steps"][0]["id"], "step_1")
            self.assertIn("risks", loaded.active_plan)

            clear_plan(loaded)
            save_session(loaded)
            reloaded = load_or_create_session(workspace)

        self.assertIsNone(reloaded.active_plan)

    def test_updates_and_persists_active_plan(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)
            set_plan(session, create_task_plan("fix login"))

            update_active_plan(session, "step_1", "completed", "Found auth flow")
            save_session(session)
            loaded = load_or_create_session(workspace)

        self.assertEqual(loaded.active_plan["steps"][0]["status"], "completed")
        self.assertEqual(loaded.active_plan["steps"][0]["notes"], "Found auth flow")

    def test_tracks_changed_files_commands_and_report_risks(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)

            add_changed_file(session, "app.py", "edited")
            add_command_run(session, "python -m unittest", 0, kind="verification")
            add_report_risk(session, "Coverage is still thin.")
            save_session(session)
            loaded = load_or_create_session(workspace)

        self.assertEqual(loaded.changed_files, [{"path": "app.py", "action": "edited"}])
        self.assertEqual(
            loaded.commands_run,
            [{"command": "python -m unittest", "exit_code": 0, "kind": "verification"}],
        )
        self.assertEqual(loaded.report_risks, ["Coverage is still thin."])

    def test_changed_files_are_deduplicated_by_path_and_action(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            session = load_or_create_session(workspace)

            add_changed_file(session, "app.py", "edited")
            add_changed_file(session, "app.py", "edited")

        self.assertEqual(session.changed_files, [{"path": "app.py", "action": "edited"}])


if __name__ == "__main__":
    unittest.main()

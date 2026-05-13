import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.session_memory import (
    append_message,
    clear_messages,
    clear_plan,
    load_or_create_session,
    save_session,
    set_plan,
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

            clear_plan(loaded)
            save_session(loaded)
            reloaded = load_or_create_session(workspace)

        self.assertIsNone(reloaded.active_plan)


if __name__ == "__main__":
    unittest.main()

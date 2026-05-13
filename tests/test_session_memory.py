import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.session_memory import append_message, clear_messages, load_or_create_session, save_session


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


if __name__ == "__main__":
    unittest.main()

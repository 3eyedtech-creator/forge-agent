import json
import unittest

from event_log import create_event, write_event


class EventLogTests(unittest.TestCase):
    def test_create_event_includes_id_type_timestamp_and_data(self) -> None:
        event = create_event("session_started", {"model": "gpt-4.1-mini"})

        self.assertTrue(event["id"].startswith("evt_"))
        self.assertEqual(event["type"], "session_started")
        self.assertIn("timestamp", event)
        self.assertEqual(event["data"], {"model": "gpt-4.1-mini"})

    def test_write_event_appends_json_line(self) -> None:
        event = create_event("user_message", {"content": "hello"})

        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "events.jsonl"
            write_event(event, log_path)

            written = json.loads(log_path.read_text().strip())

        self.assertEqual(written, event)


if __name__ == "__main__":
    unittest.main()

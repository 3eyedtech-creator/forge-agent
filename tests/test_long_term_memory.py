import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.long_term_memory import add_memory, clear_memories, list_memories, retrieve_memories


class LongTermMemoryTests(unittest.TestCase):
    def test_adds_and_lists_memory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)

            memory = add_memory(workspace, "Use pip instead of uv.", kind="preference")
            memories = list_memories(workspace)

        self.assertTrue(memory.id.startswith("mem_"))
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].text, "Use pip instead of uv.")
        self.assertEqual(memories[0].kind, "preference")
        self.assertEqual(memories[0].scope, "workspace")

    def test_returns_empty_list_when_memory_file_is_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            memories = list_memories(Path(temp_dir))

        self.assertEqual(memories, [])

    def test_clears_memories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            add_memory(workspace, "Remember this.")

            clear_memories(workspace)
            memories = list_memories(workspace)

        self.assertEqual(memories, [])

    def test_retrieves_matching_memories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            add_memory(workspace, "Use pip instead of uv.", kind="preference")
            add_memory(workspace, "Frontend uses React.", kind="fact")

            memories = retrieve_memories(workspace, "dependency install pip")

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].text, "Use pip instead of uv.")

    def test_limits_retrieved_memories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            add_memory(workspace, "Use pip for installs.")
            add_memory(workspace, "Run pip in a venv.")

            memories = retrieve_memories(workspace, "pip", max_items=1)

        self.assertEqual(len(memories), 1)


if __name__ == "__main__":
    unittest.main()

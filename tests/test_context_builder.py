import unittest

from forge_agent.context_builder import build_context_section
from forge_agent.retrieval_engine import RetrievedContextItem


class ContextBuilderTests(unittest.TestCase):
    def test_formats_retrieved_context_items(self) -> None:
        item = make_item(
            path="auth.py",
            start_line=1,
            end_line=2,
            content="1: def login():\n2:     pass",
            reason="content match",
        )

        context = build_context_section([item])

        self.assertIn("Relevant repository context:", context)
        self.assertIn("File: auth.py lines 1-2", context)
        self.assertIn("Reason: content match", context)
        self.assertIn("1: def login():", context)

    def test_returns_empty_context_message_when_no_items_exist(self) -> None:
        context = build_context_section([])

        self.assertEqual(context, "No relevant repository context was retrieved.")

    def test_respects_token_budget(self) -> None:
        items = [
            make_item(path="a.py", token_estimate=8),
            make_item(path="b.py", token_estimate=8),
        ]

        context = build_context_section(items, max_tokens=10)

        self.assertIn("File: a.py", context)
        self.assertNotIn("File: b.py", context)
        self.assertIn("Some retrieved context was omitted due to the token budget.", context)


def make_item(
    path: str = "app.py",
    start_line: int = 1,
    end_line: int = 1,
    content: str = "1: content",
    score: float = 1.0,
    reason: str = "content match",
    token_estimate: int = 3,
) -> RetrievedContextItem:
    return RetrievedContextItem(
        path=path,
        start_line=start_line,
        end_line=end_line,
        content=content,
        score=score,
        reason=reason,
        token_estimate=token_estimate,
    )


if __name__ == "__main__":
    unittest.main()

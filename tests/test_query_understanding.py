import unittest

from forge_agent.query_understanding import understand_query


class QueryUnderstandingTests(unittest.TestCase):
    def test_detects_task_type(self) -> None:
        self.assertEqual(understand_query("explain auth flow").task_type, "explain")
        self.assertEqual(understand_query("fix failing login test").task_type, "fix")
        self.assertEqual(understand_query("add password reset").task_type, "implement")
        self.assertEqual(understand_query("refactor billing service").task_type, "refactor")

    def test_extracts_search_terms_without_stop_words(self) -> None:
        result = understand_query("how does the login flow work in this repo")

        self.assertEqual(result.search_terms, ["login", "flow", "work", "repo"])

    def test_extracts_quoted_phrases(self) -> None:
        result = understand_query('find "invalid password" error')

        self.assertEqual(result.phrases, ["invalid password"])
        self.assertIn("invalid", result.search_terms)
        self.assertIn("password", result.search_terms)

    def test_extracts_likely_paths(self) -> None:
        result = understand_query("open src/auth/login.py and README.md")

        self.assertEqual(result.likely_paths, ["src/auth/login.py", "README.md"])

    def test_detects_likely_test_names(self) -> None:
        result = understand_query("fix test_login_user failure")

        self.assertEqual(result.test_terms, ["test_login_user"])


if __name__ == "__main__":
    unittest.main()

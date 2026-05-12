import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from forge_agent.repository_scanner import scan_repository


class RepositoryScannerTests(unittest.TestCase):
    def test_scans_file_metadata(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "app.py").write_text("print('hello')\n", encoding="utf-8")

            result = scan_repository(workspace)

        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, "app.py")
        self.assertEqual(result.files[0].extension, ".py")
        self.assertEqual(result.files[0].language, "python")
        self.assertEqual(result.files[0].kind, "source")

    def test_skips_excluded_directories(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "app.py").write_text("", encoding="utf-8")
            (workspace / ".git").mkdir()
            (workspace / ".git" / "ignored").write_text("", encoding="utf-8")
            (workspace / ".venv").mkdir()
            (workspace / ".venv" / "ignored.py").write_text("", encoding="utf-8")

            result = scan_repository(workspace)

        self.assertEqual([file.path for file in result.files], ["app.py"])

    def test_classifies_common_file_kinds(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "README.md").write_text("", encoding="utf-8")
            (workspace / "pyproject.toml").write_text("", encoding="utf-8")
            (workspace / "test_app.py").write_text("", encoding="utf-8")

            result = scan_repository(workspace)

        kinds = {file.path: file.kind for file in result.files}
        self.assertEqual(kinds["README.md"], "doc")
        self.assertEqual(kinds["pyproject.toml"], "config")
        self.assertEqual(kinds["test_app.py"], "test")

    def test_detects_popular_languages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            files = {
                "app.ts": "typescript",
                "component.tsx": "typescript-react",
                "server.js": "javascript",
                "view.jsx": "javascript-react",
                "main.go": "go",
                "lib.rs": "rust",
                "Main.java": "java",
                "app.kt": "kotlin",
                "service.cs": "csharp",
                "main.cpp": "cpp",
                "main.c": "c",
                "style.css": "css",
                "index.html": "html",
                "data.json": "json",
                "query.sql": "sql",
                "script.sh": "shell",
            }
            for path in files:
                (workspace / path).write_text("", encoding="utf-8")

            result = scan_repository(workspace)

        languages = {file.path: file.language for file in result.files}
        for path, language in files.items():
            self.assertEqual(languages[path], language)

    def test_classifies_tests_for_common_languages(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            for path in ["app.test.ts", "app.spec.js", "example_test.go", "lib_test.rs", "UserServiceTest.java"]:
                (workspace / path).write_text("", encoding="utf-8")

            result = scan_repository(workspace)

        kinds = {file.path: file.kind for file in result.files}
        for path in kinds:
            self.assertEqual(kinds[path], "test")


if __name__ == "__main__":
    unittest.main()

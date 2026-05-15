import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageMetadataTests(unittest.TestCase):
    def test_builtin_skill_markdown_files_are_packaged(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        package_data = pyproject["tool"]["setuptools"]["package-data"]

        self.assertIn("builtin_skills/*/SKILL.md", package_data["forge_agent"])

    def test_mcp_adapter_dependency_is_declared(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertIn("langchain-mcp-adapters", pyproject["project"]["dependencies"])


if __name__ == "__main__":
    unittest.main()

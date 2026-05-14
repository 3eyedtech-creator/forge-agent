import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/3eyedtech-creator/forge-agent.git"


class InstallScriptsTests(unittest.TestCase):
    def test_unix_install_script_uses_pipx_and_github_package_url(self) -> None:
        script = (ROOT / "install.sh").read_text(encoding="utf-8")

        self.assertTrue(script.startswith("#!/usr/bin/env bash"))
        self.assertIn("set -euo pipefail", script)
        self.assertIn("FORGE_AGENT_REPO_URL=", script)
        self.assertIn("python3 -m pipx install", script)
        self.assertIn(f"git+${{FORGE_AGENT_REPO_URL}}", script)
        self.assertIn(REPO_URL, script)
        self.assertNotIn("YOUR_USERNAME", script)
        self.assertIn("forge", script)

    def test_powershell_install_script_uses_pipx_and_github_package_url(self) -> None:
        script = (ROOT / "install.ps1").read_text(encoding="utf-8")

        self.assertIn("Set-StrictMode -Version Latest", script)
        self.assertIn("$ForgeAgentRepoUrl", script)
        self.assertIn("pipx install", script)
        self.assertIn("git+$ForgeAgentRepoUrl", script)
        self.assertIn(REPO_URL, script)
        self.assertNotIn("YOUR_USERNAME", script)
        self.assertIn("forge", script)


if __name__ == "__main__":
    unittest.main()

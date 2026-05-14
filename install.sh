#!/usr/bin/env bash
set -euo pipefail

FORGE_AGENT_REPO_URL="${FORGE_AGENT_REPO_URL:-https://github.com/3eyedtech-creator/forge-agent.git}"
PACKAGE_SPEC="git+${FORGE_AGENT_REPO_URL}"

echo "Installing forge-agent..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

if ! python3 -m pipx --version >/dev/null 2>&1; then
  echo "pipx was not found. Installing pipx for the current user..."
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
fi

python3 -m pipx install "${PACKAGE_SPEC}" --force

echo "forge-agent installed."
echo "Run it from any repository with: forge"

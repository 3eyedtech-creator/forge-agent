Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ForgeAgentRepoUrl = if ($env:FORGE_AGENT_REPO_URL) {
    $env:FORGE_AGENT_REPO_URL
} else {
    "https://github.com/3eyedtech-creator/forge-agent.git"
}
$PackageSpec = "git+$ForgeAgentRepoUrl"

Write-Host "Installing forge-agent..."

$PythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $PythonCommand) {
    $Python = "py"
} elseif ($null -ne (Get-Command python -ErrorAction SilentlyContinue)) {
    $Python = "python"
} else {
    Write-Error "Python is required but was not found."
    exit 1
}

& $Python -m pipx --version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "pipx was not found. Installing pipx for the current user..."
    & $Python -m pip install --user pipx
    & $Python -m pipx ensurepath
}

& $Python -m pipx install $PackageSpec --force

Write-Host "forge-agent installed."
Write-Host "Run it from any repository with: forge"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
python -m frigg_mcp.server.stdio
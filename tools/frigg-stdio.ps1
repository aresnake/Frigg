$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
& "$repoRoot\.venv\Scripts\pythonw.exe" -m frigg_mcp.server.stdio
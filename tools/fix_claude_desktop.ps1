# Fix Claude Desktop MCP Cache
# This script completely cleans Claude Desktop cache and restarts it

Write-Host "=== Claude Desktop MCP Cache Cleaner ===" -ForegroundColor Cyan

# Step 1: Kill Claude Desktop
Write-Host "`n[1/4] Stopping Claude Desktop..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.Name -eq 'Claude'} | ForEach-Object {
    Write-Host "  Killing process: $($_.Id)" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force
}
Start-Sleep -Seconds 2

# Step 2: Clear caches
Write-Host "`n[2/4] Clearing caches..." -ForegroundColor Yellow
$cachePaths = @(
    "$env:APPDATA\Claude\Cache",
    "$env:APPDATA\Claude\GPUCache",
    "$env:APPDATA\Claude\Code Cache",
    "$env:LOCALAPPDATA\Claude\Cache"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        Write-Host "  Removing: $path" -ForegroundColor Gray
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Step 3: Verify MCP config
Write-Host "`n[3/4] Verifying MCP configuration..." -ForegroundColor Yellow
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    Write-Host "  MCP servers configured:" -ForegroundColor Gray
    $config.mcpServers.PSObject.Properties | ForEach-Object {
        Write-Host "    - $($_.Name)" -ForegroundColor Green
    }
} else {
    Write-Host "  WARNING: No config file found!" -ForegroundColor Red
}

# Step 4: Check Python server
Write-Host "`n[4/4] Testing Python MCP server..." -ForegroundColor Yellow
$venvPython = "D:\Frigg\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "  Python found: $venvPython" -ForegroundColor Green

    # Test tool names
    $testScript = @"
import sys
sys.path.insert(0, 'D:/Frigg/src')
from frigg_mcp.tools import core_tools
import re

pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
valid = all(pattern.match(t['name']) for t in core_tools.CORE_TOOL_DEFS)
print('VALID' if valid else 'INVALID')
"@

    $result = & $venvPython -c $testScript
    if ($result -eq 'VALID') {
        Write-Host "  Tool names: VALID" -ForegroundColor Green
    } else {
        Write-Host "  Tool names: INVALID" -ForegroundColor Red
    }
} else {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
}

Write-Host "`n=== Done! ===" -ForegroundColor Cyan
Write-Host "Now restart Claude Desktop manually." -ForegroundColor Yellow
Write-Host "Wait 10 seconds after launch, then test: 'List objects in Blender'" -ForegroundColor Yellow

# Test script for Frigg MCP server
# This tests the MCP server end-to-end

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

Write-Host "Testing Frigg MCP Server..." -ForegroundColor Cyan
Write-Host "Python: $pythonExe" -ForegroundColor Gray

# Test 1: Initialize
Write-Host "`n[TEST 1] Initialize..." -ForegroundColor Yellow
$initRequest = '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
$initResponse = $initRequest | & $pythonExe -m frigg_mcp.server.stdio 2>&1 | Select-String -Pattern '"id":\s*0'
if ($initResponse) {
    Write-Host "[PASS] Initialize succeeded" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Initialize failed" -ForegroundColor Red
    exit 1
}

# Test 2: Full sequence
Write-Host "`n[TEST 2] Full MCP sequence..." -ForegroundColor Yellow
$sequence = @(
    '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
    '{"jsonrpc":"2.0","method":"initialized"}'
    '{"jsonrpc":"2.0","id":1,"method":"ping"}'
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
    '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"frigg.ping","arguments":{}}}'
)

$output = ($sequence -join "`n") | & $pythonExe -m frigg_mcp.server.stdio 2>&1
$jsonResponses = $output | Select-String -Pattern '^\{' | ForEach-Object { $_.Line }

if ($jsonResponses.Count -ge 4) {
    Write-Host "[PASS] Received $($jsonResponses.Count) responses" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Expected at least 4 responses, got $($jsonResponses.Count)" -ForegroundColor Red
    Write-Host "Output:" -ForegroundColor Gray
    $output | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    exit 1
}

# Test 3: Check logs
Write-Host "`n[TEST 3] Check log file..." -ForegroundColor Yellow
$logFile = Join-Path $repoRoot "logs\frigg_mcp_server.log"
if (Test-Path $logFile) {
    $lastLog = Get-Content $logFile -Tail 1
    Write-Host "[PASS] Log file exists: $logFile" -ForegroundColor Green
    Write-Host "Last log entry: $lastLog" -ForegroundColor Gray
} else {
    Write-Host "[FAIL] Log file not found: $logFile" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All tests passed! MCP server is ready." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

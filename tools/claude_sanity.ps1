$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not $env:PYTHONPATH) {
    $env:PYTHONPATH = Join-Path $repoRoot "src"
}

$statePath = Join-Path $repoRoot ".frigg_bridge.json"
$bridgeHost = $env:FRIGG_BRIDGE_HOST
$port = $env:FRIGG_BRIDGE_PORT

if (-not $port -and (Test-Path $statePath)) {
    try {
        $state = Get-Content -Raw $statePath | ConvertFrom-Json
        if (-not $bridgeHost) {
            $bridgeHost = $state.host
        }
        $port = $state.port
    } catch {
        $port = $null
    }
}

if (-not $bridgeHost) {
    $bridgeHost = "127.0.0.1"
}

if (-not $port) {
    Write-Output "KO: bridge state not found"
    exit 1
}

$env:FRIGG_BRIDGE_HOST = $bridgeHost
$env:FRIGG_BRIDGE_PORT = [string]$port

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "python"
$psi.Arguments = "-m frigg_mcp.server.stdio"
$psi.WorkingDirectory = $repoRoot
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$null = $proc.Start()

function Send-Rpc {
    param(
        [System.Diagnostics.Process]$Process,
        [object]$Message
    )
    $line = $Message | ConvertTo-Json -Compress
    $Process.StandardInput.WriteLine($line)
    $Process.StandardInput.Flush()
    $resp = $Process.StandardOutput.ReadLine()
    if (-not $resp) {
        throw "No response from MCP server"
    }
    return $resp | ConvertFrom-Json
}

try {
    $init = Send-Rpc -Process $proc -Message @{jsonrpc="2.0"; id=1; method="initialize"; params=@{}}
    if (-not $init.result) {
        throw "initialize failed"
    }

    $tools = Send-Rpc -Process $proc -Message @{jsonrpc="2.0"; id=2; method="tools/list"; params=@{}}
    if (-not $tools.result) {
        throw "tools/list failed"
    }

    $ping = Send-Rpc -Process $proc -Message @{jsonrpc="2.0"; id=3; method="tools/call"; params=@{name="frigg.blender.bridge_ping"; arguments=@{}}}
    if (-not $ping.result) {
        throw "bridge_ping failed"
    }

    Write-Output "OK: initialize/tools/list/bridge_ping"
    exit 0
} catch {
    Write-Output ("KO: {0}" -f $_.Exception.Message)
    exit 1
} finally {
    if (-not $proc.HasExited) {
        $proc.Kill()
    }
    $proc.Dispose()
}

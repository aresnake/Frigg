param(
    [switch]$Headless,
    [switch]$UI
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$bridgeScript = Join-Path $repoRoot "tools\frigg_blender_bridge.py"

$bridgeHost = $env:FRIGG_BRIDGE_HOST
if (-not $bridgeHost) {
    $bridgeHost = "127.0.0.1"
}

function Test-PortFree {
    param(
        [string]$BridgeHost,
        [int]$Port
    )
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse($BridgeHost), $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

function Get-FreePort {
    param(
        [string]$BridgeHost
    )
    foreach ($port in 8765..8795) {
        if (Test-PortFree -BridgeHost $BridgeHost -Port $port) {
            return $port
        }
    }
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse($BridgeHost), 0)
    $listener.Start()
    $port = $listener.LocalEndpoint.Port
    $listener.Stop()
    return $port
}

$port = $env:FRIGG_BRIDGE_PORT
if ($port) {
    try {
        $port = [int]$port
    } catch {
        $port = $null
    }
}
if (-not $port -or -not (Test-PortFree -BridgeHost $bridgeHost -Port $port)) {
    $port = Get-FreePort -BridgeHost $bridgeHost
}

$env:FRIGG_BRIDGE_HOST = $bridgeHost
$env:FRIGG_BRIDGE_PORT = $port

$blenderExe = $env:BLENDER_EXE
if (-not $blenderExe) {
    $candidates = @(
        "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        "D:\Blender_5.0.0_Portable\blender.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $blenderExe = $candidate
            break
        }
    }
}

if (-not $blenderExe) {
    Write-Error "Blender executable not found. Set BLENDER_EXE or install Blender 5.0."
    exit 1
}

$argsList = @()
if ($Headless) {
    $argsList += "--background"
}
$argsList += "--python"
$argsList += $bridgeScript

Set-Location $repoRoot

$process = Start-Process -FilePath $blenderExe -ArgumentList $argsList -PassThru
$state = @{
    host = $bridgeHost
    port = $port
    pid = $process.Id
    started_at_iso = (Get-Date).ToString("o")
}
$statePath = Join-Path $repoRoot ".frigg_bridge.json"
$state | ConvertTo-Json -Compress | Set-Content -NoNewline -Encoding Ascii $statePath

Write-Output ("FRIGG_BRIDGE={0}:{1}" -f $bridgeHost, $port)
Wait-Process -Id $process.Id

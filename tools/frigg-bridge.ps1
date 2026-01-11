param(
    [switch]$Headless,
    [switch]$UI
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$bridgeScript = Join-Path $repoRoot "tools\frigg_blender_bridge.py"

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
& $blenderExe @argsList
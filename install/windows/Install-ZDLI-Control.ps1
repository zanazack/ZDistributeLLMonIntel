#Requires -Version 5.1
$ErrorActionPreference = "Stop"
Write-Host "ZDLI Control Center installer (Windows)" -ForegroundColor Cyan

if ($env:HTTP_PROXY) { Write-Host "Using HTTP_PROXY=$env:HTTP_PROXY" }

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw "Python 3.11+ required. Install from python.org or winget install Python.Python.3.12" }

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location $repo
python -m pip install --upgrade pip
python -m pip install -e .
Pop-Location

$envDir = Join-Path $repo "zdl.env"
if (-not (Test-Path $envDir)) {
  Copy-Item (Join-Path $repo "zdl.env.example") $envDir
  Write-Host "Created zdl.env — set ZDL_COORDINATOR_ENROLL_TOKEN and API tokens before WAN use." -ForegroundColor Yellow
}

$shortcut = @"
@echo off
cd /d `"$repo`"
set ZDL_COORDINATOR_HOST=0.0.0.0
zdl-control-center
"@
$startScript = Join-Path $repo "Start-ZDLI-ControlCenter.cmd"
Set-Content -Path $startScript -Value $shortcut -Encoding ASCII

Write-Host ""
Write-Host "Done. Run: $startScript" -ForegroundColor Green
Write-Host "Dashboard opens at http://127.0.0.1:7443/ui" -ForegroundColor Green
Write-Host "WAN: run .\scripts\start-wan-tunnels.ps1 then docs/TUNNEL-SETUP.md" -ForegroundColor Cyan

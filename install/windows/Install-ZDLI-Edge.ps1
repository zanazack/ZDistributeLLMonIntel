#Requires -Version 5.1
$ErrorActionPreference = "Stop"
Write-Host "ZDLI Edge Client installer (Windows)" -ForegroundColor Cyan

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw "Python 3.11+ required." }

$repo = if ($env:ZDLI_REPO) { $env:ZDLI_REPO } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
Push-Location $repo
python -m pip install -e .
Pop-Location

$startScript = Join-Path $repo "Start-ZDLI-Edge.cmd"
@"
@echo off
cd /d `"$repo`"
set ZDL_EDGE_HOST=127.0.0.1
zdl-edge
"@ | Set-Content -Path $startScript -Encoding ASCII

Write-Host "Done. Run: $startScript" -ForegroundColor Green
Write-Host "Open http://127.0.0.1:7340 and paste Coordinator URL + enroll token from Control Center." -ForegroundColor Green

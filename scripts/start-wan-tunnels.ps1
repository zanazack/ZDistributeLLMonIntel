#Requires -Version 5.1
$ErrorActionPreference = "Stop"

function Test-LocalPort {
  param([int]$Port)
  try {
    $c = New-Object System.Net.Sockets.TcpClient
    $c.Connect("127.0.0.1", $Port)
    $c.Close()
    return $true
  } catch {
    return $false
  }
}

$wrapper = Join-Path $PSScriptRoot "run-cloudflared-tunnel.cmd"
if (-not (Test-Path $wrapper)) {
  throw "Missing $wrapper"
}

Write-Host ""
Write-Host "ZDLI WAN tunnels" -ForegroundColor Cyan

if (-not (Test-LocalPort 7443)) {
  Write-Host "ERROR: Nothing listening on port 7443." -ForegroundColor Red
  Write-Host "Start Control Center FIRST in another window:" -ForegroundColor Yellow
  Write-Host "  .\Start-ZDLI-ControlCenter.cmd" -ForegroundColor Yellow
  Write-Host ""
  exit 1
}
Write-Host "OK: Control Center detected on port 7443" -ForegroundColor Green

if (-not (Test-LocalPort 8080)) {
  Write-Host "WARN: Port 8080 not open (gateway). Second tunnel may exit until gateway starts." -ForegroundColor Yellow
} else {
  Write-Host "OK: Gateway detected on port 8080" -ForegroundColor Green
}

Write-Host ""
Write-Host "Opening two CMD windows (stay open on error). Logs: %USERPROFILE%\.zdli\logs\" -ForegroundColor Cyan
Write-Host "1) Copy https URL from COORDINATOR window (7443) into Control Center UI" -ForegroundColor Yellow
Write-Host "2) Copy https URL from GATEWAY window (8080) if needed for remote Cursor" -ForegroundColor Yellow
Write-Host ""

Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "start", "ZDLI tunnel 7443", "cmd", "/k", $wrapper, "7443")
Start-Sleep -Seconds 2
Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "start", "ZDLI tunnel 8080", "cmd", "/k", $wrapper, "8080")

Write-Host "Tunnel windows launched. If they close immediately, open the log files under .zdli\logs" -ForegroundColor Green

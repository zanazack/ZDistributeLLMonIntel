#Requires -Version 5.1
<#
.SYNOPSIS
  Start two Cloudflare quick tunnels for ZDLI WAN lab (coordinator 7443 + gateway 8080).

.NOTES
  Keep this window open or leave the spawned cloudflared processes running.
  Copy each printed https://….trycloudflare.com URL into Control Center → WAN linking.
#>
$ErrorActionPreference = "Stop"

function Get-Cloudflared {
  $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $local = Join-Path $PSScriptRoot "cloudflared.exe"
  if (Test-Path $local) { return $local }
  throw "cloudflared not found. Run: winget install Cloudflare.cloudflared"
}

$cf = Get-Cloudflared
$repo = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "ZDLI WAN tunnels" -ForegroundColor Cyan
Write-Host "1) Ensure Control Center is running (Start-ZDLI-ControlCenter.cmd)" -ForegroundColor Yellow
Write-Host "2) Two cloudflared windows will open — copy BOTH https URLs" -ForegroundColor Yellow
Write-Host "3) Paste into http://127.0.0.1:7443/ui → Save public URLs" -ForegroundColor Yellow
Write-Host "4) Edge clients use the COORDINATOR tunnel URL (first window, port 7443)" -ForegroundColor Yellow
Write-Host ""

Start-Process -FilePath $cf -ArgumentList @("tunnel", "--url", "http://127.0.0.1:7443") -WindowStyle Normal
Start-Sleep -Seconds 2
Start-Process -FilePath $cf -ArgumentList @("tunnel", "--url", "http://127.0.0.1:8080") -WindowStyle Normal

Write-Host "Tunnel processes started. See docs/TUNNEL-SETUP.md" -ForegroundColor Green

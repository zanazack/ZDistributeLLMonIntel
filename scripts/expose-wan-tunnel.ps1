#Requires -Version 5.1
# Single tunnel: coordinator only (7443). For coordinator + gateway use start-wan-tunnels.ps1

$ErrorActionPreference = "Stop"
& "$PSScriptRoot\install-cloudflared.ps1" 2>$null
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Host "Install cloudflared first: .\scripts\install-cloudflared.ps1" -ForegroundColor Yellow
  exit 1
}
Write-Host "Coordinator tunnel to http://127.0.0.1:7443" -ForegroundColor Cyan
Write-Host "Copy https://....trycloudflare.com into Control Center (no :7443). See docs/TUNNEL-SETUP.md" -ForegroundColor Cyan
cloudflared tunnel --url http://127.0.0.1:7443

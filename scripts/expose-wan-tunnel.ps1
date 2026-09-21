#Requires -Version 5.1
# Quick WAN exposure for lab — Cloudflare quick tunnel to coordinator (7443).
# Install cloudflared first: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

$ErrorActionPreference = "Stop"
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Host "cloudflared not found. Use IT reverse proxy or see docs/WAN-CLUSTER-SETUP.md" -ForegroundColor Yellow
  exit 1
}
Write-Host "Tunneling http://127.0.0.1:7443 — paste URL into Control Center Public coordinator URL" -ForegroundColor Cyan
cloudflared tunnel --url http://127.0.0.1:7443

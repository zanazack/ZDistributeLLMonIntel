#Requires -Version 5.1
$ErrorActionPreference = "Stop"
if (Get-Command cloudflared -ErrorAction SilentlyContinue) {
  cloudflared --version
  exit 0
}
Write-Host "Installing cloudflared via winget..." -ForegroundColor Cyan
winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
Write-Host "Restart terminal, then: cloudflared --version" -ForegroundColor Green

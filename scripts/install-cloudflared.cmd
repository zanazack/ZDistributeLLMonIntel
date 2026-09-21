@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-cloudflared.ps1"
exit /b %ERRORLEVEL%

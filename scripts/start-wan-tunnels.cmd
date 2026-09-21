@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-wan-tunnels.ps1"
exit /b %ERRORLEVEL%

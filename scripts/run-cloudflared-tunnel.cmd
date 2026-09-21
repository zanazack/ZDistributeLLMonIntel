@echo off
REM Quick tunnel to local ZDLI service. Window stays open so you can read errors/URL.
REM Usage: run-cloudflared-tunnel.cmd 7443
setlocal
set PORT=%~1
if "%PORT%"=="" set PORT=7443

set LOGDIR=%USERPROFILE%\.zdli\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set LOGFILE=%LOGDIR%\tunnel-%PORT%.log

echo ZDLI cloudflared tunnel - local port %PORT%
echo Log: %LOGFILE%
echo.

REM Corporate proxy often breaks cloudflared; tunnel uses direct egress to Cloudflare.
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set NO_PROXY=localhost,127.0.0.1

where cloudflared >nul 2>&1
if errorlevel 1 (
  echo cloudflared not found on PATH.
  pause
  exit /b 1
)

echo Testing local service http://127.0.0.1:%PORT% ...
curl.exe -s -o NUL -w "HTTP %%{http_code}\n" --connect-timeout 3 http://127.0.0.1:%PORT%/health 2>nul
if errorlevel 1 (
  echo WARNING: Nothing answered on port %PORT%. Start Control Center first for 7443.
  echo.
)

echo Starting tunnel... copy the https://....trycloudflare.com line below.
echo.

cloudflared tunnel --url http://127.0.0.1:%PORT% --no-autoupdate 2>&1
echo.
echo cloudflared exited with errorlevel %ERRORLEVEL%
echo If this failed, check corporate firewall blocks outbound Cloudflare or start Control Center on port %PORT%.
pause

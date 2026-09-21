@echo off
cd /d "%~dp0"
set ZDL_COORDINATOR_HOST=0.0.0.0
echo Starting ZDLI Control Center...
echo Dashboard: http://127.0.0.1:7443/ui
python -m zdli.control_center.main
if errorlevel 1 (
  echo.
  echo If python not found: pip install -e .
  pause
)

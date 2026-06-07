@echo off
REM Double-click to see current signals + equity, then stay open.
cd /d "%~dp0"
python status.py
echo.
echo (dashboard.html in this folder = web view; serve.bat = view in browser)
pause

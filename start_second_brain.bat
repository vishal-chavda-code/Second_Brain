@echo off
REM Second Brain Auto-Starter
echo Starting Second Brain...
cd /d "%~dp0"
.\venv\Scripts\python.exe slack_listener.py
pause

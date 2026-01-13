# Second Brain - Startup and Management Scripts

## Quick Start
Double-click: `start_second_brain.bat` - Starts with visible window

## Run in Background
Right-click `start_second_brain_hidden.ps1` → "Run with PowerShell" - Runs hidden

## Auto-Start on Windows Login
Right-click `setup_autostart.ps1` → "Run with PowerShell"
- Second Brain will start automatically when you log into Windows
- Runs hidden in the background

## Stop Second Brain
Right-click `stop_second_brain.ps1` → "Run with PowerShell"

## Remove Auto-Start
Right-click `remove_autostart.ps1` → "Run with PowerShell"

## Manual Commands
```powershell
# Start manually
.\venv\Scripts\python.exe slack_listener.py

# Check if running
Get-Process python | Where-Object {$_.Path -like "*notion_setup*"}

# Stop
Get-Process python | Where-Object {$_.Path -like "*notion_setup*"} | Stop-Process -Force
```

## Troubleshooting
If PowerShell scripts won't run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

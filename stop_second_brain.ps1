# Stop Second Brain
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*notion_setup*"} | Stop-Process -Force
Write-Host "🛑 Second Brain stopped"

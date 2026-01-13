# Remove Second Brain from Windows startup
Unregister-ScheduledTask -TaskName "SecondBrainAutoStart" -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "✅ Second Brain auto-start removed"

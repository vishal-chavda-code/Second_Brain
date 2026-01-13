# Setup Second Brain to run on Windows startup
$scriptPath = "C:\Users\vmc30\OneDrive\Desktop\Personal_Repos\notion_setup\start_second_brain_hidden.ps1"

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName "SecondBrainAutoStart" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automatically starts Second Brain on login" -Force

Write-Host "✅ Second Brain will now auto-start on Windows login!"
Write-Host ""
Write-Host "To manage:"
Write-Host "  - View: Task Scheduler → 'SecondBrainAutoStart'"
Write-Host "  - Disable: Disable-ScheduledTask -TaskName 'SecondBrainAutoStart'"
Write-Host "  - Remove: Unregister-ScheduledTask -TaskName 'SecondBrainAutoStart' -Confirm:`$false"

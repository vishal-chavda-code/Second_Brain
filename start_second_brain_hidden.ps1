# Second Brain Auto-Starter (Hidden)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Run Python script hidden
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = ".\venv\Scripts\python.exe"
$psi.Arguments = "slack_listener.py"
$psi.WorkingDirectory = $scriptPath
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.CreateNoWindow = $true

$process = [System.Diagnostics.Process]::Start($psi)

Write-Host "🧠 Second Brain started in background (PID: $($process.Id))"
Write-Host "To stop: taskkill /PID $($process.Id) /F"

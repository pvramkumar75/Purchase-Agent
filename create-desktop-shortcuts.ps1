$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Create START shortcut
$StartLink = $WshShell.CreateShortcut("$DesktopPath\OmniMind - Start.lnk")
$StartLink.TargetPath = "$ProjectDir\start-app.bat"
$StartLink.WorkingDirectory = $ProjectDir
$StartLink.IconLocation = "shell32.dll,21"
$StartLink.Description = "Start OmniMind AI Assistant"
$StartLink.Save()

# Create STOP shortcut
$StopLink = $WshShell.CreateShortcut("$DesktopPath\OmniMind - Stop.lnk")
$StopLink.TargetPath = "$ProjectDir\stop-app.bat"
$StopLink.WorkingDirectory = $ProjectDir
$StopLink.IconLocation = "shell32.dll,27"
$StopLink.Description = "Stop OmniMind AI Assistant"
$StopLink.Save()

Write-Host ""
Write-Host "  =================================" -ForegroundColor Magenta
Write-Host "   OmniMind shortcuts created!" -ForegroundColor Green
Write-Host "  =================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  You now have two icons on your Desktop:" -ForegroundColor White
Write-Host "    - OmniMind - Start" -ForegroundColor Yellow
Write-Host "    - OmniMind - Stop" -ForegroundColor Yellow
Write-Host ""

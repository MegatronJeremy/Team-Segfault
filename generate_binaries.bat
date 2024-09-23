@echo off

REM Run the PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File generate_binaries.ps1

REM Check if the PowerShell script ran successfully
if %errorlevel% neq 0 (
    echo PowerShell script generate_binaries.ps1 failed.
    
    pause
    exit /b 1
)

echo PowerShell script generate_binaries.ps1 ran successfully.

REM Keep the window open
pause
@echo off
REM Check if PowerShell script exists
if not exist generate_binaries.ps1 (
    echo generate_binaries.ps1 does not exist.
    exit /b 1
)

REM Run the PowerShell script
powershell.exe -NoProfile -ExecutionPolicy Bypass -File generate_binaries.ps1

REM Check if the PowerShell script ran successfully
if %errorlevel% neq 0 (
    echo PowerShell script generate_binaries.ps1 failed.
    exit /b 1
)

echo PowerShell script generate_binaries.ps1 ran successfully.

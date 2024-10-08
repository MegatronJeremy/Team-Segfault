# Check if PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "Error: PyInstaller is not installed. Please install it first."
    exit 1
}

# Display menu options
Write-Host "Select an option:"
Write-Host "1. Run command for One Directory"
Write-Host "2. Run command for One File"

# Read user input
$userChoice = Read-Host "Enter your choice (1 or 2)"

# Process user choice
switch ($userChoice)
{
    1 {
        pyinstaller --noconfirm --onedir --noconsole --icon "icon.ico" --name "team_segfault" --optimize "2" --add-data "assets;assets/" --add-data "mab/data/server_data;mab/data/server_data/" --add-data "mab/data/training_data;mab/data/training_data/" --add-data "replays;replays/" main.py
    }
    2 {
        pyinstaller --noconfirm --onefile --noconsole --icon "icon.ico" --name "team_segfault" --optimize "2" --add-data "assets;assets/" --add-data "mab/data/server_data;mab/data/server_data/" --add-data "mab/data/training_data;mab/data/training_data/" --add-data "replays;replays/" main.py
    }
    default {
        Write-Host "Invalid choice. Please enter 1 or 2."
    }
}
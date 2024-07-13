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
        pyinstaller --noconfirm --onedir --console --icon "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\icon.ico" --name "team_segfault" --optimize "2" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\assets;assets/" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\mab\data\server_data;mab/data/server_data/" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\mab\data\training_data;mab/data/training_data/"  "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\main.py"
    }
    2 {
        pyinstaller --noconfirm --onefile --console --icon "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\icon.ico" --name "team_segfault" --optimize "2" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\assets;assets/" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\mab\data\server_data;mab/data/server_data/" --add-data "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\mab\data\training_data;mab/data/training_data/"  "C:\Users\xparh\OneDrive\Desktop\Team-Segfault\main.py"
    }
    default {
        Write-Host "Invalid choice. Please enter 1 or 2."
    }
}

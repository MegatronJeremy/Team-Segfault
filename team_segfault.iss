[Setup]
AppName=Team Segfault
AppVersion=1.0
DefaultDirName={pf}\Team Segfault
DefaultGroupName=Team Segfault
OutputDir=.
OutputBaseFilename=team_segfault_setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\team_segfault.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Team Segfault"; Filename: "{app}\team_segfault.exe"
Name: "{group}\Uninstall Team Segfault"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Team Segfault"; Filename: "{app}\team_segfault.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\team_segfault.exe"; Description: "{cm:LaunchProgram,Team Segfault}"; Flags: nowait postinstall skipifsilent

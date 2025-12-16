; Скрипт Inno Setup для создания установщика ChatList
; Для компиляции установщика используйте Inno Setup Compiler

#define MyAppName "ChatList"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ChatList"
#define MyAppURL "https://github.com/your-repo/chatlist"
#define MyAppExeName "ChatList.exe"
#define MyAppIcon "app.ico"

[Setup]
; Основные настройки
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=ChatList-Setup-{#MyAppVersion}
SetupIconFile={#MyAppIcon}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

; Языки
[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; Задачи установки
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

; Файлы для установки
[Files]
; Основной исполняемый файл
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Иконка приложения
Source: "{#MyAppIcon}"; DestDir: "{app}"; Flags: ignoreversion
; README (опционально)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
; LICENSE
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Иконки
[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppIcon}"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\{#MyAppIcon}"

; Запуск после установки
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Коды возврата
[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;



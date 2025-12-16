; Скрипт Inno Setup для создания установщика ChatList
; Для компиляции установщика используйте Inno Setup Compiler
; ВАЖНО: Версия автоматически заменяется из version.py при запуске build-installer.ps1
; Не редактируйте версию вручную!

#define MyAppName "ChatList"
#define MyAppVersion "1.0.0"  ; Эта версия будет автоматически заменена из version.py
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

; Удаление при деинсталляции
[UninstallDelete]
; Удаляем файлы базы данных и логов, если они находятся в папке приложения
Type: files; Name: "{app}\chatlist.db"
Type: files; Name: "{app}\chatlist.db-journal"
Type: files; Name: "{app}\chatlist.log"
; Удаляем временные файлы, если они есть
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.pyc"
; Удаляем папку приложения, если она пустая (после удаления всех файлов)
Type: dirifempty; Name: "{app}"

; Настройки деинсталлятора
[UninstallRun]
; Действия выполняются в функции InitializeUninstall в секции [Code]

; Коды возврата и дополнительные функции
[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
  ResultCode: Integer;
begin
  Result := True;
  
  // Проверяем, запущено ли приложение через tasklist
  if Exec('cmd.exe', '/C tasklist /FI "IMAGENAME eq ChatList.exe" 2>NUL | find /I /N "ChatList.exe">NUL', 
          '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // Если процесс найден (ResultCode = 0), предлагаем закрыть
    if ResultCode = 0 then
    begin
      if MsgBox('Приложение ChatList запущено. Закрыть его перед удалением?', 
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        // Закрываем приложение принудительно
        Exec('taskkill', '/F /IM ChatList.exe', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
        // Даем время на закрытие процесса
        Sleep(1500);
      end
      else
      begin
        Result := False;
        MsgBox('Удаление отменено. Закройте приложение ChatList и попробуйте снова.', mbError, MB_OK);
        Exit;
      end;
    end;
  end;
end;



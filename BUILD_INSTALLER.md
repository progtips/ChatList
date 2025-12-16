# Создание установщика с помощью Inno Setup

Это руководство поможет вам создать установщик Windows для ChatList с помощью Inno Setup.

## Подготовка проекта

### 1. Установка Inno Setup

1. Скачайте Inno Setup с официального сайта: https://jrsoftware.org/isdl.php
2. Установите Inno Setup (рекомендуется версия 6.x или новее)
3. При установке выберите опцию "Install Inno Setup Preprocessor" (ISPP)

### 2. Сборка исполняемого файла

Перед созданием установщика убедитесь, что исполняемый файл собран:

```powershell
# Установите зависимости (если еще не установлены)
pip install -r requirements.txt

# Соберите исполняемый файл
.\build.ps1
```

Или вручную:

```powershell
pyinstaller --onefile --windowed --name "ChatList" --icon="app.ico" main.py
```

Проверьте, что файл `dist\ChatList.exe` существует.

### 3. Проверка необходимых файлов

Убедитесь, что в корне проекта есть следующие файлы:
- ✅ `dist\ChatList.exe` - исполняемый файл
- ✅ `app.ico` - иконка приложения
- ✅ `LICENSE` - файл лицензии
- ✅ `README.md` - документация (опционально)
- ✅ `setup.iss` - скрипт Inno Setup

## Создание установщика

### Способ 1: Через графический интерфейс Inno Setup

1. Откройте **Inno Setup Compiler**
2. Выберите **File → Open** и откройте файл `setup.iss`
3. Нажмите **Build → Compile** (или F9)
4. Установщик будет создан в папке `installer\ChatList-Setup-1.0.0.exe`

### Способ 2: Через командную строку

```powershell
# Путь к компилятору Inno Setup (обычно)
$innoCompiler = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# Компиляция установщика
& $innoCompiler "setup.iss"
```

Или если Inno Setup установлен в стандартное место:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "setup.iss"
```

### Способ 3: Автоматический скрипт

Создайте файл `build-installer.ps1`:

```powershell
# Скрипт для автоматической сборки установщика

Write-Host "Проверка необходимых файлов..." -ForegroundColor Green

# Проверяем наличие исполняемого файла
if (-not (Test-Path "dist\ChatList.exe")) {
    Write-Host "Ошибка: dist\ChatList.exe не найден!" -ForegroundColor Red
    Write-Host "Сначала выполните сборку: .\build.ps1" -ForegroundColor Yellow
    exit 1
}

# Проверяем наличие иконки
if (-not (Test-Path "app.ico")) {
    Write-Host "Предупреждение: app.ico не найден. Установщик будет создан без иконки." -ForegroundColor Yellow
}

# Проверяем наличие скрипта Inno Setup
if (-not (Test-Path "setup.iss")) {
    Write-Host "Ошибка: setup.iss не найден!" -ForegroundColor Red
    exit 1
}

# Путь к компилятору Inno Setup
$innoPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$innoCompiler = $null
foreach ($path in $innoPaths) {
    if (Test-Path $path) {
        $innoCompiler = $path
        break
    }
}

if (-not $innoCompiler) {
    Write-Host "Ошибка: Inno Setup Compiler не найден!" -ForegroundColor Red
    Write-Host "Установите Inno Setup с https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    exit 1
}

Write-Host "Найден компилятор: $innoCompiler" -ForegroundColor Green
Write-Host "Создание установщика..." -ForegroundColor Green

# Создаем папку для установщика, если её нет
if (-not (Test-Path "installer")) {
    New-Item -ItemType Directory -Path "installer" | Out-Null
}

# Компилируем установщик
& $innoCompiler "setup.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Установщик успешно создан!" -ForegroundColor Green
    Write-Host "Файл: installer\ChatList-Setup-1.0.0.exe" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Ошибка при создании установщика!" -ForegroundColor Red
    exit 1
}
```

Затем запустите:

```powershell
.\build-installer.ps1
```

## Настройка установщика

### Изменение версии

Откройте `setup.iss` и измените строку:

```iss
#define MyAppVersion "1.0.0"
```

### Изменение имени приложения

```iss
#define MyAppName "ChatList"
```

### Изменение пути установки по умолчанию

```iss
DefaultDirName={autopf}\{#MyAppName}
```

Доступные варианты:
- `{autopf}` - Program Files (требует прав администратора)
- `{localappdata}` - AppData\Local (не требует прав администратора)
- `{userpf}` - User Profile\Program Files

### Добавление дополнительных файлов

В секции `[Files]` добавьте:

```iss
Source: "путь\к\файлу"; DestDir: "{app}"; Flags: ignoreversion
```

### Изменение языка установщика

В секции `[Languages]` можно добавить другие языки:

```iss
[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
```

## Структура установщика

После компиляции в папке `installer` будет создан файл:
- `ChatList-Setup-1.0.0.exe` - установщик программы

## Тестирование установщика

1. Запустите созданный установщик
2. Проверьте установку в выбранной директории
3. Проверьте создание ярлыков в меню "Пуск" и на рабочем столе
4. Проверьте запуск программы
5. Проверьте удаление через "Программы и компоненты"

## Дополнительные возможности

### Подпись установщика

Для подписи установщика цифровой подписью добавьте в секцию `[Setup]`:

```iss
SignTool=signtool
SignedUninstaller=yes
```

И настройте SignTool в Inno Setup Compiler (Tools → Configure Sign Tools).

### Автоматическое обновление

Для поддержки автоматических обновлений можно использовать секцию `[Code]` для проверки версии и скачивания обновлений.

### Создание портативной версии

Для создания портативной версии (без установки) можно использовать параметр:

```iss
DisableProgramGroupPage=yes
DisableDirPage=yes
```

## Устранение проблем

### Ошибка "Cannot find ISPP"

Установите Inno Setup Preprocessor при установке Inno Setup.

### Ошибка "File not found"

Проверьте, что все файлы, указанные в секции `[Files]`, существуют.

### Установщик не запускается

Проверьте, что исполняемый файл собран правильно и не требует дополнительных DLL.

## Полезные ссылки

- [Документация Inno Setup](https://jrsoftware.org/ishelp/)
- [Примеры скриптов](https://jrsoftware.org/is3/index.php)
- [Форум Inno Setup](https://groups.google.com/g/innosetup)



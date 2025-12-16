# Скрипт для автоматической сборки установщика ChatList

Write-Host "=== Создание установщика ChatList ===" -ForegroundColor Cyan
Write-Host ""

# Функция для чтения версии из version.py
function Get-VersionFromPython {
    if (-not (Test-Path "version.py")) {
        Write-Host "❌ Ошибка: version.py не найден!" -ForegroundColor Red
        exit 1
    }
    
    $versionContent = Get-Content "version.py" -Raw
    if ($versionContent -match '__version__\s*=\s*["'']([^"'']+)["'']') {
        return $matches[1]
    } else {
        Write-Host "❌ Ошибка: не удалось найти __version__ в version.py!" -ForegroundColor Red
        exit 1
    }
}

# Получаем версию из version.py
$appVersion = Get-VersionFromPython
Write-Host "Версия приложения: $appVersion" -ForegroundColor Cyan
Write-Host ""

# Проверка необходимых файлов
Write-Host "Проверка необходимых файлов..." -ForegroundColor Green

# Проверяем наличие исполняемого файла
if (-not (Test-Path "dist\ChatList.exe")) {
    Write-Host "❌ Ошибка: dist\ChatList.exe не найден!" -ForegroundColor Red
    Write-Host "   Сначала выполните сборку: .\build.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Исполняемый файл найден: dist\ChatList.exe" -ForegroundColor Green

# Проверяем наличие иконки
if (-not (Test-Path "app.ico")) {
    Write-Host "⚠️  Предупреждение: app.ico не найден. Установщик будет создан без иконки." -ForegroundColor Yellow
} else {
    Write-Host "✅ Иконка найдена: app.ico" -ForegroundColor Green
}

# Проверяем наличие скрипта Inno Setup
if (-not (Test-Path "setup.iss")) {
    Write-Host "❌ Ошибка: setup.iss не найден!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Скрипт Inno Setup найден: setup.iss" -ForegroundColor Green

# Проверяем наличие LICENSE
if (-not (Test-Path "LICENSE")) {
    Write-Host "⚠️  Предупреждение: LICENSE не найден." -ForegroundColor Yellow
}

Write-Host ""

# Поиск компилятора Inno Setup
Write-Host "Поиск компилятора Inno Setup..." -ForegroundColor Green

$innoPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$innoCompiler = $null
foreach ($path in $innoPaths) {
    if (Test-Path $path) {
        $innoCompiler = $path
        Write-Host "✅ Найден компилятор: $path" -ForegroundColor Green
        break
    }
}

if (-not $innoCompiler) {
    Write-Host "❌ Ошибка: Inno Setup Compiler не найден!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установите Inno Setup:" -ForegroundColor Yellow
    Write-Host "  1. Скачайте с https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "  2. Установите Inno Setup" -ForegroundColor Yellow
    Write-Host "  3. При установке выберите опцию 'Install Inno Setup Preprocessor'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

# Создаем папку для установщика, если её нет
if (-not (Test-Path "installer")) {
    New-Item -ItemType Directory -Path "installer" | Out-Null
    Write-Host "✅ Создана папка: installer" -ForegroundColor Green
}

Write-Host "Создание установщика..." -ForegroundColor Cyan
Write-Host ""

# Создаем временный setup.iss с подставленной версией
$setupContent = Get-Content "setup.iss" -Raw
$setupContent = $setupContent -replace '#define MyAppVersion ".*"', "#define MyAppVersion `"$appVersion`""

$tempSetupFile = "setup.temp.iss"
$setupContent | Out-File -FilePath $tempSetupFile -Encoding UTF8 -NoNewline

Write-Host "Используется версия: $appVersion" -ForegroundColor Green
Write-Host ""

# Компилируем установщик с временным файлом
& $innoCompiler $tempSetupFile

# Удаляем временный файл
if (Test-Path $tempSetupFile) {
    Remove-Item $tempSetupFile -Force
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Установщик успешно создан!" -ForegroundColor Green
    Write-Host ""
    
    $installerFile = "installer\ChatList-Setup-$appVersion.exe"
    if (Test-Path $installerFile) {
        $fileSize = (Get-Item $installerFile).Length / 1MB
        Write-Host "Файл: $installerFile" -ForegroundColor Yellow
        Write-Host "Размер: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Для установки запустите: .\$installerFile" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "❌ Ошибка при создании установщика!" -ForegroundColor Red
    Write-Host "Код возврата: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}



# Скрипт для создания исполняемого файла
# Убедитесь, что установлены зависимости: pip install -r requirements.txt

Write-Host "Создание исполняемого файла..." -ForegroundColor Green

# Функция для чтения версии из version.py
function Get-VersionFromPython {
    if (-not (Test-Path "version.py")) {
        Write-Host "⚠️  Предупреждение: version.py не найден, используется версия по умолчанию" -ForegroundColor Yellow
        return "1.0.0"
    }
    
    $versionContent = Get-Content "version.py" -Raw
    if ($versionContent -match '__version__\s*=\s*["'']([^"'']+)["'']') {
        return $matches[1]
    } else {
        Write-Host "⚠️  Предупреждение: не удалось найти __version__ в version.py, используется версия по умолчанию" -ForegroundColor Yellow
        return "1.0.0"
    }
}

# Получаем версию из version.py
$appVersion = Get-VersionFromPython
Write-Host "Версия приложения: $appVersion" -ForegroundColor Cyan
Write-Host ""

# Проверяем наличие иконки
$iconPath = ""
if (Test-Path "app.ico") {
    $iconPath = "app.ico"
    Write-Host "Найдена иконка: app.ico" -ForegroundColor Green
} elseif (Test-Path "icon.ico") {
    $iconPath = "icon.ico"
    Write-Host "Найдена иконка: icon.ico" -ForegroundColor Green
} else {
    Write-Host "Иконка не найдена. Исполняемый файл будет создан без иконки." -ForegroundColor Yellow
    Write-Host "Для добавления иконки создайте файл app.ico или icon.ico в корне проекта." -ForegroundColor Yellow
}

# Создаем один исполняемый файл с иконкой (если есть)
if ($iconPath) {
    pyinstaller --onefile --windowed --name "ChatList" --icon="$iconPath" main.py
} else {
    pyinstaller --onefile --windowed --name "ChatList" main.py
}

Write-Host "`nИсполняемый файл создан в папке dist\ChatList.exe" -ForegroundColor Green
Write-Host "Для запуска: .\dist\ChatList.exe" -ForegroundColor Yellow




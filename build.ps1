# Скрипт для создания исполняемого файла
# Убедитесь, что установлены зависимости: pip install -r requirements.txt

Write-Host "Создание исполняемого файла..." -ForegroundColor Green

# Создаем один исполняемый файл с иконкой (если есть)
pyinstaller --onefile --windowed --name "PyQtApp" main.py

Write-Host "`nИсполняемый файл создан в папке dist\PyQtApp.exe" -ForegroundColor Green
Write-Host "Для запуска: .\dist\PyQtApp.exe" -ForegroundColor Yellow


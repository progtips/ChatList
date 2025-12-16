# Краткое руководство по публикации ChatList

Это краткое руководство поможет вам быстро опубликовать ChatList на GitHub Release и GitHub Pages.

## Быстрый старт

### 1. Подготовка к релизу

```powershell
# Обновите версию в version.py
# Затем соберите установщик
.\build.ps1
.\build-installer.ps1
```

### 2. Настройка GitHub Pages

1. Откройте `docs/index.html`
2. Замените `ваш-username` на ваш GitHub username во всех ссылках
3. Закоммитьте изменения:
   ```powershell
   git add docs/
   git commit -m "Add landing page"
   git push origin main
   ```
4. В настройках репозитория GitHub:
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main, folder: /docs
   - Save

### 3. Создание релиза

1. Перейдите на https://github.com/ваш-username/ChatList/releases
2. Нажмите "Draft a new release"
3. Создайте тег: `v1.0.0`
4. Заполните описание (используйте `.github/release-template.md`)
5. Загрузите файл `installer\ChatList-Setup-1.0.0.exe`
6. Нажмите "Publish release"

## Подробные инструкции

- **GitHub Release:** См. [GITHUB_RELEASE.md](GITHUB_RELEASE.md)
- **GitHub Pages:** См. [GITHUB_PAGES.md](GITHUB_PAGES.md)

## Что нужно настроить перед публикацией

### В файле `docs/index.html`:

Замените все вхождения `ваш-username` на ваш реальный GitHub username:

```html
<!-- Было: -->
<a href="https://github.com/ваш-username/ChatList">

<!-- Должно быть: -->
<a href="https://github.com/ваш-реальный-username/ChatList">
```

Также обновите ссылки на скачивание:

```html
<!-- Было: -->
<a href="https://github.com/ваш-username/ChatList/releases/latest/download/ChatList-Setup-1.0.0.exe">

<!-- Должно быть: -->
<a href="https://github.com/ваш-реальный-username/ChatList/releases/latest/download/ChatList-Setup-1.0.0.exe">
```

### В файле `.github/release-template.md`:

Замените `{версия}` на актуальную версию при создании релиза.

## Автоматизация (опционально)

Если хотите автоматизировать процесс:

1. GitHub Actions workflows уже настроены в `.github/workflows/`
2. При создании релиза через GitHub автоматически запустится сборка
3. При изменении файлов в `docs/` автоматически обновится GitHub Pages

## Проверка после публикации

- ✅ GitHub Pages доступен по адресу: `https://ваш-username.github.io/ChatList/`
- ✅ Релиз опубликован: `https://github.com/ваш-username/ChatList/releases`
- ✅ Установщик доступен для скачивания
- ✅ Все ссылки на лендинге работают корректно

## Следующие шаги

1. Добавьте скриншоты в `docs/index.html` (замените placeholder'ы)
2. Настройте кастомный домен (если есть)
3. Добавьте больше информации о проекте на лендинге
4. Создайте CHANGELOG.md для отслеживания изменений


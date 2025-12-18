# Исправление ошибки деплоя GitHub Pages

Если вы видите ошибку "Failed to deploy to github-pages", выполните следующие шаги:

## Шаг 1: Настройте GitHub Pages в настройках репозитория

**ВАЖНО:** Это нужно сделать ПЕРВЫМ делом!

1. Перейдите в настройки репозитория:
   - `https://github.com/progtips/ChatList/settings/pages`

2. В разделе "Source" выберите:
   - **Source:** "GitHub Actions" (не "Deploy from a branch"!)
   - Это включит использование GitHub Actions для деплоя

3. Нажмите "Save"

## Шаг 2: Проверьте права доступа

1. Перейдите в настройки репозитория:
   - `https://github.com/progtips/ChatList/settings/actions`

2. Убедитесь, что:
   - "Allow all actions and reusable workflows" включено
   - Или "Allow local actions and reusable workflows" включено

3. В разделе "Workflow permissions":
   - Выберите "Read and write permissions"
   - Включите "Allow GitHub Actions to create and approve pull requests"

## Шаг 3: Проверьте наличие файла index.html

Убедитесь, что файл `docs/index.html` существует и закоммичен:

```powershell
# Проверьте наличие файла
Test-Path "docs\index.html"

# Если файла нет, создайте его или скопируйте из шаблона
```

## Шаг 4: Перезапустите workflow

1. Перейдите на страницу Actions:
   - `https://github.com/progtips/ChatList/actions`

2. Найдите failed workflow "Deploy GitHub Pages"

3. Нажмите на него и выберите "Re-run jobs" → "Re-run failed jobs"

Или создайте новый коммит для триггера:

```powershell
# Сделайте небольшое изменение в docs/index.html (например, добавьте пробел)
# Или создайте пустой коммит
git commit --allow-empty -m "Trigger GitHub Pages deployment"
git push origin main
```

## Шаг 5: Альтернативное решение - используйте простой деплой

Если проблемы продолжаются, можно использовать более простой workflow без разделения на build и deploy:

Создайте файл `.github/workflows/pages-simple.yml`:

```yaml
name: Deploy GitHub Pages (Simple)

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './docs'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Проверка после исправления

После выполнения всех шагов:

1. ✅ Проверьте статус workflow в Actions
2. ✅ Дождитесь завершения деплоя (обычно 1-2 минуты)
3. ✅ Откройте сайт: `https://progtips.github.io/ChatList/`

## Частые ошибки и решения

### Ошибка: "No such file or directory: './docs'"

**Решение:** Убедитесь, что папка `docs` существует и содержит файл `index.html`

### Ошибка: "Permission denied"

**Решение:** Проверьте права доступа в настройках репозитория (шаг 2)

### Ошибка: "Environment 'github-pages' not found"

**Решение:** 
1. Убедитесь, что в настройках Pages выбран "GitHub Actions" как источник
2. Создайте коммит после изменения настроек

### Workflow не запускается

**Решение:**
1. Проверьте, что файл `.github/workflows/pages.yml` закоммичен
2. Убедитесь, что путь `docs/**` указан правильно
3. Попробуйте запустить workflow вручную через "workflow_dispatch"

## Если ничего не помогает

Используйте простой способ без GitHub Actions:

1. В настройках Pages выберите "Deploy from a branch"
2. Выберите ветку `main` и папку `/docs`
3. Сохраните настройки

GitHub автоматически будет публиковать сайт при каждом коммите в папку `docs`.




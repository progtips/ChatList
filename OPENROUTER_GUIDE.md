# Руководство по подключению моделей OpenRouter

## Подготовка

1. **Добавьте API-ключ в файл `.env`:**
   ```
   OPENROUTER_API_KEY=ваш_ключ_от_openrouter
   ```

2. **Список доступных моделей:** https://openrouter.ai/models

## Как добавить модель из OpenRouter

### Через интерфейс программы:

1. Запустите программу
2. Перейдите в меню **"Модели"** → **"Добавить модель"**
3. Заполните форму:
   - **Название:** Любое удобное имя (например, "GPT-4 через OpenRouter")
   - **API URL:** `https://openrouter.ai/api/v1/chat/completions`
   - **API ID (model):** Полное имя модели из OpenRouter (см. примеры ниже)
   - **Имя переменной окружения с API-ключом:** `OPENROUTER_API_KEY`
   - **Тип модели:** `openrouter`
   - **Активна:** Отметьте галочку

4. Нажмите **"OK"**

### Примеры популярных моделей:

#### OpenAI модели:
- **GPT-4 Turbo:** `openai/gpt-4-turbo`
- **GPT-4:** `openai/gpt-4`
- **GPT-3.5 Turbo:** `openai/gpt-3.5-turbo`

#### Anthropic (Claude):
- **Claude 3.5 Sonnet:** `anthropic/claude-3.5-sonnet`
- **Claude 3 Opus:** `anthropic/claude-3-opus`
- **Claude 3 Haiku:** `anthropic/claude-3-haiku`

#### Google:
- **Gemini Pro:** `google/gemini-pro`
- **Gemini Pro Vision:** `google/gemini-pro-vision`

#### Meta:
- **Llama 2 70B:** `meta-llama/llama-2-70b-chat`
- **Llama 2 13B:** `meta-llama/llama-2-13b-chat`

#### Mistral AI:
- **Mistral 7B Instruct:** `mistralai/mistral-7b-instruct`
- **Mixtral 8x7B:** `mistralai/mixtral-8x7b-instruct`

#### Другие популярные:
- **Perplexity Llama 3 70B:** `perplexity/llama-3-sonar-large-32k-online`
- **Cohere Command:** `cohere/command`
- **Nous Hermes 2:** `nousresearch/nous-hermes-2-mixtral-8x7b-dpo`

## Пример добавления GPT-4 через OpenRouter:

**Название:** GPT-4 (OpenRouter)  
**API URL:** `https://openrouter.ai/api/v1/chat/completions`  
**API ID:** `openai/gpt-4`  
**Переменная окружения:** `OPENROUTER_API_KEY`  
**Тип модели:** `openrouter`  
**Активна:** ✓

## Важные замечания:

1. **Один API-ключ для всех моделей:** OpenRouter использует один API-ключ для доступа ко всем моделям
2. **Стоимость:** Разные модели имеют разную стоимость запросов. Проверьте цены на https://openrouter.ai/models
3. **Имена моделей:** Используйте точное имя модели из списка OpenRouter (формат: `provider/model-name`)
4. **Лимиты:** OpenRouter может иметь лимиты на количество запросов в зависимости от вашего тарифа

## Проверка работы:

После добавления модели:
1. Введите тестовый промт
2. Нажмите "Отправить"
3. Проверьте, что модель отвечает корректно

Если возникают ошибки:
- Проверьте правильность API-ключа в `.env`
- Убедитесь, что имя модели указано точно (с учетом регистра и провайдера)
- Проверьте, что модель активна в интерфейсе программы


# Схема базы данных ChatList

База данных SQLite с именем `chatlist.db` (по умолчанию) содержит следующие таблицы:

## Таблица: prompts (Промты)

Хранит сохраненные промты пользователя.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| date | TEXT | Дата создания промта | NOT NULL, формат ISO (YYYY-MM-DD HH:MM:SS) |
| prompt | TEXT | Текст промта | NOT NULL |
| tags | TEXT | Теги для категоризации (через запятую) | NULL |

**Индексы:**
- `idx_prompts_date` на поле `date` (для сортировки по дате)
- `idx_prompts_tags` на поле `tags` (для поиска по тегам)

**Пример данных:**
```sql
INSERT INTO prompts (date, prompt, tags) 
VALUES ('2024-01-15 10:30:00', 'Объясни квантовую физику', 'наука, физика');
```

---

## Таблица: models (Модели нейросетей)

Хранит информацию о доступных моделях нейросетей.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | Название модели | NOT NULL, UNIQUE |
| api_url | TEXT | URL API для отправки запросов | NOT NULL |
| api_id | TEXT | Идентификатор модели в API | NOT NULL |
| api_key_env_var | TEXT | Имя переменной окружения с API-ключом | NOT NULL |
| model_type | TEXT | Тип модели (openai, deepseek, groq и т.д.) | NOT NULL |
| is_active | INTEGER | Активна ли модель (1 - да, 0 - нет) | NOT NULL, DEFAULT 1 |
| created_at | TEXT | Дата добавления модели | NOT NULL, формат ISO |
| updated_at | TEXT | Дата последнего обновления | NULL |

**Индексы:**
- `idx_models_active` на поле `is_active` (для быстрого поиска активных моделей)
- `idx_models_type` на поле `model_type` (для фильтрации по типу)

**Пример данных:**
```sql
INSERT INTO models (name, api_url, api_id, api_key_env_var, model_type, is_active, created_at) 
VALUES (
    'GPT-4', 
    'https://api.openai.com/v1/chat/completions', 
    'gpt-4', 
    'OPENAI_API_KEY', 
    'openai', 
    1, 
    '2024-01-15 10:00:00'
);
```

**Примечание:** API-ключи хранятся в файле `.env` в виде переменных окружения. В таблице хранится только имя переменной (`api_key_env_var`), например `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` и т.д.

---

## Таблица: results (Результаты)

Хранит сохраненные результаты ответов моделей.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| prompt_id | INTEGER | Ссылка на промт | FOREIGN KEY REFERENCES prompts(id) |
| model_id | INTEGER | Ссылка на модель | FOREIGN KEY REFERENCES models(id) |
| prompt_text | TEXT | Текст промта (копия на момент запроса) | NOT NULL |
| model_name | TEXT | Название модели (копия на момент запроса) | NOT NULL |
| response_text | TEXT | Текст ответа модели | NOT NULL |
| created_at | TEXT | Дата и время сохранения результата | NOT NULL, формат ISO |
| metadata | TEXT | Дополнительные данные в формате JSON | NULL |

**Индексы:**
- `idx_results_prompt_id` на поле `prompt_id` (для поиска по промту)
- `idx_results_model_id` на поле `model_id` (для поиска по модели)
- `idx_results_created_at` на поле `created_at` (для сортировки по дате)

**Пример данных:**
```sql
INSERT INTO results (prompt_id, model_id, prompt_text, model_name, response_text, created_at) 
VALUES (
    1, 
    1, 
    'Объясни квантовую физику', 
    'GPT-4', 
    'Квантовая физика - это раздел физики...', 
    '2024-01-15 10:35:00'
);
```

**Примечание:** Поля `prompt_text` и `model_name` хранятся как копии на момент запроса, чтобы результаты оставались актуальными даже если промт или модель будут изменены или удалены.

---

## Таблица: settings (Настройки)

Хранит настройки программы в формате ключ-значение.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| key | TEXT | Ключ настройки | PRIMARY KEY |
| value | TEXT | Значение настройки | NOT NULL |
| updated_at | TEXT | Дата последнего обновления | NOT NULL, формат ISO |

**Пример данных:**
```sql
INSERT INTO settings (key, value, updated_at) 
VALUES ('default_timeout', '30', '2024-01-15 10:00:00');

INSERT INTO settings (key, value, updated_at) 
VALUES ('auto_save', 'false', '2024-01-15 10:00:00');
```

**Возможные настройки:**
- `default_timeout` - таймаут запросов по умолчанию (секунды)
- `auto_save` - автоматическое сохранение результатов (true/false)
- `theme` - тема интерфейса (light/dark)
- `language` - язык интерфейса (ru/en)
- И другие настройки по необходимости

---

## Связи между таблицами

```
prompts (1) ──< (N) results
              │
              └── prompt_id

models (1) ──< (N) results
              │
              └── model_id
```

- Один промт может иметь множество результатов
- Одна модель может иметь множество результатов
- Результат всегда связан с одним промтом и одной моделью

---

## SQL-скрипт создания таблиц

```sql
-- Таблица промтов
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date);
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    api_key_env_var TEXT NOT NULL,
    model_type TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_models_active ON models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);

-- Таблица результатов
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER,
    model_id INTEGER,
    prompt_text TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id);
CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id);
CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at);

-- Таблица настроек
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## Примеры запросов

### Получить все активные модели:
```sql
SELECT * FROM models WHERE is_active = 1 ORDER BY name;
```

### Получить промты с поиском по тегам:
```sql
SELECT * FROM prompts WHERE tags LIKE '%физика%' ORDER BY date DESC;
```

### Получить результаты для конкретного промта:
```sql
SELECT r.*, m.name as model_name 
FROM results r
JOIN models m ON r.model_id = m.id
WHERE r.prompt_id = 1
ORDER BY r.created_at DESC;
```

### Получить статистику по моделям:
```sql
SELECT m.name, COUNT(r.id) as response_count
FROM models m
LEFT JOIN results r ON m.id = r.model_id
GROUP BY m.id, m.name
ORDER BY response_count DESC;
```


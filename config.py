"""Модуль конфигурации и загрузки переменных окружения"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки базы данных
DB_NAME = "chatlist.db"

# Настройки по умолчанию
DEFAULT_TIMEOUT = 30  # секунды

def get_env_var(var_name: str, default: str = None) -> str:
    """Получить переменную окружения"""
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Переменная окружения {var_name} не установлена")
    return value


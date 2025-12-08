"""Модуль работы с базой данных SQLite"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from config import DB_NAME


class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_name: str = DB_NAME):
        """Инициализация подключения к БД"""
        self.db_name = db_name
        self.conn = None
        self._connect()
        self._init_database()
    
    def _connect(self):
        """Установить соединение с БД"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  # Возвращать результаты как словари
    
    def _init_database(self):
        """Создать таблицы при первом запуске"""
        cursor = self.conn.cursor()
        
        # Таблица промтов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prompt TEXT NOT NULL,
                tags TEXT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)")
        
        # Таблица моделей
        cursor.execute("""
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
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_active ON models(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type)")
        
        # Таблица результатов
        cursor.execute("""
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
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at)")
        
        # Таблица настроек
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def close(self):
        """Закрыть соединение с БД"""
        if self.conn:
            self.conn.close()
    
    # ========== Методы для работы с промтами ==========
    
    def create_prompt(self, prompt: str, tags: Optional[str] = None) -> int:
        """Создать новый промт"""
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO prompts (date, prompt, tags) VALUES (?, ?, ?)",
            (date, prompt, tags)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_prompts(self, search: Optional[str] = None, 
                    order_by: str = "date", 
                    order_dir: str = "DESC") -> List[Dict]:
        """Получить список промтов с поиском и сортировкой"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM prompts"
        params = []
        
        if search:
            query += " WHERE prompt LIKE ? OR tags LIKE ?"
            search_pattern = f"%{search}%"
            params = [search_pattern, search_pattern]
        
        # Валидация порядка сортировки
        valid_columns = ["date", "prompt", "tags"]
        if order_by not in valid_columns:
            order_by = "date"
        if order_dir.upper() not in ["ASC", "DESC"]:
            order_dir = "DESC"
        
        query += f" ORDER BY {order_by} {order_dir}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """Получить промт по ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_prompt(self, prompt_id: int, prompt: str, tags: Optional[str] = None) -> bool:
        """Обновить промт"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE prompts SET prompt = ?, tags = ? WHERE id = ?",
            (prompt, tags, prompt_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """Удалить промт"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ========== Методы для работы с моделями ==========
    
    def create_model(self, name: str, api_url: str, api_id: str, 
                    api_key_env_var: str, model_type: str, 
                    is_active: int = 1) -> int:
        """Добавить новую модель"""
        cursor = self.conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO models (name, api_url, api_id, api_key_env_var, 
                              model_type, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, api_url, api_id, api_key_env_var, model_type, is_active, created_at))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_active_models(self) -> List[Dict]:
        """Получить активные модели"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models WHERE is_active = 1 ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_models(self) -> List[Dict]:
        """Получить все модели"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models ORDER BY name")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_model_by_id(self, model_id: int) -> Optional[Dict]:
        """Получить модель по ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_model(self, model_id: int, name: str = None, api_url: str = None,
                    api_id: str = None, api_key_env_var: str = None,
                    model_type: str = None, is_active: int = None) -> bool:
        """Обновить модель"""
        cursor = self.conn.cursor()
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if api_url is not None:
            updates.append("api_url = ?")
            params.append(api_url)
        if api_id is not None:
            updates.append("api_id = ?")
            params.append(api_id)
        if api_key_env_var is not None:
            updates.append("api_key_env_var = ?")
            params.append(api_key_env_var)
        if model_type is not None:
            updates.append("model_type = ?")
            params.append(model_type)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(updated_at)
        params.append(model_id)
        
        query = f"UPDATE models SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def toggle_model_active(self, model_id: int) -> bool:
        """Переключить активность модели"""
        model = self.get_model_by_id(model_id)
        if not model:
            return False
        new_status = 0 if model['is_active'] else 1
        return self.update_model(model_id, is_active=new_status)
    
    def delete_model(self, model_id: int) -> bool:
        """Удалить модель"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ========== Методы для работы с результатами ==========
    
    def save_result(self, prompt_id: Optional[int], model_id: Optional[int],
                   prompt_text: str, model_name: str, response_text: str,
                   metadata: Optional[Dict] = None) -> int:
        """Сохранить один результат"""
        cursor = self.conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO results (prompt_id, model_id, prompt_text, model_name, 
                               response_text, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (prompt_id, model_id, prompt_text, model_name, response_text, 
              created_at, metadata_json))
        self.conn.commit()
        return cursor.lastrowid
    
    def save_results(self, results: List[Dict]) -> int:
        """Массовое сохранение результатов"""
        cursor = self.conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = 0
        
        for result in results:
            metadata_json = json.dumps(result.get('metadata')) if result.get('metadata') else None
            cursor.execute("""
                INSERT INTO results (prompt_id, model_id, prompt_text, model_name, 
                                   response_text, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result.get('prompt_id'),
                result.get('model_id'),
                result['prompt_text'],
                result['model_name'],
                result['response_text'],
                created_at,
                metadata_json
            ))
            count += 1
        
        self.conn.commit()
        return count
    
    def get_results(self, prompt_id: Optional[int] = None,
                   model_id: Optional[int] = None,
                   search: Optional[str] = None,
                   order_by: str = "created_at",
                   order_dir: str = "DESC") -> List[Dict]:
        """Получить результаты с поиском и сортировкой"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM results WHERE 1=1"
        params = []
        
        if prompt_id is not None:
            query += " AND prompt_id = ?"
            params.append(prompt_id)
        
        if model_id is not None:
            query += " AND model_id = ?"
            params.append(model_id)
        
        if search:
            query += " AND (prompt_text LIKE ? OR model_name LIKE ? OR response_text LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Валидация порядка сортировки
        valid_columns = ["created_at", "model_name", "prompt_text"]
        if order_by not in valid_columns:
            order_by = "created_at"
        if order_dir.upper() not in ["ASC", "DESC"]:
            order_dir = "DESC"
        
        query += f" ORDER BY {order_by} {order_dir}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        # Парсим metadata из JSON
        for result in results:
            if result.get('metadata'):
                try:
                    result['metadata'] = json.loads(result['metadata'])
                except:
                    result['metadata'] = None
        
        return results
    
    def delete_result(self, result_id: int) -> bool:
        """Удалить результат"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ========== Методы для работы с настройками ==========
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Получить настройку"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Сохранить настройку"""
        cursor = self.conn.cursor()
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, updated_at))
        self.conn.commit()
        return True

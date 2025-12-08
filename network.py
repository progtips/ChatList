"""Модуль сетевых запросов к API моделей"""
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import Model, ModelFactory
from config import DEFAULT_TIMEOUT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NetworkManager:
    """Менеджер для отправки запросов к API моделей"""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_workers: int = 5):
        """
        Инициализация менеджера
        
        Args:
            timeout: Таймаут запросов в секундах
            max_workers: Максимальное количество параллельных запросов
        """
        self.timeout = timeout
        self.max_workers = max_workers
    
    def send_to_model(self, model: Model, prompt: str) -> Dict:
        """
        Отправить запрос к одной модели
        
        Args:
            model: Экземпляр модели
            prompt: Текст промта
            
        Returns:
            Словарь с результатом:
            {
                'model_name': str,
                'model_id': int (опционально),
                'success': bool,
                'response': str,
                'error': str
            }
        """
        logger.info(f"Отправка запроса к модели: {model.name}")
        
        try:
            result = model.send_request(prompt)
            
            response_dict = {
                'model_name': model.name,
                'success': result['success'],
                'response': result.get('response'),
                'error': result.get('error')
            }
            
            if result['success']:
                logger.info(f"Успешный ответ от модели: {model.name}")
            else:
                logger.warning(f"Ошибка от модели {model.name}: {result.get('error')}")
            
            return response_dict
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {model.name}: {str(e)}")
            return {
                'model_name': model.name,
                'success': False,
                'response': None,
                'error': f'Неожиданная ошибка: {str(e)}'
            }
    
    def send_to_all_models(self, prompt: str, models: List[Model]) -> List[Dict]:
        """
        Отправить промт во все модели параллельно
        
        Args:
            prompt: Текст промта
            models: Список экземпляров моделей
            
        Returns:
            Список словарей с результатами в едином формате:
            [
                {
                    'model_name': str,
                    'success': bool,
                    'response': str,
                    'error': str
                },
                ...
            ]
        """
        if not models:
            logger.warning("Список моделей пуст")
            return []
        
        logger.info(f"Отправка промта в {len(models)} моделей")
        
        results = []
        
        # Используем ThreadPoolExecutor для параллельной обработки
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Запускаем все запросы параллельно
            future_to_model = {
                executor.submit(self.send_to_model, model, prompt): model
                for model in models
            }
            
            # Собираем результаты по мере их готовности
            for future in as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Ошибка при выполнении запроса к {model.name}: {str(e)}")
                    results.append({
                        'model_name': model.name,
                        'success': False,
                        'response': None,
                        'error': f'Ошибка выполнения: {str(e)}'
                    })
        
        logger.info(f"Получено {len(results)} результатов")
        return results
    
    def send_to_models_from_db(self, prompt: str, db, model_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Отправить промт в модели из БД
        
        Args:
            prompt: Текст промта
            db: Экземпляр Database
            model_ids: Список ID моделей (если None, используются все активные)
            
        Returns:
            Список словарей с результатами
        """
        if model_ids:
            models_data = []
            for model_id in model_ids:
                model_data = db.get_model_by_id(model_id)
                if model_data:
                    models_data.append(model_data)
        else:
            models_data = db.get_active_models()
        
        if not models_data:
            logger.warning("Не найдено активных моделей")
            return []
        
        # Создаем экземпляры моделей из данных БД
        models = []
        for model_data in models_data:
            model = ModelFactory.create_model_from_db(model_data)
            if model:
                models.append(model)
            else:
                logger.warning(f"Не удалось создать модель типа {model_data.get('model_type')}")
        
        return self.send_to_all_models(prompt, models)
    
    def process_response(self, response: Dict) -> Dict:
        """
        Обработать ответ от API (унификация формата)
        
        Args:
            response: Словарь с ответом от модели
            
        Returns:
            Обработанный словарь в едином формате
        """
        # Базовая обработка уже выполнена в send_to_model
        # Этот метод можно расширить для дополнительной обработки
        return {
            'model_name': response.get('model_name', 'Unknown'),
            'success': response.get('success', False),
            'response': response.get('response', ''),
            'error': response.get('error')
        }

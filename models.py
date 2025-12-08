"""Модуль работы с моделями нейросетей"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from config import get_env_var


class Model(ABC):
    """Базовый класс для моделей нейросетей"""
    
    def __init__(self, name: str, api_url: str, api_id: str, 
                 api_key_env_var: str, is_active: bool = True):
        """
        Инициализация модели
        
        Args:
            name: Название модели
            api_url: URL API для отправки запросов
            api_id: Идентификатор модели в API
            api_key_env_var: Имя переменной окружения с API-ключом
            is_active: Активна ли модель
        """
        self.name = name
        self.api_url = api_url
        self.api_id = api_id
        self.api_key_env_var = api_key_env_var
        self.is_active = is_active
        self._api_key = None
    
    def get_api_key(self) -> str:
        """Получить API-ключ из переменной окружения"""
        if self._api_key is None:
            self._api_key = get_env_var(self.api_key_env_var)
        return self._api_key
    
    @abstractmethod
    def send_request(self, prompt: str) -> Dict:
        """
        Отправить запрос к модели
        
        Args:
            prompt: Текст промта
            
        Returns:
            Словарь с результатом: {'success': bool, 'response': str, 'error': str}
        """
        pass
    
    def to_dict(self) -> Dict:
        """Преобразовать модель в словарь"""
        return {
            'name': self.name,
            'api_url': self.api_url,
            'api_id': self.api_id,
            'api_key_env_var': self.api_key_env_var,
            'is_active': self.is_active
        }


class OpenAIModel(Model):
    """Модель для OpenAI API"""
    
    def send_request(self, prompt: str) -> Dict:
        """Отправить запрос к OpenAI API"""
        import requests
        import json
        
        api_key = self.get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.api_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'response': response_text,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Неожиданный формат ответа от API'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'response': None,
                'error': f'Ошибка запроса: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Неожиданная ошибка: {str(e)}'
            }


class DeepSeekModel(Model):
    """Модель для DeepSeek API"""
    
    def send_request(self, prompt: str) -> Dict:
        """Отправить запрос к DeepSeek API"""
        import requests
        import json
        
        api_key = self.get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.api_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'response': response_text,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Неожиданный формат ответа от API'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'response': None,
                'error': f'Ошибка запроса: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Неожиданная ошибка: {str(e)}'
            }


class GroqModel(Model):
    """Модель для Groq API"""
    
    def send_request(self, prompt: str) -> Dict:
        """Отправить запрос к Groq API"""
        import requests
        import json
        
        api_key = self.get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.api_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'response': response_text,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Неожиданный формат ответа от API'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'response': None,
                'error': f'Ошибка запроса: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Неожиданная ошибка: {str(e)}'
            }


class OpenRouterModel(Model):
    """Модель для OpenRouter API"""
    
    def send_request(self, prompt: str) -> Dict:
        """Отправить запрос к OpenRouter API"""
        import requests
        import json
        
        api_key = self.get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Рекомендуется для OpenRouter
            "X-Title": "ChatList"  # Опционально, название приложения
        }
        
        data = {
            "model": self.api_id,  # Полное имя модели, например "mistralai/mistral-7b-instruct"
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            # Проверяем статус код перед парсингом JSON
            if response.status_code != 200:
                error_message = self._parse_openrouter_error(response)
                return {
                    'success': False,
                    'response': None,
                    'error': error_message
                }
            
            # Если статус 200, парсим ответ
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'response': response_text,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Неожиданный формат ответа от API'
                }
        except requests.exceptions.HTTPError as e:
            # Обработка HTTP ошибок (когда raise_for_status() вызывается)
            error_message = self._parse_openrouter_error(e.response if hasattr(e, 'response') and e.response else None)
            return {
                'success': False,
                'response': None,
                'error': error_message
            }
        except requests.exceptions.RequestException as e:
            # Для других ошибок запросов пытаемся извлечь информацию об ошибке
            error_msg = str(e)
            # Если это ошибка с кодом статуса в сообщении, пытаемся обработать
            if '404' in error_msg:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Модель "{self.api_id}" не найдена (404). Проверьте правильность имени модели на https://openrouter.ai/models'
                }
            elif '402' in error_msg:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Требуется оплата. Модель "{self.api_id}" требует пополнения баланса на OpenRouter.'
                }
            elif '429' in error_msg:
                return {
                    'success': False,
                    'response': None,
                    'error': 'Превышен лимит запросов. Подождите 1-2 минуты и попробуйте снова.'
                }
            else:
                return {
                    'success': False,
                    'response': None,
                    'error': f'Ошибка запроса: {error_msg}'
                }
        except Exception as e:
            return {
                'success': False,
                'response': None,
                'error': f'Неожиданная ошибка: {str(e)}'
            }
    
    def _parse_openrouter_error(self, response):
        """Парсинг ошибок OpenRouter API для понятных сообщений"""
        status_code = response.status_code if response else None
        
        # Пытаемся извлечь детали ошибки из ответа
        error_detail = ""
        try:
            if response:
                error_data = response.json()
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_detail = error_data['error'].get('message', '')
                    else:
                        error_detail = str(error_data['error'])
        except:
            pass
        
        if status_code == 400:
            msg = 'Неверный запрос. Проверьте правильность имени модели и формат данных.'
            if error_detail:
                msg += f' Детали: {error_detail}'
            return msg
        elif status_code == 401:
            return 'Неверный API-ключ. Проверьте ключ OPENROUTER_API_KEY в файле .env'
        elif status_code == 402:
            return f'Требуется оплата. Модель "{self.api_id}" требует пополнения баланса на OpenRouter. Попробуйте бесплатную модель или пополните баланс.'
        elif status_code == 404:
            return f'Модель "{self.api_id}" не найдена. Проверьте правильность имени модели на https://openrouter.ai/models'
        elif status_code == 429:
            return 'Превышен лимит запросов (Too Many Requests). Подождите 1-2 минуты и попробуйте снова. Возможно, вы превысили лимит бесплатных запросов.'
        elif status_code == 500:
            return 'Ошибка сервера OpenRouter. Попробуйте позже.'
        elif status_code:
            msg = f'Ошибка {status_code}'
            if error_detail:
                msg += f': {error_detail}'
            else:
                msg += f': {str(response.text[:100]) if response else "Неизвестная ошибка"}'
            return msg
        else:
            return 'Неизвестная ошибка при запросе к OpenRouter'


class ModelFactory:
    """Фабрика для создания экземпляров моделей из данных БД"""
    
    _model_classes = {
        'openai': OpenAIModel,
        'deepseek': DeepSeekModel,
        'groq': GroqModel,
        'openrouter': OpenRouterModel
    }
    
    @classmethod
    def create_model_from_db(cls, model_data: Dict) -> Optional[Model]:
        """
        Создать экземпляр модели из данных БД
        
        Args:
            model_data: Словарь с данными модели из БД
            
        Returns:
            Экземпляр модели или None, если тип модели не поддерживается
        """
        model_type = model_data.get('model_type', '').lower()
        model_class = cls._model_classes.get(model_type)
        
        if not model_class:
            return None
        
        return model_class(
            name=model_data['name'],
            api_url=model_data['api_url'],
            api_id=model_data['api_id'],
            api_key_env_var=model_data['api_key_env_var'],
            is_active=bool(model_data.get('is_active', 1))
        )
    
    @classmethod
    def register_model_type(cls, model_type: str, model_class: type):
        """Зарегистрировать новый тип модели"""
        cls._model_classes[model_type.lower()] = model_class

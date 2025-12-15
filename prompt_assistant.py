"""Модуль для улучшения промтов с помощью AI"""
import re
import json
import logging
from typing import Dict, List, Optional
from models import Model
from network import NetworkManager

logger = logging.getLogger(__name__)


class PromptAssistant:
    """Класс для работы с улучшением промтов"""
    
    def __init__(self, network_manager: Optional[NetworkManager] = None):
        """
        Инициализация ассистента
        
        Args:
            network_manager: Менеджер сетевых запросов (если None, создается новый)
        """
        self.network_manager = network_manager or NetworkManager()
        self.cache = {}  # Простой кэш для одинаковых промтов
    
    def improve_prompt(self, prompt: str, model: Model) -> Dict:
        """
        Улучшить промт с помощью AI модели
        
        Args:
            prompt: Исходный промт
            model: Модель для улучшения
            
        Returns:
            Словарь с результатом:
            {
                'success': bool,
                'improved_prompt': str,
                'error': str
            }
        """
        # Проверяем кэш
        cache_key = f"{model.name}:{prompt[:100]}"
        if cache_key in self.cache:
            logger.info("Использован кэш для улучшения промта")
            return self.cache[cache_key]
        
        # Формируем промпт для улучшения
        improvement_prompt = self._create_improvement_prompt(prompt)
        
        # Отправляем запрос
        result = self.network_manager.send_to_model(model, improvement_prompt)
        
        if result.get('success'):
            improved = self._parse_improved_prompt(result.get('response', ''))
            response = {
                'success': True,
                'improved_prompt': improved,
                'error': None
            }
            # Сохраняем в кэш
            self.cache[cache_key] = response
            return response
        else:
            return {
                'success': False,
                'improved_prompt': None,
                'error': result.get('error', 'Неизвестная ошибка')
            }
    
    def generate_variants(self, prompt: str, model: Model, count: int = 3) -> Dict:
        """
        Сгенерировать варианты переформулировки промта
        
        Args:
            prompt: Исходный промт
            model: Модель для генерации
            count: Количество вариантов (2-3)
            
        Returns:
            Словарь с результатом:
            {
                'success': bool,
                'variants': List[str],
                'error': str
            }
        """
        # Формируем промпт для генерации вариантов
        variants_prompt = self._create_variants_prompt(prompt, count)
        
        # Отправляем запрос
        result = self.network_manager.send_to_model(model, variants_prompt)
        
        if result.get('success'):
            variants = self._parse_variants(result.get('response', ''), count)
            return {
                'success': True,
                'variants': variants,
                'error': None
            }
        else:
            return {
                'success': False,
                'variants': [],
                'error': result.get('error', 'Неизвестная ошибка')
            }
    
    def adapt_for_model_type(self, prompt: str, model_type: str, model: Model) -> Dict:
        """
        Адаптировать промт под тип модели
        
        Args:
            prompt: Исходный промт
            model_type: Тип модели ('code', 'analysis', 'creative')
            model: Модель для адаптации
            
        Returns:
            Словарь с результатом:
            {
                'success': bool,
                'adapted_prompt': str,
                'error': str
            }
        """
        # Формируем промпт для адаптации
        adaptation_prompt = self._create_adaptation_prompt(prompt, model_type)
        
        # Отправляем запрос
        result = self.network_manager.send_to_model(model, adaptation_prompt)
        
        if result.get('success'):
            adapted = self._parse_improved_prompt(result.get('response', ''))
            return {
                'success': True,
                'adapted_prompt': adapted,
                'error': None
            }
        else:
            return {
                'success': False,
                'adapted_prompt': None,
                'error': result.get('error', 'Неизвестная ошибка')
            }
    
    def improve_with_variants(self, prompt: str, model: Model, 
                             generate_variants: bool = True,
                             adapt_for_type: Optional[str] = None) -> Dict:
        """
        Комплексное улучшение промта с вариантами
        
        Args:
            prompt: Исходный промт
            model: Модель для улучшения
            generate_variants: Генерировать ли варианты переформулировки
            adapt_for_type: Тип адаптации ('code', 'analysis', 'creative') или None
            
        Returns:
            Словарь с результатом:
            {
                'success': bool,
                'improved_prompt': str,
                'variants': List[str],
                'adapted_prompt': Optional[str],
                'error': str
            }
        """
        result = {
            'success': False,
            'improved_prompt': None,
            'variants': [],
            'adapted_prompt': None,
            'error': None
        }
        
        # Улучшаем основной промт
        improved_result = self.improve_prompt(prompt, model)
        if not improved_result.get('success'):
            result['error'] = improved_result.get('error')
            return result
        
        result['improved_prompt'] = improved_result.get('improved_prompt')
        result['success'] = True
        
        # Генерируем варианты, если нужно
        if generate_variants:
            variants_result = self.generate_variants(prompt, model)
            if variants_result.get('success'):
                result['variants'] = variants_result.get('variants', [])
            else:
                logger.warning(f"Не удалось сгенерировать варианты: {variants_result.get('error')}")
        
        # Адаптируем под тип, если указан
        if adapt_for_type:
            adapted_result = self.adapt_for_model_type(prompt, adapt_for_type, model)
            if adapted_result.get('success'):
                result['adapted_prompt'] = adapted_result.get('adapted_prompt')
            else:
                logger.warning(f"Не удалось адаптировать промт: {adapted_result.get('error')}")
        
        return result
    
    def _create_improvement_prompt(self, prompt: str) -> str:
        """Создать промпт для улучшения"""
        return f"""Ты эксперт по написанию эффективных промптов для AI-моделей. 

Задача: улучши следующий промпт, сделав его более четким, конкретным и эффективным.

Исходный промпт:
{prompt}

Требования к улучшенному промпту:
1. Сохрани основную суть и цель исходного промпта
2. Сделай формулировку более четкой и конкретной
3. Добавь контекст, если это улучшит понимание задачи
4. Используй структурированный формат, если это уместно
5. Убедись, что промпт понятен и не содержит двусмысленностей

Верни ТОЛЬКО улучшенную версию промпта, без дополнительных объяснений и комментариев."""

    def _create_variants_prompt(self, prompt: str, count: int) -> str:
        """Создать промпт для генерации вариантов"""
        return f"""Ты эксперт по написанию промптов для AI-моделей.

Задача: создай {count} различных варианта переформулировки следующего промпта. Каждый вариант должен передавать ту же суть, но использовать разные формулировки и подходы.

Исходный промпт:
{prompt}

Требования:
- Каждый вариант должен быть эффективным и понятным
- Варианты должны отличаться по стилю и структуре
- Сохрани основную цель и смысл исходного промпта

Верни варианты в следующем формате:
Вариант 1: [текст первого варианта]
Вариант 2: [текст второго варианта]
Вариант 3: [текст третьего варианта]

Если нужно меньше вариантов, используй только необходимое количество."""

    def _create_adaptation_prompt(self, prompt: str, model_type: str) -> str:
        """Создать промпт для адаптации под тип модели"""
        type_descriptions = {
            'code': 'программирование и разработка кода',
            'analysis': 'анализ данных и логическое мышление',
            'creative': 'креативные задачи и творчество'
        }
        
        description = type_descriptions.get(model_type.lower(), 'специфические задачи')
        
        return f"""Ты эксперт по адаптации промптов для разных типов AI-моделей.

Задача: адаптируй следующий промпт для модели, специализирующейся на {description}.

Исходный промпт:
{prompt}

Требования к адаптации:
1. Сохрани основную цель промпта
2. Адаптируй формулировку под специализацию модели ({description})
3. Используй терминологию и подходы, характерные для этого типа задач
4. Сделай промпт максимально эффективным для данной специализации

Верни ТОЛЬКО адаптированную версию промпта, без дополнительных объяснений."""

    def _parse_improved_prompt(self, response: str) -> str:
        """Парсить улучшенный промт из ответа модели"""
        # Убираем лишние пробелы и переносы строк
        cleaned = response.strip()
        
        # Пытаемся найти промт в различных форматах
        # Формат: "Улучшенный промпт: ..."
        match = re.search(r'(?:улучшенный|improved|результат)[\s:]*\n*(.+?)(?:\n\n|\Z)', cleaned, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Формат: "```\n...\n```"
        match = re.search(r'```(?:prompt|text)?\n?(.+?)\n?```', cleaned, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Формат: "**Промпт:** ..."
        match = re.search(r'\*\*[^*]+\*\*[\s:]*\n*(.+?)(?:\n\n|\Z)', cleaned, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Если ничего не найдено, возвращаем весь ответ
        return cleaned

    def _parse_variants(self, response: str, expected_count: int) -> List[str]:
        """Парсить варианты переформулировки из ответа модели"""
        variants = []
        
        # Пытаемся найти варианты в формате "Вариант 1: ..."
        pattern = r'вариант\s+\d+[\s:]*\n*(.+?)(?=\n*вариант\s+\d+|$)'
        matches = re.finditer(pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            variant = match.group(1).strip()
            # Убираем маркеры списка и лишние символы
            variant = re.sub(r'^[-*•]\s*', '', variant, flags=re.MULTILINE)
            variant = re.sub(r'^\d+[.)]\s*', '', variant, flags=re.MULTILINE)
            if variant:
                variants.append(variant)
        
        # Если не нашли в формате "Вариант N:", пытаемся найти пронумерованный список
        if not variants:
            pattern = r'(?:^|\n)(?:\d+[.)]|[-*•])\s*(.+?)(?=\n(?:^\d+[.)]|[-*•])|$)'
            matches = re.finditer(pattern, response, re.MULTILINE | re.DOTALL)
            for match in matches:
                variant = match.group(1).strip()
                if variant and len(variant) > 10:  # Минимальная длина варианта
                    variants.append(variant)
        
        # Если все еще нет вариантов, пытаемся разбить по параграфам
        if not variants:
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            # Берем первые N параграфов как варианты
            variants = paragraphs[:expected_count]
        
        # Ограничиваем количество вариантов
        return variants[:expected_count]







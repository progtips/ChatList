"""Тесты для модуля моделей"""
import unittest
from unittest.mock import Mock, patch
from models import OpenAIModel, OpenRouterModel, ModelFactory


class TestModels(unittest.TestCase):
    """Тесты для классов моделей"""
    
    @patch('models.get_env_var')
    def test_openai_model_init(self, mock_get_env):
        """Тест инициализации OpenAI модели"""
        mock_get_env.return_value = "test-key"
        model = OpenAIModel(
            "GPT-4", "https://api.openai.com/v1/chat/completions",
            "gpt-4", "OPENAI_API_KEY"
        )
        self.assertEqual(model.name, "GPT-4")
        self.assertEqual(model.api_id, "gpt-4")
    
    @patch('models.get_env_var')
    def test_openrouter_model_init(self, mock_get_env):
        """Тест инициализации OpenRouter модели"""
        mock_get_env.return_value = "test-key"
        model = OpenRouterModel(
            "GPT-4 Turbo", "https://openrouter.ai/api/v1/chat/completions",
            "openai/gpt-4-turbo", "OPENROUTER_API_KEY"
        )
        self.assertEqual(model.name, "GPT-4 Turbo")
        self.assertEqual(model.api_id, "openai/gpt-4-turbo")
    
    @patch('requests.post')
    @patch('models.get_env_var')
    def test_openai_model_send_request_success(self, mock_get_env, mock_post):
        """Тест успешной отправки запроса к OpenAI"""
        mock_get_env.return_value = "test-key"
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Тестовый ответ'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        model = OpenAIModel("GPT-4", "https://api.openai.com/v1/chat/completions",
                           "gpt-4", "OPENAI_API_KEY")
        result = model.send_request("Тестовый промт")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['response'], 'Тестовый ответ')
    
    @patch('requests.post')
    @patch('models.get_env_var')
    def test_openai_model_send_request_error(self, mock_get_env, mock_post):
        """Тест обработки ошибки при запросе к OpenAI"""
        mock_get_env.return_value = "test-key"
        mock_post.side_effect = Exception("Ошибка сети")
        
        model = OpenAIModel("GPT-4", "https://api.openai.com/v1/chat/completions",
                           "gpt-4", "OPENAI_API_KEY")
        result = model.send_request("Тестовый промт")
        
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
    
    def test_model_factory_create_openai(self):
        """Тест создания OpenAI модели через фабрику"""
        model_data = {
            'name': 'GPT-4',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_id': 'gpt-4',
            'api_key_env_var': 'OPENAI_API_KEY',
            'model_type': 'openai',
            'is_active': 1
        }
        
        with patch('models.get_env_var', return_value="test-key"):
            model = ModelFactory.create_model_from_db(model_data)
            self.assertIsNotNone(model)
            self.assertIsInstance(model, OpenAIModel)
    
    def test_model_factory_create_openrouter(self):
        """Тест создания OpenRouter модели через фабрику"""
        model_data = {
            'name': 'GPT-4 Turbo',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'openai/gpt-4-turbo',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        }
        
        with patch('models.get_env_var', return_value="test-key"):
            model = ModelFactory.create_model_from_db(model_data)
            self.assertIsNotNone(model)
            self.assertIsInstance(model, OpenRouterModel)
    
    def test_model_factory_unknown_type(self):
        """Тест обработки неизвестного типа модели"""
        model_data = {
            'name': 'Unknown Model',
            'api_url': 'https://api.test.com',
            'api_id': 'test',
            'api_key_env_var': 'TEST_KEY',
            'model_type': 'unknown_type',
            'is_active': 1
        }
        
        model = ModelFactory.create_model_from_db(model_data)
        self.assertIsNone(model)


if __name__ == '__main__':
    unittest.main()


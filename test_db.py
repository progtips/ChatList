"""Тесты для модуля базы данных"""
import unittest
import os
import tempfile
from db import Database


class TestDatabase(unittest.TestCase):
    """Тесты для класса Database"""
    
    def setUp(self):
        """Создать временную БД для тестов"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(db_name=self.temp_db.name)
    
    def tearDown(self):
        """Удалить временную БД после тестов"""
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_prompt(self):
        """Тест создания промта"""
        prompt_id = self.db.create_prompt("Тестовый промт", "тест")
        self.assertIsNotNone(prompt_id)
        self.assertGreater(prompt_id, 0)
    
    def test_get_prompt_by_id(self):
        """Тест получения промта по ID"""
        prompt_id = self.db.create_prompt("Тестовый промт", "тест")
        prompt = self.db.get_prompt_by_id(prompt_id)
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt['prompt'], "Тестовый промт")
        self.assertEqual(prompt['tags'], "тест")
    
    def test_get_prompts(self):
        """Тест получения списка промтов"""
        self.db.create_prompt("Промт 1", "тег1")
        self.db.create_prompt("Промт 2", "тег2")
        prompts = self.db.get_prompts()
        self.assertEqual(len(prompts), 2)
    
    def test_search_prompts(self):
        """Тест поиска промтов"""
        self.db.create_prompt("Промт про Python", "python")
        self.db.create_prompt("Промт про Java", "java")
        results = self.db.get_prompts(search="Python")
        self.assertEqual(len(results), 1)
        self.assertIn("Python", results[0]['prompt'])
    
    def test_update_prompt(self):
        """Тест обновления промта"""
        prompt_id = self.db.create_prompt("Старый промт", "старый")
        success = self.db.update_prompt(prompt_id, "Новый промт", "новый")
        self.assertTrue(success)
        prompt = self.db.get_prompt_by_id(prompt_id)
        self.assertEqual(prompt['prompt'], "Новый промт")
    
    def test_delete_prompt(self):
        """Тест удаления промта"""
        prompt_id = self.db.create_prompt("Удаляемый промт")
        success = self.db.delete_prompt(prompt_id)
        self.assertTrue(success)
        prompt = self.db.get_prompt_by_id(prompt_id)
        self.assertIsNone(prompt)
    
    def test_create_model(self):
        """Тест создания модели"""
        model_id = self.db.create_model(
            "Test Model", "https://api.test.com", "test-model",
            "TEST_API_KEY", "test", 1
        )
        self.assertIsNotNone(model_id)
        self.assertGreater(model_id, 0)
    
    def test_get_active_models(self):
        """Тест получения активных моделей"""
        self.db.create_model("Active Model", "https://api.test.com", "active",
                            "TEST_KEY", "test", 1)
        self.db.create_model("Inactive Model", "https://api.test.com", "inactive",
                            "TEST_KEY", "test", 0)
        active = self.db.get_active_models()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]['name'], "Active Model")
    
    def test_toggle_model_active(self):
        """Тест переключения активности модели"""
        model_id = self.db.create_model("Test Model", "https://api.test.com",
                                       "test", "TEST_KEY", "test", 1)
        model = self.db.get_model_by_id(model_id)
        self.assertEqual(model['is_active'], 1)
        
        self.db.toggle_model_active(model_id)
        model = self.db.get_model_by_id(model_id)
        self.assertEqual(model['is_active'], 0)
    
    def test_save_result(self):
        """Тест сохранения результата"""
        prompt_id = self.db.create_prompt("Тест")
        model_id = self.db.create_model("Test Model", "https://api.test.com",
                                       "test", "TEST_KEY", "test", 1)
        
        result_id = self.db.save_result(
            prompt_id, model_id, "Тест промт", "Test Model", "Тестовый ответ"
        )
        self.assertIsNotNone(result_id)
        self.assertGreater(result_id, 0)
    
    def test_save_results(self):
        """Тест массового сохранения результатов"""
        prompt_id = self.db.create_prompt("Тест")
        results = [
            {
                'prompt_id': prompt_id,
                'model_id': None,
                'prompt_text': 'Тест',
                'model_name': 'Model 1',
                'response_text': 'Ответ 1'
            },
            {
                'prompt_id': prompt_id,
                'model_id': None,
                'prompt_text': 'Тест',
                'model_name': 'Model 2',
                'response_text': 'Ответ 2'
            }
        ]
        count = self.db.save_results(results)
        self.assertEqual(count, 2)
    
    def test_get_results(self):
        """Тест получения результатов"""
        prompt_id = self.db.create_prompt("Тест")
        self.db.save_result(prompt_id, None, "Тест", "Model", "Ответ")
        results = self.db.get_results()
        self.assertEqual(len(results), 1)
    
    def test_get_setting(self):
        """Тест получения настройки"""
        self.db.set_setting("test_key", "test_value")
        value = self.db.get_setting("test_key")
        self.assertEqual(value, "test_value")
    
    def test_set_setting(self):
        """Тест сохранения настройки"""
        success = self.db.set_setting("test_key", "test_value")
        self.assertTrue(success)
        value = self.db.get_setting("test_key")
        self.assertEqual(value, "test_value")


if __name__ == '__main__':
    unittest.main()


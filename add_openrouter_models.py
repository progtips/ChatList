"""Скрипт для добавления моделей OpenRouter в базу данных"""
from db import Database
from datetime import datetime

def add_openrouter_models():
    """Добавить популярные модели OpenRouter в БД"""
    db = Database()
    
    models_to_add = [
        {
            'name': 'GPT-4 Turbo (OpenRouter)',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'openai/gpt-4-turbo',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        },
        {
            'name': 'Claude 3.5 Sonnet (OpenRouter)',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'anthropic/claude-3.5-sonnet',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        },
        {
            'name': 'Gemini Pro (OpenRouter)',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'google/gemini-pro',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        },
        {
            'name': 'Llama 2 70B (OpenRouter)',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'meta-llama/llama-2-70b-chat',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        },
        {
            'name': 'Mistral 7B (OpenRouter)',
            'api_url': 'https://openrouter.ai/api/v1/chat/completions',
            'api_id': 'mistralai/mistral-7b-instruct',
            'api_key_env_var': 'OPENROUTER_API_KEY',
            'model_type': 'openrouter',
            'is_active': 1
        }
    ]
    
    added_count = 0
    skipped_count = 0
    
    print("Добавление моделей OpenRouter в базу данных...")
    print("-" * 60)
    
    for model_data in models_to_add:
        try:
            # Проверяем, существует ли уже модель с таким именем
            existing_models = db.get_all_models()
            model_exists = any(m['name'] == model_data['name'] for m in existing_models)
            
            if model_exists:
                print(f"⚠ Пропущено: {model_data['name']} (уже существует)")
                skipped_count += 1
            else:
                db.create_model(
                    name=model_data['name'],
                    api_url=model_data['api_url'],
                    api_id=model_data['api_id'],
                    api_key_env_var=model_data['api_key_env_var'],
                    model_type=model_data['model_type'],
                    is_active=model_data['is_active']
                )
                print(f"✓ Добавлено: {model_data['name']}")
                added_count += 1
        except Exception as e:
            print(f"✗ Ошибка при добавлении {model_data['name']}: {str(e)}")
    
    print("-" * 60)
    print(f"Итого: добавлено {added_count}, пропущено {skipped_count}")
    
    # Показываем список всех моделей OpenRouter
    print("\nСписок всех моделей OpenRouter в базе:")
    all_models = db.get_all_models()
    openrouter_models = [m for m in all_models if m['model_type'] == 'openrouter']
    for model in openrouter_models:
        status = "✓ Активна" if model['is_active'] else "✗ Неактивна"
        print(f"  - {model['name']} ({model['api_id']}) - {status}")
    
    db.close()

if __name__ == "__main__":
    add_openrouter_models()


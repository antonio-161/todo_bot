import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'todo_bot'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Валидация переменных окружения
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных среды")

required_db_fields = ['user', 'password']
missing_fields = [
    field for field in required_db_fields
    if not DB_CONFIG[field]
]

# Валидация конфигурации БД
if missing_fields:
    raise ValueError(
        f"Не заданы обязательные параметры БД: {', '.join(missing_fields)}"
    )

# Первоначальная конфигурация БД
INIT_DB_USER = os.getenv('INIT_DB_USER', 'postgres')
INIT_DB_PASS = os.getenv('INIT_DB_PASS', 'your_admin_password')
INIT_DB_HOST = os.getenv('INIT_DB_HOST', 'localhost')
INIT_DB_PORT = int(os.getenv('INIT_DB_PORT', 5432))
INIT_DB_NAME = os.getenv('INIT_DB_NAME', 'todo_bot')


# Валидация конфигурации для инициализации БД (если заданы)
def validate_init_config():
    """Валидация конфигурации для инициализации БД"""
    required_init_fields = {
        'INIT_DB_USER': INIT_DB_USER,
        'INIT_DB_PASS': INIT_DB_PASS,
        'INIT_DB_HOST': INIT_DB_HOST,
        'INIT_DB_NAME': INIT_DB_NAME
    }

    missing_init_fields = [
        field for field, value in required_init_fields.items()
        if not value or value == 'your_admin_password'
    ]

    if missing_init_fields:
        raise ValueError(
            "Не заданы параметры "
            f"инициализации БД: {', '.join(missing_init_fields)}"
        )

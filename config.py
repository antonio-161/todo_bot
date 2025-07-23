import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'todo_bot'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных среды")

if not all([DB_CONFIG['user'], DB_CONFIG['password']]):
    raise ValueError(
        "Пользователь и пароль базы данных не заданы в переменных среды"
    )

# Initial database configuration
INIT_DB_USER = os.getenv('INIT_DB_USER', 'postgres')
INIT_DB_PASS = os.getenv('INIT_DB_PASS', 'your_admin_password')
INIT_DB_HOST = os.getenv('INIT_DB_HOST', 'localhost')
INIT_DB_PORT = int(os.getenv('INIT_DB_PORT', 5432))
INIT_DB_NAME = os.getenv('INIT_DB_NAME', 'todo_bot')

# Validate initial database configuration
if not all([INIT_DB_USER, INIT_DB_PASS, INIT_DB_NAME]):
    raise ValueError(
        (
            "В переменных среды не указаны имя пользователя, "
            "пароль или название исходной базы данных"
        )
    )
if not INIT_DB_HOST or not INIT_DB_PORT:
    raise ValueError(
        "В переменных среды не указаны хост или порт исходной базы данных"
    )

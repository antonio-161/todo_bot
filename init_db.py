import asyncpg
import asyncio
from pathlib import Path
from config import (
    INIT_DB_USER,
    INIT_DB_PASS,
    INIT_DB_HOST,
    INIT_DB_PORT,
    INIT_DB_NAME,
    validate_init_config
)


async def run_init_sql():
    """Инициализация базы данных из SQL-скрипта"""
    try:
        # Валидируем конфигурацию
        validate_init_config()

        # Проверяем наличие SQL-файла
        sql_file = Path("init_db.sql")
        if not sql_file.exists():
            print("❌ Файл init_db.sql не найден")
            return False

        # Читаем SQL-скрипт
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Подключение к базе данных
        print(
            f"🔗 Подключение к БД {INIT_DB_NAME} "
            f"на {INIT_DB_HOST}:{INIT_DB_PORT}"
        )
        conn = await asyncpg.connect(
            user=INIT_DB_USER,
            password=INIT_DB_PASS,
            database=INIT_DB_NAME,
            host=INIT_DB_HOST,
            port=INIT_DB_PORT
        )

        try:
            # Проверка существования таблицы
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'tasks'
                );
            """)

            if table_exists:
                print(
                    "ℹ️ Таблица 'tasks' уже существует. "
                    "Инициализация не требуется."
                )
                return True
            else:
                # Выполняем скрипт инициализации
                await conn.execute(sql_script)
                print("✅ База данных успешно инициализирована.")
                return True

        finally:
            await conn.close()
            print("🔒 Соединение с БД закрыто")

    except asyncpg.PostgresError as e:
        print(f"❌ Ошибка PostgreSQL: {e}")
        return False
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_init_sql())
    exit(0 if success else 1)

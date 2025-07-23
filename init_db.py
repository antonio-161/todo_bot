import asyncpg
import asyncio
from config import (
    INIT_DB_USER,
    INIT_DB_PASS,
    INIT_DB_HOST,
    INIT_DB_PORT,
    INIT_DB_NAME
)


async def run_init_sql():
    # Читаем SQL-скрипт
    with open("init_db.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Подключение
    conn = await asyncpg.connect(
        user=INIT_DB_USER,
        password=INIT_DB_PASS,
        database=INIT_DB_NAME,
        host=INIT_DB_HOST,
        port=INIT_DB_PORT
    )

    try:
        # Проверка таблицы
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
        else:
            await conn.execute(sql_script)
            print("✅ Таблица создана по скрипту.")
    except Exception as e:
        print("❌ Ошибка при инициализации:", e)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_init_sql())

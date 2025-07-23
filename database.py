import asyncpg
import logging
import sys

from typing import List, Dict, Optional

from config import DB_CONFIG

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        """Создание пула подключений к БД"""
        try:
            self.pool = await asyncpg.create_pool(**DB_CONFIG)
            await self.create_tables()
            logger.info("Подключение к базе данных установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    async def close_pool(self):
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()
            logger.info("Подключение к базе данных закрыто")

    async def create_tables(self):
        """Создание таблиц в БД"""
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            task_text TEXT NOT NULL,
            status BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
        CREATE INDEX IF NOT EXISTS idx_tasks_completed_at
        ON tasks(completed_at);
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query)
        logger.info("Таблицы созданы")

    async def add_task(self, user_id: int, task_text: str) -> int:
        """Добавление новой задачи"""
        query = """
        INSERT INTO tasks (user_id, task_text)
        VALUES ($1, $2)
        RETURNING id
        """

        # Добавляем задачу в базу данных
        async with self.pool.acquire() as connection:
            task_id = await connection.fetchval(query, user_id, task_text)
            logger.info(
                f"Добавлена задача {task_id} для пользователя {user_id}"
            )
            return task_id

    async def get_user_tasks(
            self,
            user_id: int,
            include_completed: bool = False
    ) -> List[Dict]:
        """Получение задач пользователя"""
        # Фильтрация задач
        if include_completed:
            query = """
            SELECT id, task_text, status, created_at, completed_at
            FROM tasks
            WHERE user_id = $1
            ORDER BY created_at DESC
            """
        else:
            query = """
            SELECT id, task_text, status, created_at, completed_at
            FROM tasks
            WHERE user_id = $1 AND status = FALSE
            ORDER BY created_at DESC
            """

        # Получение задач
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, user_id)
            return [dict(row) for row in rows]

    async def complete_task(self, task_id: int, user_id: int) -> bool:
        """Отметить задачу как выполненную"""
        query = """
        UPDATE tasks
        SET status = TRUE, completed_at = CURRENT_TIMESTAMP
        WHERE id = $1 AND user_id = $2 AND status = FALSE
        """

        # Отмечаем задачу как выполненную
        async with self.pool.acquire() as connection:
            result = await connection.execute(query, task_id, user_id)
            # Проверяем количество затронутых строк
            success = result.split()[-1] == '1'
            if success:
                logger.info(
                    (
                        f"Задача {task_id} отмечена как выполненная "
                        f"пользователем {user_id}"
                    )
                )
            return success

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удаление задачи"""
        query = "DELETE FROM tasks WHERE id = $1 AND user_id = $2"

        # Удаляем задачу
        async with self.pool.acquire() as connection:
            result = await connection.execute(query, task_id, user_id)
            success = result.split()[-1] == '1'
            if success:
                logger.info(
                    f"Задача {task_id} удалена пользователем {user_id}"
                )
            return success

    async def get_task_by_id(
            self,
            task_id: int,
            user_id: int
    ) -> Optional[Dict]:
        """Получение задачи по ID"""
        query = """
        SELECT id, task_text, status, created_at, completed_at
        FROM tasks
        WHERE id = $1 AND user_id = $2
        """

        # Получение задачи
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, task_id, user_id)
            return dict(row) if row else None


# Глобальный экземпляр базы данных
db = Database()

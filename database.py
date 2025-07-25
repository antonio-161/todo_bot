import asyncpg
import logging
from typing import List, Dict, Optional

from config import DB_CONFIG

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
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP WITH TIME ZONE NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            timezone VARCHAR(50) DEFAULT 'UTC',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
        CREATE INDEX IF NOT EXISTS idx_tasks_completed_at
        ON tasks(completed_at);
        CREATE INDEX IF NOT EXISTS idx_users_timezone
        ON users(timezone);
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query)
        logger.info("Таблицы созданы")

    async def add_task(self, user_id: int, task_text: str) -> int:
        """Добавление новой задачи"""
        # Валидация входных данных
        if not task_text or not task_text.strip():
            raise ValueError("Текст задачи не может быть пустым")

        if len(task_text) > 1000:
            raise ValueError("Текст задачи слишком длинный")

        query = """
        INSERT INTO tasks (user_id, task_text)
        VALUES ($1, $2)
        RETURNING id
        """

        async with self.pool.acquire() as connection:
            task_id = await connection.fetchval(
                query,
                user_id,
                task_text.strip()
            )
            logger.info(
                f"Добавлена задача {task_id} для пользователя {user_id}"
            )
            return task_id

    async def get_user_tasks(
            self,
            user_id: int,
            include_completed: bool = False,
            limit: int = 50,
            offset: int = 0
    ) -> List[Dict]:
        """Получение задач пользователя с пагинацией"""
        if include_completed:
            query = """
            SELECT id, task_text, status, created_at, completed_at
            FROM tasks
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """
        else:
            query = """
            SELECT id, task_text, status, created_at, completed_at
            FROM tasks
            WHERE user_id = $1 AND status = FALSE
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """

        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, user_id, limit, offset)
            return [dict(row) for row in rows]

    async def complete_task(self, task_id: int, user_id: int) -> bool:
        """Отметить задачу как выполненную"""
        query = """
        UPDATE tasks
        SET status = TRUE, completed_at = CURRENT_TIMESTAMP
        WHERE id = $1 AND user_id = $2 AND status = FALSE
        RETURNING id
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchval(query, task_id, user_id)
            success = result is not None
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
        query = "DELETE FROM tasks WHERE id = $1 AND user_id = $2 RETURNING id"

        async with self.pool.acquire() as connection:
            result = await connection.fetchval(query, task_id, user_id)
            success = result is not None
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

        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, task_id, user_id)
            return dict(row) if row else None

    async def update_task(
            self,
            task_id: int,
            user_id: int,
            new_text: str
    ) -> bool:
        """Обновление текста задачи"""
        # Валидация входных данных
        if not new_text or not new_text.strip():
            raise ValueError("Текст задачи не может быть пустым")

        if len(new_text) > 1000:
            raise ValueError("Текст задачи слишком длинный")

        query = """
        UPDATE tasks
        SET task_text = $3
        WHERE id = $1 AND user_id = $2 AND status = FALSE
        RETURNING id
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchval(
                query,
                task_id,
                user_id,
                new_text.strip()
            )
            success = result is not None
            if success:
                logger.info(
                    f"Текст задачи {task_id} обновлен пользователем {user_id}"
                )
            return success

    async def get_user_tasks_count(
            self,
            user_id: int,
            include_completed: bool = False
    ) -> int:
        """Получение количества задач пользователя"""
        if include_completed:
            query = "SELECT COUNT(*) FROM tasks WHERE user_id = $1"
        else:
            query = """
            SELECT COUNT(*) FROM tasks
            WHERE user_id = $1 AND status = FALSE
            """

        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, user_id)

    async def set_user_timezone(self, user_id: int, timezone: str) -> bool:
        """Установка часового пояса пользователя"""
        query = """
        INSERT INTO users (user_id, timezone, updated_at)
        VALUES ($1, $2, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id)
        DO UPDATE SET
            timezone = EXCLUDED.timezone,
            updated_at = CURRENT_TIMESTAMP
        """

        async with self.pool.acquire() as connection:
            try:
                await connection.execute(query, user_id, timezone)
                logger.info(
                    f"Часовой пояс {timezone} установлен "
                    f"для пользователя {user_id}"
                )
                return True
            except Exception as e:
                logger.error(
                    "Ошибка установки часового пояса "
                    f"для пользователя {user_id}: {e}"
                )
                return False

    async def get_user_timezone(self, user_id: int) -> str:
        """Получение часового пояса пользователя"""
        query = "SELECT timezone FROM users WHERE user_id = $1"

        async with self.pool.acquire() as connection:
            timezone = await connection.fetchval(query, user_id)
            return timezone if timezone else 'UTC'


# Глобальный экземпляр базы данных
db = Database()

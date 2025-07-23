import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import db

# Импортируем все роутеры
from handlers import start, help, new_task, tasks_list, actions

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


async def main():
    """Основная функция запуска бота"""

    # Инициализация бота с настройками по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Создаем диспетчер с хранилищем состояний в памяти
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры
    dp.include_routers(
        start.router,
        help.router,
        new_task.router,
        tasks_list.router,
        actions.router
    )

    try:
        # Инициализируем подключение к базе данных
        await db.create_pool()
        logger.info("Установлено подключение к базе данных")

        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username}")

        # Запускаем поллинг
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        # Закрываем подключение к БД при завершении
        await db.close_pool()
        await bot.session.close()
        logger.info("Подключение к базе данных закрыто")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

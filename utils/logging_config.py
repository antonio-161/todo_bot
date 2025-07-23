import logging
import sys
from pathlib import Path


def setup_logging():
    """Настройка централизованного логирования"""
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Настройка обработчиков
    handlers = [
        logging.StreamHandler(sys.stdout)
    ]

    # Добавляем файловый обработчик,
    # только если не в продакшене без файловой системы
    try:
        file_handler = logging.FileHandler(
            log_dir / 'bot.log', encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except (PermissionError, OSError):
        # В некоторых платформах развертывания файловые логи недоступны
        pass

    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Уменьшаем многословность некоторых библиотек
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('asyncpg').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Получение логгера с единообразной настройкой"""
    return logging.getLogger(name)

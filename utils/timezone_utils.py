from datetime import datetime
from typing import Dict, List
import pytz
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Популярные часовые пояса для выбора
POPULAR_TIMEZONES = {
    'UTC': 'UTC (Всемирное время)',
    'Europe/Moscow': 'Москва (UTC+3)',
    'Europe/Kiev': 'Киев (UTC+2/UTC+3)',
    'Europe/Minsk': 'Минск (UTC+3)',
    'Asia/Almaty': 'Алматы (UTC+6)',
    'Asia/Tashkent': 'Ташкент (UTC+5)',
    'Asia/Yekaterinburg': 'Екатеринбург (UTC+5)',
    'Asia/Novosibirsk': 'Новосибирск (UTC+7)',
    'Asia/Krasnoyarsk': 'Красноярск (UTC+7)',
    'Asia/Irkutsk': 'Иркутск (UTC+8)',
    'Asia/Vladivostok': 'Владивосток (UTC+10)',
    'Europe/London': 'Лондон (UTC+0/UTC+1)',
    'Europe/Berlin': 'Берлин (UTC+1/UTC+2)',
    'Europe/Paris': 'Париж (UTC+1/UTC+2)',
    'America/New_York': 'Нью-Йорк (UTC-5/UTC-4)',
    'America/Los_Angeles': 'Лос-Анджелес (UTC-8/UTC-7)',
    'Asia/Tokyo': 'Токио (UTC+9)',
    'Asia/Shanghai': 'Шанхай (UTC+8)',
    'Australia/Sydney': 'Сидней (UTC+10/UTC+11)'
}


def get_timezone_keyboard_data() -> List[Dict[str, str]]:
    """Получение данных для клавиатуры выбора часовых поясов"""
    return [
        {'name': name, 'tz': tz}
        for tz, name in POPULAR_TIMEZONES.items()
    ]


def format_datetime_for_user(dt: datetime, user_timezone: str = 'UTC') -> str:
    """
    Форматирование datetime в часовой пояс пользователя

    Args:
        dt: datetime объект (должен быть aware с UTC timezone)
        user_timezone: строка часового пояса пользователя

    Returns:
        Отформатированная строка даты и времени
    """
    try:
        # Если datetime naive, считаем его UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        elif dt.tzinfo != pytz.UTC:
            # Конвертируем в UTC если не UTC
            dt = dt.astimezone(pytz.UTC)

        # Конвертируем в часовой пояс пользователя
        user_tz = pytz.timezone(user_timezone)
        local_dt = dt.astimezone(user_tz)

        return local_dt.strftime("%d.%m.%Y в %H:%M")

    except Exception as e:
        logger.error(f"Ошибка форматирования времени: {e}")
        # Возвращаем исходное время в случае ошибки
        return dt.strftime("%d.%m.%Y в %H:%M")


def validate_timezone(timezone_str: str) -> bool:
    """
    Валидация строки часового пояса

    Args:
        timezone_str: строка часового пояса

    Returns:
        True если часовой пояс валиден, False иначе
    """
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.UnknownTimeZoneError:
        return False


def get_user_current_time(user_timezone: str = 'UTC') -> str:
    """
    Получение текущего времени в часовом поясе пользователя

    Args:
        user_timezone: строка часового пояса пользователя

    Returns:
        Отформатированная строка текущего времени
    """
    try:
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)
        return now.strftime("%d.%m.%Y в %H:%M")
    except Exception as e:
        logger.error(f"Ошибка получения текущего времени: {e}")
        return datetime.now().strftime("%d.%m.%Y в %H:%M")


def get_timezone_info(timezone_str: str) -> str:
    """
    Получение информации о часовом поясе

    Args:
        timezone_str: строка часового пояса

    Returns:
        Человекочитаемое название часового пояса
    """
    return POPULAR_TIMEZONES.get(timezone_str, timezone_str)

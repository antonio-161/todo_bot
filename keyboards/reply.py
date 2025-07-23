from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура с быстрым доступом к командам"""
    buttons = [
        [
            KeyboardButton(text="📝 Добавить задачу"),
            KeyboardButton(text="📋 Мои задачи")
        ],
        [
            KeyboardButton(text="❓ Помощь")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отмены действия"""
    buttons = [
        [KeyboardButton(text="❌ Отмена")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

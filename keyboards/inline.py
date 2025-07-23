from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_task_keyboard(
    task_id: int,
    is_completed: bool = False
) -> InlineKeyboardMarkup:
    """Создание inline-клавиатуры для отдельной задачи"""
    buttons = []
    # Добавляем кнопку "Выполнено"
    if not is_completed:
        buttons.append([
            InlineKeyboardButton(
                text="✅ Выполнено",
                callback_data=f"complete_task:{task_id}"
            )
        ])
    # Добавляем кнопку "Удалить"
    buttons.append([
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"delete_task:{task_id}"
        )
    ])
    # Добавляем кнопку "Назад"
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="my_tasks"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasks_list_keyboard(tasks: List[Dict]) -> InlineKeyboardMarkup:
    """Создание клавиатуры для списка задач"""
    buttons = []

    # Добавляем кнопки для каждой задачи
    for task in tasks:
        task_id = task['id']
        status_emoji = "✅" if task['status'] else "⏳"

        # Обрезаем текст задачи для кнопки если он слишком длинный
        task_text = task['task_text']
        if len(task_text) > 30:
            task_text = task_text[:27] + "..."

        # Формируем текст кнопки
        button_text = f"{status_emoji} {task_text}"

        # Добавляем кнопку
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"show_task:{task_id}"
            )
        ])

    # Добавляем кнопки управления
    control_buttons = [
        InlineKeyboardButton(text="📝 Новая задача", callback_data="new_task"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks")
    ]
    buttons.append(control_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(
    task_id: int,
    is_completed: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра задачи"""
    buttons = []

    # Добавляем кнопку "Отметить выполненной"
    if not is_completed:
        buttons.append([
            InlineKeyboardButton(
                text="✅ Отметить выполненной",
                callback_data=f"complete_task:{task_id}"
            )
        ])

    # Добавляем кнопку "Удалить задачу" и кнопку "Назад к списку"
    buttons.extend([
        [
            InlineKeyboardButton(
                text="🗑 Удалить задачу",
                callback_data=f"delete_task:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад к списку",
                callback_data="my_tasks"
            )
        ]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(
        task_id: int,
        action: str
) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действий"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data=f"confirm_{action}:{task_id}"
            ),
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"show_task:{task_id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

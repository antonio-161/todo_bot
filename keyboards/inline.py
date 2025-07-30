from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.timezone_utils import get_timezone_keyboard_data


def get_tasks_list_keyboard(
    tasks: List[Dict],
    show_completed: bool = False,
    completed_count: int = 0
) -> InlineKeyboardMarkup:
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

    # Кнопка переключения режима просмотра
    if show_completed:
        # Если показываем выполненные, добавляем кнопку скрытия
        toggle_button = InlineKeyboardButton(
            text="👁‍🗨 Скрыть выполненные",
            callback_data="hide_completed"
        )
    else:
        # Если скрываем выполненные, показываем кнопку с количеством
        if completed_count > 0:
            toggle_button = InlineKeyboardButton(
                text=f"👁 Показать выполненные ({completed_count})",
                callback_data="show_completed"
            )
        else:
            toggle_button = None

    # Добавляем кнопки управления
    control_buttons = [
        InlineKeyboardButton(text="📝 Новая задача", callback_data="new_task"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks")
    ]

    if toggle_button:
        buttons.append([toggle_button])

    buttons.append(control_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(
    task_id: int,
    is_completed: bool = False,
    edit: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура для детального просмотра задачи"""
    buttons = []

    if edit:
        # Режим редактирования - только кнопка отмены
        buttons.append([
            InlineKeyboardButton(
                text="❌ Отменить редактирование",
                callback_data=f"cancel_edit:{task_id}"
            )
        ])
    else:
        # Обычный режим просмотра
        if not is_completed:
            # Кнопки для активных задач
            buttons.extend([
                [
                    InlineKeyboardButton(
                        text="✅ Отметить выполненной",
                        callback_data=f"complete_task:{task_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✏️ Редактировать",
                        callback_data=f"edit_task:{task_id}"
                    )
                ]
            ])
        else:
            # Кнопки для выполненных задач
            buttons.extend([
                [
                    InlineKeyboardButton(
                        text="⏳ Отметить как активную",
                        callback_data=f"reactivate_task:{task_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🫥 Скрыть задачу",
                        callback_data=f"hide_task:{task_id}"
                    )
                ]
            ])

        # Кнопка удаления для всех задач
        buttons.append([
            InlineKeyboardButton(
                text="🗑 Удалить задачу",
                callback_data=f"delete_task:{task_id}"
            )
        ])

    # Кнопка возврата к списку
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад к списку",
            callback_data="my_tasks"
        )
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


def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора часового пояса"""
    timezone_data = get_timezone_keyboard_data()
    buttons = []

    # Добавляем кнопки по 1 в ряд для лучшей читаемости
    for tz_info in timezone_data:
        buttons.append([
            InlineKeyboardButton(
                text=tz_info['name'],
                callback_data=f"set_tz:{tz_info['tz']}"
            )
        ])

    # Добавляем кнопку для ручного ввода
    buttons.append([
        InlineKeyboardButton(
            text="✏️ Ввести вручную",
            callback_data="timezone_manual"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

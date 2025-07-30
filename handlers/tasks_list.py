from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from database import db
from keyboards.inline import get_tasks_list_keyboard, get_task_detail_keyboard
from utils.logging_config import get_logger
from utils.task_formatting import (
    format_tasks_list_text,
    format_task_detail_text
)

logger = get_logger(__name__)
router = Router()


@router.message(Command("my_tasks"))
@router.message(F.text == "📋 Мои задачи")
@router.callback_query(F.data == "my_tasks")
@router.callback_query(F.data == "refresh_tasks")
@router.callback_query(F.data == "hide_completed")
async def show_tasks_list(update, show_completed: bool = False):
    """Показать список задач пользователя"""

    # Определяем тип события
    if isinstance(update, CallbackQuery):
        message = update.message
        user_id = update.from_user.id
        await update.answer()
        edit_message = True
    else:
        message = update
        user_id = update.from_user.id
        edit_message = False

    try:
        # Получаем задачи в зависимости от режима
        tasks = await db.get_user_tasks(
            user_id,
            include_completed=show_completed
        )

        # Получаем количество выполненных задач для кнопки
        completed_count = await db.get_completed_tasks_count(user_id)

        # Получаем часовой пояс пользователя
        user_timezone = await db.get_user_timezone(user_id)

        # Форматируем текст списка задач с учетом режима просмотра
        tasks_text = format_tasks_list_text(
            tasks, user_timezone, show_completed
        )

        # Создаем клавиатуру с учетом режима и количества выполненных
        keyboard = get_tasks_list_keyboard(
            tasks, show_completed, completed_count
        )

        # Обновляем сообщение
        if edit_message:
            await message.edit_text(
                tasks_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                tasks_text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

    except Exception as e:
        error_text = "❌ Произошла ошибка при загрузке задач. Попробуй еще раз."
        logger.error(f"Error loading tasks for user {user_id}: {e}")

        if edit_message:
            await message.edit_text(error_text)
        else:
            await message.answer(error_text)


@router.callback_query(F.data == "show_completed")
async def show_completed_tasks(callback: CallbackQuery):
    """Показать список с выполненными задачами"""
    await show_tasks_list(callback, show_completed=True)


@router.callback_query(F.data.startswith("show_task:"))
async def show_task_detail(callback: CallbackQuery):
    """Показать детали конкретной задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        # Получаем задачу из БД
        task = await db.get_task_by_id(task_id, user_id)

        if not task:
            await callback.message.edit_text(
                "❌ Задача не найдена или была удалена.",
                reply_markup=get_tasks_list_keyboard([])
            )
            return

        # Получаем часовой пояс пользователя
        user_timezone = await db.get_user_timezone(user_id)

        # Используем общую функцию форматирования с часовым поясом
        task_detail_text = await format_task_detail_text(task, user_timezone)

        # Обновляем сообщение
        await callback.message.edit_text(
            task_detail_text,
            parse_mode="HTML",
            reply_markup=get_task_detail_keyboard(task_id, task['status'])
        )

    except Exception as e:
        logger.error(f"Error loading task {task_id} for user {user_id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке задачи."
        )

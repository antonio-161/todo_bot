from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import (
    get_confirmation_keyboard,
    get_task_detail_keyboard,
    get_tasks_list_keyboard
)
from handlers.tasks_list import show_tasks_list
from states import TaskStates
from utils.logging_config import get_logger
from utils.task_formatting import format_task_detail_text

logger = get_logger(__name__)

router = Router()


async def update_tasks_list_message(
        callback: CallbackQuery,
        show_completed: bool = False
):
    """Обновление сообщения со списком задач"""
    user_id = callback.from_user.id
    tasks = await db.get_user_tasks(user_id, include_completed=show_completed)
    completed_count = await db.get_completed_tasks_count(user_id)

    # Получаем часовой пояс пользователя
    user_timezone = await db.get_user_timezone(user_id)

    if not tasks:
        if show_completed:
            no_tasks_text = """📋 <b>Список задач</b>

У тебя пока нет задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""
        else:
            no_tasks_text = """📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""

        await callback.message.edit_text(
            no_tasks_text,
            parse_mode="HTML",
            reply_markup=get_tasks_list_keyboard(
                [], show_completed, completed_count
            )
        )
        return

    from utils.task_formatting import format_tasks_list_text
    tasks_text = format_tasks_list_text(tasks, user_timezone, show_completed)

    await callback.message.edit_text(
        tasks_text,
        parse_mode="HTML",
        reply_markup=get_tasks_list_keyboard(
            tasks, show_completed, completed_count
        )
    )


@router.callback_query(F.data.startswith("edit_task:"))
async def edit_task_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия кнопки редактирования задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        task = await db.get_task_by_id(task_id, user_id)

        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return

        if task['status']:
            await callback.answer(
                "❌ Невозможно редактировать выполненную задачу",
                show_alert=True
            )
            return

        # Сохраняем ID задачи в состоянии
        await state.update_data(editing_task_id=task_id)
        await state.set_state(TaskStates.waiting_for_task_edit)

        task_text = task['task_text']
        if len(task_text) > 100:
            task_text = task_text[:97] + "..."

        edit_text = f"""📝 <b>Редактирование задачи</b>

<b>Текущий текст задачи:</b>
<i>{task_text}</i>

<i>Введите новый текст задачи:</i>"""

        await callback.message.edit_text(
            edit_text,
            parse_mode="HTML",
            reply_markup=get_task_detail_keyboard(task_id, edit=True)
        )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Ошибка редактирования задачи {task_id} "
            f"пользователя {user_id}: {e}"
        )


@router.callback_query(F.data.startswith("complete_task:"))
async def complete_task_callback(callback: CallbackQuery):
    """Отметить задачу как выполненную"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        success = await db.complete_task(task_id, user_id)

        if success:
            await callback.answer(
                "✅ Задача отмечена как выполненная! "
                "Теперь она видна в разделе выполненных задач.",
                show_alert=True
            )

            # Получаем часовой пояс пользователя
            user_timezone = await db.get_user_timezone(user_id)

            # Обновляем сообщение с деталями задачи
            task = await db.get_task_by_id(task_id, user_id)
            if task:
                updated_text = await format_task_detail_text(
                    task, user_timezone
                )
                await callback.message.edit_text(
                    updated_text,
                    parse_mode="HTML",
                    reply_markup=get_task_detail_keyboard(
                        task_id, task['status']
                    )
                )
        else:
            await callback.answer(
                "❌ Не удалось отметить задачу как выполненную",
                show_alert=True
            )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Ошибка отметки выполненной задачи {task_id} "
            f"пользователя {user_id}: {e}"
        )


@router.callback_query(F.data.startswith("delete_task:"))
async def delete_task_callback(callback: CallbackQuery):
    """Запрос подтверждения удаления задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        task = await db.get_task_by_id(task_id, user_id)

        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return

        task_text = task['task_text']
        if len(task_text) > 100:
            task_text = task_text[:97] + "..."

        confirmation_text = f"""🗑 <b>Удаление задачи</b>

<b>Ты действительно хочешь удалить эту задачу?</b>

<i>{task_text}</i>

⚠️ <b>Это действие нельзя отменить!</b>"""

        await callback.message.edit_text(
            confirmation_text,
            parse_mode="HTML",
            reply_markup=get_confirmation_keyboard(task_id, "delete")
        )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            (
                "Ошибка при подготовке подтверждения удаления задачи "
                f"{task_id}: {e}"
            )
        )


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_task(callback: CallbackQuery):
    """Подтверждение удаления задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        success = await db.delete_task(task_id, user_id)

        if success:
            await callback.answer("🗑 Задача удалена!", show_alert=True)
            # Возвращаемся к списку задач
            # (с показом выполненных если была выполненная)
            await show_tasks_list(callback, show_completed=True)
        else:
            await callback.answer(
                "❌ Не удалось удалить задачу", show_alert=True
            )

    except Exception as e:
        await callback.answer(
            "❌ Произошла ошибка при удалении", show_alert=True
        )
        logger.error(f"Error deleting task {task_id} for user {user_id}: {e}")


@router.callback_query(F.data.startswith("cancel_edit:"))
async def cancel_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена редактирования задачи"""
    await callback.answer()
    await state.clear()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        task = await db.get_task_by_id(task_id, user_id)
        if task:
            # Получаем часовой пояс пользователя
            user_timezone = await db.get_user_timezone(user_id)
            task_detail_text = await format_task_detail_text(
                task, user_timezone
            )
            await callback.message.edit_text(
                task_detail_text,
                parse_mode="HTML",
                reply_markup=get_task_detail_keyboard(task_id, task['status'])
            )
    except Exception as e:
        logger.error(f"Error canceling edit for task {task_id}: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("reactivate_task:"))
async def reactivate_task_callback(callback: CallbackQuery):
    """Реактивация задачи (отмена выполнения)"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        success = await db.reactivate_task(task_id, user_id)

        if success:
            await callback.answer(
                "⏳ Задача снова активна!", show_alert=True
            )

            # Получаем часовой пояс пользователя
            user_timezone = await db.get_user_timezone(user_id)

            # Обновляем сообщение с деталями задачи
            task = await db.get_task_by_id(task_id, user_id)
            if task:
                updated_text = await format_task_detail_text(
                    task, user_timezone
                )
                await callback.message.edit_text(
                    updated_text,
                    parse_mode="HTML",
                    reply_markup=get_task_detail_keyboard(
                        task_id, task['status']
                    )
                )
        else:
            await callback.answer(
                "❌ Не удалось реактивировать задачу",
                show_alert=True
            )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Ошибка реактивации задачи {task_id} "
            f"пользователя {user_id}: {e}"
        )


@router.callback_query(F.data.startswith("hide_task:"))
async def hide_task_callback(callback: CallbackQuery):
    """Запрос подтверждения скрытия задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        task = await db.get_task_by_id(task_id, user_id)

        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return

        if not task['status']:
            await callback.answer(
                "❌ Можно скрыть только выполненную задачу",
                show_alert=True
            )
            return

        task_text = task['task_text']
        if len(task_text) > 100:
            task_text = task_text[:97] + "..."

        confirmation_text = f"""🫥 <b>Скрытие задачи</b>

<b>Ты действительно хочешь скрыть эту выполненную задачу?</b>

<i>{task_text}</i>

ℹ️ <b>Скрытые задачи не отображаются в списке, но остаются в базе данных</b>"""

        await callback.message.edit_text(
            confirmation_text,
            parse_mode="HTML",
            reply_markup=get_confirmation_keyboard(task_id, "hide")
        )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Ошибка при подготовке скрытия задачи {task_id}: {e}"
        )


@router.callback_query(F.data.startswith("confirm_hide:"))
async def confirm_hide_task(callback: CallbackQuery):
    """Подтверждение скрытия задачи"""
    await callback.answer()

    try:
        task_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        success = await db.hide_task(task_id, user_id)

        if success:
            await callback.answer("🫥 Задача скрыта!", show_alert=True)
            # Возвращаемся к списку задач
            await show_tasks_list(callback, show_completed=True)
        else:
            await callback.answer(
                "❌ Не удалось скрыть задачу", show_alert=True
            )

    except Exception as e:
        await callback.answer(
            "❌ Произошла ошибка при скрытии", show_alert=True
        )
        logger.error(f"Ошибка скрытия задачи {task_id} "
                     f"для пользователя {user_id}: {e}")

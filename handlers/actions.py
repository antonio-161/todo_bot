from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import (
    get_confirmation_keyboard,
    get_task_detail_keyboard,
    get_tasks_list_keyboard
)
from states import TaskStates
from utils.logging_config import get_logger

logger = get_logger(__name__)

router = Router()


async def format_task_detail_text(task: dict) -> str:
    """Форматирование текста с деталями задачи"""
    created_date = task['created_at'].strftime("%d.%m.%Y в %H:%M")
    status_text = "✅ Выполнена" if task['status'] else "⏳ Активна"

    text = f"""📝 <b>Детали задачи</b>

<b>Текст:</b>
<i>{task['task_text']}</i>

<b>Статус:</b> {status_text}
<b>Создана:</b> {created_date}"""

    if task['status'] and task['completed_at']:
        completed_date = task['completed_at'].strftime("%d.%m.%Y в %H:%M")
        text += f"\n<b>Выполнена:</b> {completed_date}"

    return text


async def update_tasks_list_message(callback: CallbackQuery):
    """Обновление сообщения со списком задач"""
    user_id = callback.from_user.id
    tasks = await db.get_user_tasks(user_id, include_completed=False)

    if not tasks:
        no_tasks_text = """📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""

        await callback.message.edit_text(
            no_tasks_text,
            parse_mode="HTML",
            reply_markup=get_tasks_list_keyboard([])
        )
        return

    tasks_text = f"📋 <b>Твои задачи ({len(tasks)})</b>\n\n"

    for i, task in enumerate(tasks, 1):
        created_date = task['created_at'].strftime("%d.%m.%Y")
        status_emoji = "✅" if task['status'] else "⏳"

        task_text = task['task_text']
        if len(task_text) > 60:
            task_text = task_text[:57] + "..."

        tasks_text += f"{i}. {status_emoji} <i>{task_text}</i>\n"
        tasks_text += f"   📅 {created_date}\n\n"

    tasks_text += "👆 <i>Нажми на задачу для подробного просмотра</i>"

    await callback.message.edit_text(
        tasks_text,
        parse_mode="HTML",
        reply_markup=get_tasks_list_keyboard(tasks)
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
                "✅ Задача отмечена как выполненная!", show_alert=True
            )

            # Обновляем сообщение с деталями задачи
            task = await db.get_task_by_id(task_id, user_id)
            if task:
                updated_text = await format_task_detail_text(task)
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
            f"пользователя {user_id}: {e}")


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
            await update_tasks_list_message(callback)
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
            task_detail_text = await format_task_detail_text(task)
            await callback.message.edit_text(
                task_detail_text,
                parse_mode="HTML",
                reply_markup=get_task_detail_keyboard(task_id, task['status'])
            )
    except Exception as e:
        logger.error(f"Error canceling edit for task {task_id}: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

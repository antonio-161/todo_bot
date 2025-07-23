import logging
import sys
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import db
from keyboards.inline import (
    get_confirmation_keyboard,
    get_task_detail_keyboard,
    get_tasks_list_keyboard
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("edit_task:"))
async def edit_task_callback(callback: CallbackQuery):
    """Обработчик нажатия кнопки редактирования задачи"""
    await callback.answer()

    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        # Получаем задачу для редактирования
        task = await db.get_task_by_id(task_id, user_id)
        # Если задача не найдена, показываем ошибку
        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return
        # Если задача уже выполнена, показываем ошибку
        if task['status']:
            await callback.answer(
                "❌ Невозможно редактировать выполненную задачу",
                show_alert=True
            )
            return
        # Обрезаем текст задачи для кнопки
        task_text = task['task_text']
        if len(task_text) > 100:
            task_text = task_text[:97] + "..."
        # Отправляем сообщение с текущим текстом задачи для редактирования
        edit_text = "📝 <b>Редактирование задачи</b>"
        edit_text += f"\n\n<b>Текущий текст задачи:</b>\n<i>{task_text}</i>"
        edit_text += "\n\n<i>Введите новый текст задачи:</i>"
        await callback.message.edit_text(
            edit_text,
            parse_mode="HTML",
            reply_markup=get_task_detail_keyboard(task_id, edit=True)
        )
    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(f"Error editing task {task_id} for user {user_id}: {e}")


@router.callback_query(F.data.startswith("update_task:"))
async def update_task_callback(callback: CallbackQuery):
    """Обработчик обновления задачи после редактирования"""
    await callback.answer()

    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    # Получаем новый текст задачи из сообщения
    new_task_text = callback.message.text.split("\n\n", 1)[-1].strip()

    try:
        # Обновляем задачу в базе данных
        success = await db.update_task(task_id, user_id, new_task_text)
        # Если обновление успешно, отправляем уведомление
        if success:
            await callback.answer("✅ Задача обновлена!", show_alert=True)
            # Если задача была успешно обновлена,
            # удаляем клавиатуру редактирования
            await callback.message.edit_reply_markup()
            # Обновляем сообщение с деталями задачи
            task = await db.get_task_by_id(task_id, user_id)
            if task:
                created_date = task['created_at'].strftime("%d.%m.%Y в %H:%M")
                # Формируем текст с деталями задачи
                updated_text = f"""
                                📝 <b>Детали задачи</b>
                                <b>Текст:</b>
                                <i>{task['task_text']}</i>
                                <b>Статус:</b> ⏳ Активна
                                <b>Создана:</b> {created_date}
                                """
                await callback.message.edit_text(
                    updated_text,
                    parse_mode="HTML",
                    reply_markup=get_task_detail_keyboard(task_id, True)
                )
        else:
            await callback.answer(
                "❌ Не удалось обновить задачу", show_alert=True
            )
    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(f"Error updating task {task_id} for user {user_id}: {e}")


@router.callback_query(F.data.startswith("complete_task:"))
async def complete_task_callback(callback: CallbackQuery):
    """Отметить задачу как выполненную"""
    await callback.answer()

    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        # Отмечаем задачу как выполненную
        success = await db.complete_task(task_id, user_id)
        # Если успешно, отправляем уведомление
        if success:
            await callback.answer(
                "✅ Задача отмечена как выполненная!",
                show_alert=True
            )
            # Удаляем клавиатуру редактирования
            await callback.message.edit_reply_markup()
            # Получаем текущую дату и время выполнения
            completed_at = datetime.now()
            # Обновляем статус задачи в базе данных
            await db.update_task_status(task_id, user_id, completed_at)
            # Обновляем сообщение с деталями задачи
            task = await db.get_task_by_id(task_id, user_id)
            if task:
                completed_at = task['completed_at']
                completed_date = completed_at.strftime("%d.%m.%Y в %H:%M")
                created_date = task['created_at'].strftime("%d.%m.%Y в %H:%M")
                updated_text = f"""
📝 <b>Детали задачи</b>
<b>Текст:</b>
<i>{task['task_text']}</i>
<b>Статус:</b> ✅ Выполнена
<b>Создана:</b> {created_date}
<b>Выполнена:</b> {completed_date}
"""
                await callback.message.edit_text(
                    updated_text,
                    parse_mode="HTML",
                    reply_markup=get_task_detail_keyboard(task_id, True)
                )
        else:
            await callback.answer(
                "❌ Не удалось отметить задачу как выполненную", show_alert=True
            )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Error completing task {task_id} for user {user_id}: {e}"
        )


@router.callback_query(F.data.startswith("delete_task:"))
async def delete_task_callback(callback: CallbackQuery):
    """Запрос подтверждения удаления задачи"""
    await callback.answer()

    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        # Получаем задачу для показа в подтверждении
        task = await db.get_task_by_id(task_id, user_id)
        # Если задача не найдена, показываем ошибку
        if not task:
            await callback.answer("❌ Задача не найдена", show_alert=True)
            return
        # Если задача уже выполнена, показываем ошибку
        if task['status']:
            await callback.answer(
                "❌ Невозможно удалить выполненную задачу",
                show_alert=True
            )
            return
        # Обрезаем текст задачи для подтверждения
        task_text = task['task_text']
        if len(task_text) > 100:
            task_text = task_text[:97] + "..."
        # Формируем текст подтверждения удаления
        confirmation_text = f"""
🗑 <b>Удаление задачи</b>

<b>Ты действительно хочешь удалить эту задачу?</b>

<i>{task_text}</i>

⚠️ <b>Это действие нельзя отменить!</b>
"""

        await callback.message.edit_text(
            confirmation_text,
            parse_mode="HTML",
            reply_markup=get_confirmation_keyboard(task_id, "delete")
        )

    except Exception as e:
        await callback.answer("❌ Произошла ошибка", show_alert=True)
        logger.error(
            f"Error preparing delete confirmation for task {task_id}: {e}"
        )


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_task(callback: CallbackQuery):
    """Подтвержение удаления задачи"""
    await callback.answer()

    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        # Удаляем задачу
        success = await db.delete_task(task_id, user_id)
        # Если удаление успешно, отправляем уведомление
        if success:
            await callback.answer("🗑 Задача удалена!", show_alert=True)
            # Удаляем клавиатуру редактирования
            await callback.message.edit_reply_markup()
            # Удаляем сообщение с деталями задачи
            await callback.message.delete()
            # Показываем обновленный список задач
            tasks = await db.get_user_tasks(user_id, include_completed=False)
            # Если задач нет, показываем сообщение об отсутствии задач
            if not tasks:
                no_tasks_text = """
📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task
"""
                await callback.message.edit_text(
                    no_tasks_text,
                    parse_mode="HTML",
                    reply_markup=get_tasks_list_keyboard([])
                )
            else:
                tasks_text = f"📋 <b>Твои задачи ({len(tasks)})</b>\n\n"

                for i, task in enumerate(tasks, 1):
                    created_date = task['created_at'].strftime("%d.%m.%Y")
                    status_emoji = "✅" if task['status'] else "⏳"

                    task_text = task['task_text']
                    if len(task_text) > 60:
                        task_text = task_text[:57] + "..."
                    # Формируем текст задачи
                    tasks_text += f"{i}. {status_emoji} <i>{task_text}</i>\n"
                    tasks_text += f"   📅 {created_date}\n\n"
                # Добавляем подсказку для пользователя
                tasks_text += """
                            👆 <i>Нажми на задачу для подробного просмотра</i>
                            """
                # Обновляем клавиатуру со списком задач
                await callback.message.edit_text(
                    tasks_text,
                    parse_mode="HTML",
                    reply_markup=get_tasks_list_keyboard(tasks)
                )
        else:
            await callback.answer(
                "❌ Не удалось удалить задачу", show_alert=True
            )

    except Exception as e:
        await callback.answer(
            "❌ Произошла ошибка при удалении", show_alert=True
        )
        logger.error(f"Error deleting task {task_id} for user {user_id}: {e}")

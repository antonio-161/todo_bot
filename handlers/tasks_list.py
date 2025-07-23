import logging
import sys

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from database import db
from keyboards.inline import get_tasks_list_keyboard, get_task_detail_keyboard

router = Router()

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


@router.message(Command("my_tasks"))
@router.message(F.text == "📋 Мои задачи")
@router.callback_query(F.data == "my_tasks")
@router.callback_query(F.data == "refresh_tasks")
async def show_tasks_list(update):
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
        # Получаем активные задачи пользователя
        tasks = await db.get_user_tasks(user_id, include_completed=False)
        # Если задач нет, показываем сообщение об отсутствии задач
        if not tasks:
            no_tasks_text = """
📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task
"""
            # Обновляем сообщение
            if edit_message:
                await message.edit_text(
                    no_tasks_text,
                    parse_mode="HTML",
                    reply_markup=get_tasks_list_keyboard([])
                )
            else:
                await message.answer(
                    no_tasks_text,
                    parse_mode="HTML",
                    reply_markup=get_tasks_list_keyboard([])
                )
            return

        # Формируем текст со списком задач
        tasks_text = f"📋 <b>Твои задачи ({len(tasks)})</b>\n\n"
        # Добавляем каждую задачу в текст
        for i, task in enumerate(tasks, 1):
            created_date = task['created_at'].strftime("%d.%m.%Y")
            status_emoji = "✅" if task['status'] else "⏳"

            # Обрезаем длинные задачи в списке
            task_text = task['task_text']
            if len(task_text) > 60:
                task_text = task_text[:57] + "..."
            # Добавляем задачу в текст
            tasks_text += f"{i}. {status_emoji} <i>{task_text}</i>\n"
            # Добавляем дату создания
            tasks_text += f"   📅 {created_date}\n\n"

        tasks_text += "👆 <i>Нажми на задачу для подробного просмотра</i>"
        # Обновляем сообщение
        if edit_message:
            await message.edit_text(
                tasks_text,
                parse_mode="HTML",
                reply_markup=get_tasks_list_keyboard(tasks)
            )
        else:
            await message.answer(
                tasks_text,
                parse_mode="HTML",
                reply_markup=get_tasks_list_keyboard(tasks)
            )

    except Exception as e:
        error_text = "❌ Произошла ошибка при загрузке задач. Попробуй еще раз."

        if edit_message:
            await message.edit_text(error_text)
        else:
            await message.answer(error_text)

        logger.error(f"Error loading tasks for user {user_id}: {e}")


@router.callback_query(F.data.startswith("show_task:"))
async def show_task_detail(callback: CallbackQuery):
    """Показать детали конкретной задачи"""
    await callback.answer()

    # Извлекаем ID задачи из callback_data
    task_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        # Получаем задачу из БД
        task = await db.get_task_by_id(task_id, user_id)

        # Если задача не найдена, выходим
        if not task:
            await callback.message.edit_text(
                "❌ Задача не найдена или была удалена.",
                reply_markup=get_tasks_list_keyboard([])
            )
            return

        # Форматируем информацию о задаче
        created_date = task['created_at'].strftime("%d.%m.%Y в %H:%M")
        status_text = "✅ Выполнена" if task['status'] else "⏳ В процессе"

        task_detail_text = f"""
📝 <b>Детали задачи</b>

<b>Текст:</b>
<i>{task['task_text']}</i>

<b>Статус:</b> {status_text}
<b>Создана:</b> {created_date}
"""

        # Добавляем дату выполнения если задача выполнена
        if task['status'] and task['completed_at']:
            completed_date = task['completed_at'].strftime("%d.%m.%Y в %H:%M")
            task_detail_text += f"<b>Выполнена:</b> {completed_date}"
        # Обновляем сообщение
        await callback.message.edit_text(
            task_detail_text,
            parse_mode="HTML",
            reply_markup=get_task_detail_keyboard(task_id, task['status'])
        )

    except Exception as e:
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке задачи."
        )

        logger.error(f"Error loading task {task_id} for user {user_id}: {e}")

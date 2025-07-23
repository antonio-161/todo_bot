import logging
import sys

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import TaskStates
from database import db
from keyboards.reply import get_cancel_keyboard, get_main_keyboard

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


@router.message(Command("new_task"))
@router.message(F.text == "📝 Добавить задачу")
@router.callback_query(F.data == "new_task")
async def new_task_command(update, state: FSMContext):
    """Начало процесса добавления новой задачи"""

    # Определяем тип события (сообщение или callback)
    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update
    # Устанавливаем состояние ожидания новой задачи
    await state.set_state(TaskStates.waiting_for_new_task)

    prompt_text = """
📝 <b>Добавление новой задачи</b>

Напиши текст своей задачи или заметки.

<i>Например:</i>
• Купить молоко
• Позвонить маме
• Подготовить презентацию к пятнице
• Записаться к врачу

Для отмены нажми кнопку "❌ Отмена"
"""

    await message.answer(
        prompt_text,
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(TaskStates.waiting_for_new_task, F.text == "❌ Отмена")
async def cancel_new_task(message: Message, state: FSMContext):
    """Отмена добавления новой задачи"""
    await state.clear()
    await message.answer(
        "❌ Добавление задачи отменено.",
        reply_markup=get_main_keyboard()
    )


@router.message(TaskStates.waiting_for_new_task)
async def save_new_task(message: Message, state: FSMContext):
    """Сохранение новой задачи"""
    # Получаем текст задачи из сообщения
    task_text = message.text.strip()

    # Валидация ввода
    if not task_text:
        await message.answer(
            "❌ Текст задачи не может быть пустым. Попробуй еще раз:"
        )
        return
    # Проверяем длину текста задачи
    if len(task_text) > 1000:
        await message.answer(
            "❌ Текст задачи слишком длинный (максимум 1000 символов). "
            "Попробуй сократить:"
        )
        return

    try:
        # Сохраняем задачу в базу данных
        task_id = await db.add_task(message.from_user.id, task_text)
        # Очищаем состояние после успешного сохранения
        await state.clear()
        # Формируем текст ответа
        success_text = f"""
✅ <b>Задача успешно добавлена!</b>

📝 <i>{task_text}</i>

ID задачи: {task_id}
"""
        # Отправляем ответ пользователю с кнопками
        await message.answer(
            success_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при сохранении задачи. Попробуй еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        # Логируем ошибку
        logger.error(
            f"Error saving task for user {message.from_user.id}: {e}"
        )


@router.message(TaskStates.waiting_for_new_task, ~F.text)
async def invalid_task_input(message: Message):
    """Обработка некорректного ввода при добавлении задачи"""
    await message.answer(
        "❌ Пожалуйста, отправь текст задачи или нажми '❌ Отмена' для выхода."
    )

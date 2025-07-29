from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_keyboard

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Сбрасываем состояние при старте
    await state.clear()
    # Формируем приветственное сообщение
    welcome_text = f"""
🎯 <b>Добро пожаловать в ToDo Bot!</b>

Привет, {message.from_user.first_name}!
Я помогу тебе организовать свои задачи и заметки.

<b>Что я умею:</b>
📝 Добавлять новые задачи
📋 Показывать список задач
✅ Отмечать задачи выполненными
🗑 Удалять задачи

<b>Начни с команды /help для подробной инструкции</b>
или используй кнопки ниже для быстрого доступа!
Для корректного отображения времени выбери часовой пояс в меню.
"""
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    # Сбрасываем состояние, если оно было установлено
    await state.clear()

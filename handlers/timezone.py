from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.inline import get_timezone_keyboard
from keyboards.reply import get_main_keyboard
from states import TimezoneStates
from utils.timezone_utils import (
    validate_timezone,
    get_timezone_info,
    get_user_current_time
)
from utils.logging_config import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("set_timezone"))
@router.message(F.text == "🌍 Часовой пояс")
async def set_timezone_command(message: Message, state: FSMContext):
    """Команда установки часового пояса"""
    await state.clear()

    # Получаем текущий часовой пояс пользователя
    current_timezone = await db.get_user_timezone(message.from_user.id)
    current_time = get_user_current_time(current_timezone)
    timezone_name = get_timezone_info(current_timezone)

    text = f"""🌍 <b>Настройка часового пояса</b>

<b>Текущий часовой пояс:</b> {timezone_name}
<b>Время сейчас:</b> {current_time}

Выбери свой часовой пояс из списка ниже:"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_timezone_keyboard()
    )


@router.callback_query(F.data.startswith("set_tz:"))
async def set_timezone_callback(callback: CallbackQuery):
    """Обработчик выбора часового пояса"""
    await callback.answer()

    try:
        timezone = callback.data.split(":", 1)[1]
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    user_id = callback.from_user.id

    # Валидируем часовой пояс
    if not validate_timezone(timezone):
        await callback.answer("❌ Неверный часовой пояс", show_alert=True)
        return

    try:
        # Сохраняем часовой пояс в БД
        success = await db.set_user_timezone(user_id, timezone)

        if success:
            timezone_name = get_timezone_info(timezone)
            current_time = get_user_current_time(timezone)

            success_text = f"""✅ <b>Часовой пояс обновлен!</b>

<b>Установлен:</b> {timezone_name}
<b>Время сейчас:</b> {current_time}

Теперь все даты и время будут отображаться в вашем часовом поясе."""

            await callback.message.edit_text(
                success_text,
                parse_mode="HTML"
            )

            # Отправляем новое сообщение с основной клавиатурой
            await callback.message.answer(
                "Вы можете продолжить работу с задачами:",
                reply_markup=get_main_keyboard()
            )

        else:
            await callback.answer(
                "❌ Ошибка при сохранении часового пояса",
                show_alert=True
            )

    except Exception as e:
        logger.error(
            f"Ошибка установки часового пояса для пользователя {user_id}: {e}"
        )
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "timezone_manual")
async def manual_timezone_input(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод часового пояса"""
    await callback.answer()
    await state.set_state(TimezoneStates.waiting_for_manual_timezone)

    manual_text = """✏️ <b>Ручной ввод часового пояса</b>

Введите название часового пояса в формате:
• <code>Europe/Moscow</code>
• <code>Asia/Tokyo</code>
• <code>America/New_York</code>

Или введите "отмена" для возврата к списку."""

    await callback.message.edit_text(
        manual_text,
        parse_mode="HTML"
    )


@router.message(TimezoneStates.waiting_for_manual_timezone)
async def save_manual_timezone(message: Message, state: FSMContext):
    """Сохранение часового пояса введенного вручную"""
    timezone_input = message.text.strip()

    if timezone_input.lower() in ['отмена', 'cancel']:
        await state.clear()
        await set_timezone_command(message, state)
        return

    # Валидируем введенный часовой пояс
    if not validate_timezone(timezone_input):
        await message.answer(
            "❌ Неверный часовой пояс. Попробуйте еще раз или введите 'отмена'."
        )
        return

    try:
        user_id = message.from_user.id
        success = await db.set_user_timezone(user_id, timezone_input)

        if success:
            await state.clear()
            current_time = get_user_current_time(timezone_input)

            success_text = f"""✅ <b>Часовой пояс обновлен!</b>

<b>Установлен:</b> {timezone_input}
<b>Время сейчас:</b> {current_time}

Теперь все даты и время будут отображаться в вашем часовом поясе."""

            await message.answer(
                success_text,
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                "❌ Ошибка при сохранении часового пояса. Попробуйте еще раз."
            )

    except Exception as e:
        logger.error(
            "Ошибка ручной установки часового пояса "
            f"для пользователя {message.from_user.id}: {e}"
        )
        await message.answer(
            "❌ Произошла ошибка при сохранении.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import TaskStates
from database import db
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from keyboards.inline import get_task_detail_keyboard
from utils.logging_config import get_logger

logger = get_logger(__name__)

router = Router()


@router.message(Command("new_task"))
@router.message(F.text == "📝 Добавить задачу")
@router.callback_query(F.data == "new_task")
async def new_task_command(update, state: FSMContext):
    """Начало процесса добавления новой задачи"""

    if isinstance(update, CallbackQuery):
        message = update.message
        await update.answer()
    else:
        message = update

    await state.set_state(TaskStates.waiting_for_new_task)

    prompt_text = """📝 <b>Добавление новой задачи</b>

Напиши текст своей задачи или заметки.

<i>Например:</i>
• Купить молоко
• Позвонить маме
• Подготовить презентацию к пятнице
• Записаться к врачу

Для отмены нажми кнопку "❌ Отмена" """

    if isinstance(update, CallbackQuery):
        await message.edit_text(
            prompt_text,
            parse_mode="HTML",
            reply_markup=None
        )
        # Отправляем новое сообщение с клавиатурой отмены
        await message.answer(
            "Жду текст задачи...",
            reply_markup=get_cancel_keyboard()
        )
    else:
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
    task_text = message.text.strip()

    # Валидация на уровне обработчика
    if not task_text:
        await message.answer(
            "❌ Текст задачи не может быть пустым. Попробуй еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return

    if len(task_text) > 1000:
        await message.answer(
            "❌ Текст задачи слишком длинный (максимум 1000 символов). "
            "Попробуй сократить:",
            reply_markup=get_cancel_keyboard()
        )
        return

    try:
        task_id = await db.add_task(message.from_user.id, task_text)
        await state.clear()

        success_text = f"""✅ <b>Задача успешно добавлена!</b>

📝 <i>{task_text}</i>

ID задачи: {task_id}"""

        await message.answer(
            success_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

    except ValueError as e:
        await message.answer(
            f"❌ {str(e)}",
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при сохранении задачи. Попробуй еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        logger.error(f"Error saving task for user {message.from_user.id}: {e}")


@router.message(TaskStates.waiting_for_task_edit)
async def save_edited_task(message: Message, state: FSMContext):
    """Сохранение отредактированной задачи"""
    new_text = message.text.strip()

    # Валидация
    if not new_text:
        await message.answer(
            "❌ Текст задачи не может быть пустым. Попробуй еще раз:"
        )
        return

    if len(new_text) > 1000:
        await message.answer(
            "❌ Текст задачи слишком длинный (максимум 1000 символов). "
            "Попробуй сократить:"
        )
        return

    try:
        data = await state.get_data()
        task_id = data.get('editing_task_id')

        if not task_id:
            await message.answer(
                "❌ Ошибка: не найден ID редактируемой задачи.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return

        success = await db.update_task(task_id, message.from_user.id, new_text)

        if success:
            await state.clear()

            # Получаем обновленную задачу и показываем детали
            task = await db.get_task_by_id(task_id, message.from_user.id)
            if task:
                from handlers.actions import format_task_detail_text
                task_detail_text = await format_task_detail_text(task)

                await message.answer(
                    "✅ Задача обновлена!",
                    reply_markup=get_main_keyboard()
                )

                await message.answer(
                    task_detail_text,
                    parse_mode="HTML",
                    reply_markup=get_task_detail_keyboard(
                        task_id, task['status']
                    )
                )
            else:
                await message.answer(
                    "✅ Задача обновлена!",
                    reply_markup=get_main_keyboard()
                )
        else:
            await message.answer(
                "❌ Не удалось обновить задачу. Попробуй еще раз."
            )

    except ValueError as e:
        await message.answer(f"❌ {str(e)}")
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при обновлении задачи.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        logger.error(
            "Ошибка обновления задачи "
            f"для пользователя {message.from_user.id}: {e}"
        )


@router.message(TaskStates.waiting_for_new_task, ~F.text)
@router.message(TaskStates.waiting_for_task_edit, ~F.text)
async def invalid_task_input(message: Message):
    """Обработка некорректного ввода при работе с задачами"""
    await message.answer(
        "❌ Пожалуйста, отправь текст задачи или нажми '❌ Отмена' для выхода.",
        reply_markup=get_cancel_keyboard()
    )

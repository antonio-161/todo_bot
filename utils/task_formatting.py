from utils.timezone_utils import format_datetime_for_user


async def format_task_detail_text(
        task: dict,
        user_timezone: str = 'UTC'
) -> str:
    """Форматирование текста с деталями задачи"""
    created_date = format_datetime_for_user(task['created_at'], user_timezone)
    status_text = "✅ Выполнена" if task['status'] else "⏳ Активна"

    text = f"""📝 <b>Детали задачи</b>

<b>Текст:</b>
<i>{task['task_text']}</i>

<b>Статус:</b> {status_text}
<b>Создана:</b> {created_date}"""

    if task['status'] and task['completed_at']:
        completed_date = format_datetime_for_user(
            task['completed_at'], user_timezone
        )
        text += f"\n<b>Выполнена:</b> {completed_date}"

    return text


def format_tasks_list_text(tasks: list, user_timezone: str = 'UTC') -> str:
    """Форматирование текста списка задач"""
    if not tasks:
        return """📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""

    tasks_text = f"📋 <b>Твои задачи ({len(tasks)})</b>\n\n"

    for i, task in enumerate(tasks, 1):
        # Используем пользовательский часовой пояс
        created_date = format_datetime_for_user(
            task['created_at'], user_timezone
        ).split(' в ')[0]  # Берем только дату без времени
        status_emoji = "✅" if task['status'] else "⏳"

        # Обрезаем длинные задачи в списке
        task_text = task['task_text']
        if len(task_text) > 60:
            task_text = task_text[:57] + "..."

        tasks_text += f"{i}. {status_emoji} <i>{task_text}</i>\n"
        tasks_text += f"   📅 {created_date}\n\n"

    tasks_text += "👆 <i>Нажми на задачу для подробного просмотра</i>"
    return tasks_text

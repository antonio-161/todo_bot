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


def format_tasks_list_text(
    tasks: list,
    user_timezone: str = 'UTC',
    show_completed: bool = False
) -> str:
    """Форматирование текста списка задач"""
    if not tasks:
        if show_completed:
            return """📋 <b>Список задач</b>

У тебя пока нет задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""
        else:
            return """📋 <b>Список задач</b>

У тебя пока нет активных задач!

Создай свою первую задачу с помощью кнопки ниже или команды /new_task"""

    # Разделяем задачи на активные и выполненные
    active_tasks = [task for task in tasks if not task['status']]
    completed_tasks = [task for task in tasks if task['status']]

    if show_completed:
        total_count = len(tasks)
        header = f"📋 <b>Все задачи ({total_count})</b>"
        if len(active_tasks) > 0 and len(completed_tasks) > 0:
            header += (
                f"\n<i>Активных: {len(active_tasks)}, "
                f"выполненных: {len(completed_tasks)}</i>"
            )
    else:
        header = f"📋 <b>Активные задачи ({len(active_tasks)})</b>"

    tasks_text = header + "\n\n"

    # Сначала показываем активные задачи
    if active_tasks:
        if show_completed and completed_tasks:
            tasks_text += "<b>⏳ Активные:</b>\n"

        for i, task in enumerate(active_tasks, 1):
            created_date = format_datetime_for_user(
                task['created_at'], user_timezone
            ).split(' в ')[0]

            task_text = task['task_text']
            if len(task_text) > 60:
                task_text = task_text[:57] + "..."

            tasks_text += f"{i}. ⏳ <i>{task_text}</i>\n"
            tasks_text += f"   📅 {created_date}\n\n"

    # Затем показываем выполненные (если режим включен)
    if show_completed and completed_tasks:
        if active_tasks:
            tasks_text += "<b>✅ Выполненные:</b>\n"

        for i, task in enumerate(completed_tasks, len(active_tasks) + 1):
            created_date = format_datetime_for_user(
                task['created_at'], user_timezone
            ).split(' в ')[0]

            completed_date = ""
            if task['completed_at']:
                completed_date = format_datetime_for_user(
                    task['completed_at'], user_timezone
                ).split(' в ')[0]

            task_text = task['task_text']
            if len(task_text) > 60:
                task_text = task_text[:57] + "..."

            tasks_text += f"{i}. ✅ <i>{task_text}</i>\n"
            tasks_text += f"   📅 {created_date}"
            if completed_date:
                tasks_text += f" → ✅ {completed_date}"
            tasks_text += "\n\n"

    tasks_text += "👇 <i>Нажми на задачу для подробного просмотра</i>"
    return tasks_text

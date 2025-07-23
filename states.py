from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    """Состояния для работы с задачами"""
    waiting_for_new_task = State()     # Ожидание ввода новой задачи
    # Ожидание ввода для редактирования задачи
    waiting_for_task_edit = State()

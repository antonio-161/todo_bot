import logging
import re
from openai import AsyncOpenAI
from config import QWEN_API_KEY

logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI/OpenRouter
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=QWEN_API_KEY,
)


def build_system_prompt(profile: dict) -> str:
    pass


def strip_markdown(text: str) -> str:
    """
    Удаляет основные элементы Markdown-разметки из текста.
    """
    # жирный и курсив
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    # заголовки
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # блоки цитат
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # списки "- ", "* ", "• "
    text = re.sub(r'^[\-\*\•]\s*', '', text, flags=re.MULTILINE)
    # убрать лишние двойные пробелы и переносы
    text = re.sub(r'\s+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


async def make_plan(profile: dict) -> str:
    """
    Генерация вдохновляющей цитаты
    """
    system_prompt = build_system_prompt(profile)
    user_prompt = (
        f"Пользователь выполнил задачу: «{task_text}».\n"
        "Напиши короткую (до 2 предложений) вдохновляющую цитату в дружеском тоне. "
        "Можно использовать эмодзи умеренно, без шаблонных фраз типа 'Молодец'."
    )

    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3-235b-a22b:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.choices[0].message.content
        cleaned_content = re.sub(
            r"<think>.*?</think>", "", content, flags=re.DOTALL
        ).strip()
        cleaned_content = strip_markdown(cleaned_content)
        return cleaned_content or "Ошибка: пустой ответ от сервиса."
    except Exception as e:
        logger.exception(f"Ошибка при генерации вдохновляющей цитаты: {e}")
        return "Ошибка сервиса, попробуйте позже."
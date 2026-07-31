"""generators/text/manager.py"""
from .base import TextGenerator
from .agnes import AgnesGenerator
from core.logger import get_logger

logger = get_logger("text_manager")

class TextManager:
    def __init__(self):
        self._generator: TextGenerator = AgnesGenerator()

    def generate(self, topic: str) -> str:
        try:
            return self._generator.generate(topic)
        except Exception as e:
            logger.error(f"Ошибка генерации текста: {e}")
            return f"⚡ Пост на тему: {topic}"

    # ----- НОВЫЙ МЕТОД ДЛЯ ГЕНЕРАЦИИ АНОНСА -----
    def generate_announce(self, topic: str, group_name: str) -> str:
        prompt = (
            f"Напиши короткий анонс (до 200 символов) для поста на тему '{topic}' "
            f"в группе {group_name}. Пригласи подписаться на группу и перейти по ссылке. "
            "Сделай текст вовлекающим и кратким."
        )
        try:
            return self._generator.generate(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации анонса: {e}")
            return f"🔥 Свежий пост на тему '{topic}' в группе {group_name}! Подписывайся, чтобы не пропустить новости."

text_manager = TextManager()
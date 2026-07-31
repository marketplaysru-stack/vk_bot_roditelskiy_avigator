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

text_manager = TextManager()
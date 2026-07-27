from core.base import TextGenerator

class DummyTextGenerator(TextGenerator):
    def generate(self, topic: str) -> str:
        return f"📢 {topic}\n\nЭто автоматический пост. Тема: {topic}."
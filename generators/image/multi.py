"""generators/image/multi.py"""
import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        # Генераторы для фона (иллюстрации)
        self.background_generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]
        # Генератор баннеров (накладывает текст)
        self.banner_generator = BannerGenerator(self.background_generators[0])

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        # Если это анонс или мы хотим баннер с текстом
        if is_announce or "Анонс" in prompt:
            # Формируем детальный промпт для фона
            bg_prompt = self._build_background_prompt(prompt)
            # Генерируем баннер с текстом
            try:
                return self.banner_generator.generate(bg_prompt, title=title, subtitle=subtitle, cta=cta)
            except Exception as e:
                logger.error(f"Ошибка генерации баннера: {e}")

        # Если не анонс – генерируем обычную картинку через background_generators
        prompt = self._build_background_prompt(prompt)
        for gen in self.background_generators:
            try:
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    return result
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        # Заглушка
        return self._create_fallback_image()

    def _build_background_prompt(self, raw_prompt: str) -> str:
        # Строим промпт для фона (иллюстрации) как раньше, но с акцентом на плоский дизайн
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                else:
                    topic = parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "technology and innovation"

        # Шаблон для плоского дизайна (баннер)
        return (
            f"Modern flat vector illustration about {topic}. "
            f"Include abstract geometric shapes, icons, and simple graphics. "
            f"Use vibrant colors: blue, purple, gold, white. "
            f"Style: minimalistic, clean, professional, isometric. "
            f"Format: vertical 9:16, high resolution, bright, eye-catching. "
            f"No people, no faces, no text."
        )

    def _create_fallback_image(self) -> bytes:
        # как раньше
        ...

multi_image = MultiImageGenerator()
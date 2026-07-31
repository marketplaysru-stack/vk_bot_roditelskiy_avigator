"""generators/image/multi.py"""
import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]

    def generate(self, prompt: str) -> Optional[bytes]:
        # Если промпт короткий или содержит только тему, преобразуем в детальный рекламный промпт
        if len(prompt) < 30 or "тему" in prompt or prompt.startswith("Анонс"):
            prompt = self._build_promotional_prompt(prompt)

        for gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {gen.__class__.__name__} с промптом: {prompt[:100]}...")
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"Успешно, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"Генератор вернул пустой результат")
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        logger.info("Создаём локальную картинку-заглушку")
        return self._create_fallback_image()

    def _build_promotional_prompt(self, topic: str) -> str:
        """Формирует рекламный промпт для картинки на основе темы."""
        # Извлекаем ключевые слова из темы (удаляем стоп-слова)
        stopwords = {'и', 'в', 'на', 'с', 'по', 'для', 'как', 'новый', 'новые', 'это', 'что', 'при', 'через', 'без', 'у'}
        words = topic.split()
        keywords = [w for w in words if w.lower() not in stopwords and len(w) > 2]
        if not keywords:
            keywords = ["технологии", "инновации"]

        # Выбираем случайный стиль
        styles = [
            "яркий рекламный плакат, футуристичный дизайн, неоновые цвета",
            "современный минималистичный баннер, высокое качество, 4K",
            "динамичный постер, абстрактные формы, золотые и синие тона",
            "изометрическая иллюстрация, плоский дизайн, технологичные иконки"
        ]
        style = random.choice(styles)

        # Выбираем цветовую гамму
        palettes = [
            "синий, фиолетовый, золотой",
            "тёмно-синий, бирюзовый, белый",
            "чёрный, золотой, серебряный",
            "индиго, розовый, неоновый зелёный"
        ]
        colors = random.choice(palettes)

        # Формируем промпт
        prompt = (
            f"Создай изображение в стиле {style}. "
            f"Тема: {topic}. "
            f"Включи элементы: {', '.join(keywords[:5])}. "
            f"Используй цвета: {colors}. "
            f"Формат: вертикальный, 9:16, для социальных сетей. "
            f"Без людей, без текста, без лиц. "
            f"Высокое разрешение, детализированно."
        )
        return prompt

    def _create_fallback_image(self) -> bytes:
        try:
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color='#0a0a2e')
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            except:
                font = ImageFont.load_default()

            text = "AI Навигатор"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='#FFD700', font=font)

            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Ошибка создания заглушки: {e}")
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()
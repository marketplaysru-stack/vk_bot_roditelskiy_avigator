"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.pollinations = PollinationsGenerator(timeout=90)
        self.picsum = PicsumGenerator()
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        # Определяем категорию
        category = self._detect_category(prompt)
        # Строим детальный промпт для Pollinations на английском
        detailed_prompt = self._build_detailed_prompt(prompt, category)

        # Пытаемся сгенерировать через Pollinations
        try:
            logger.info(f"Генерация через Pollinations с промптом: {detailed_prompt[:150]}...")
            image_bytes = self.pollinations.generate(detailed_prompt)
            if image_bytes and isinstance(image_bytes, bytes) and len(image_bytes) > 0:
                logger.info(f"✅ Изображение получено, размер {len(image_bytes)} байт")
                # Если это анонс – накладываем текст
                if is_announce:
                    return self.banner_generator.create_banner_from_image(
                        image_bytes,
                        title=title or "🔥 НОВОСТЬ",
                        subtitle=subtitle or prompt[:60],
                        cta=cta or "ПОДПИСЫВАЙСЯ"
                    )
                return image_bytes
        except Exception as e:
            logger.error(f"Pollinations ошибка: {e}")

        # Если Pollinations не сработал – пробуем Picsum (случайное фото)
        logger.warning("Pollinations не дал результат, используем Picsum с текстом")
        try:
            bg_bytes = self.picsum.generate(prompt)
            if bg_bytes:
                if is_announce:
                    return self.banner_generator.create_banner_from_image(
                        bg_bytes,
                        title=title or "🔥 НОВОСТЬ",
                        subtitle=subtitle or prompt[:60],
                        cta=cta or "ПОДПИСЫВАЙСЯ"
                    )
                else:
                    return self.banner_generator.create_banner_from_image(
                        bg_bytes,
                        title=prompt[:50],
                        subtitle="Подробности в посте",
                        cta="ЧИТАТЬ"
                    )
        except Exception as e:
            logger.error(f"Picsum ошибка: {e}")

        # Если всё совсем плохо – баннер-заглушка
        logger.warning("Все генераторы не сработали, создаём баннер-заглушку")
        if is_announce:
            return self.banner_generator.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category
            )
        else:
            return self.banner_generator.create_banner(
                title=prompt[:50],
                subtitle="Подробности в посте",
                cta="ЧИТАТЬ",
                category=category
            )

    def _detect_category(self, prompt: str) -> str:
        topic = prompt.lower()
        if any(w in topic for w in ['строитель', 'архитектур', 'здание', 'ремонт', 'стройка', 'bim', 'кран', 'чертёж']):
            return "construction"
        elif any(w in topic for w in ['бизнес', 'предприним', 'стартап', 'инвест', 'финанс']):
            return "business"
        elif any(w in topic for w in ['ии', 'нейросет', 'ai', 'машинн', 'интеллект', 'чатгпт']):
            return "ai"
        elif any(w in topic for w in ['образован', 'учёб', 'школ', 'университет', 'курс', 'лекция']):
            return "education"
        else:
            return "general"

    def _build_detailed_prompt(self, raw_prompt: str, category: str) -> str:
        # Извлекаем тему
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                topic = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "Technology and innovation"

        # Детализируем в зависимости от категории
        templates = {
            "construction": f"Professional illustration of {topic}. Include construction site, cranes, blueprints, hard hats, buildings, BIM model. Style: flat design, modern architecture, vibrant colors: blue, orange, white, gray. High resolution, 4K, vertical 9:16, no text, no people.",
            "business": f"Corporate illustration of {topic}. Include growth charts, graphs, gears, handshake, dollar signs. Style: clean, modern, flat vector. Colors: navy, gold, white, teal. High resolution, 4K, vertical 9:16, no text, no people.",
            "ai": f"Futuristic illustration of {topic}. Include neural networks, AI chips, data streams, glowing circuits. Style: cyberpunk, neon, high-tech. Colors: purple, blue, cyan, gold. High resolution, 4K, vertical 9:16, no text, no people.",
            "education": f"Educational illustration of {topic}. Include books, graduation cap, light bulb, globe, pencils. Style: colorful, flat vector, playful. Colors: blue, yellow, green, white. High resolution, 4K, vertical 9:16, no text, no people.",
            "general": f"Creative illustration of {topic}. Include abstract icons, geometric shapes. Style: modern, clean, flat design. Colors: blue, purple, orange, white. High resolution, 4K, vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

multi_image = MultiImageGenerator()
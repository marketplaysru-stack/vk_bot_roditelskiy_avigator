"""generators/image/multi.py – баннер (основной), Pollinations, Picsum"""
import logging
from typing import Optional
from .base import ImageGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.pollinations = PollinationsGenerator(timeout=90)
        self.picsum = PicsumGenerator()
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Для анонсов сразу баннер (быстро и стабильно)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category,
                is_announce=True
            )

        # Для постов – сначала пытаемся получить картинку через Pollinations
        detailed_prompt = self._build_detailed_prompt(prompt, category)
        image_bytes = None

        # 1) Pollinations
        try:
            logger.info(f"Pollinations: {detailed_prompt[:150]}...")
            result = self.pollinations.generate(detailed_prompt)
            if result:
                logger.info(f"✅ Pollinations успешно, {len(result)} байт")
                image_bytes = result
        except Exception as e:
            logger.error(f"Pollinations ошибка: {e}")

        # 2) Если Pollinations дал результат – накладываем текст (как в анонсах) или оставляем как есть
        if image_bytes:
            try:
                return self.banner.create_banner_from_image(
                    image_bytes,
                    title=title or prompt[:50],
                    subtitle=subtitle or "Подробности в посте",
                    cta=cta or "ЧИТАТЬ"
                )
            except Exception as e:
                logger.error(f"Ошибка наложения текста: {e}")
                # Если не получилось наложить текст, возвращаем картинку без текста
                return image_bytes

        # 3) Если Pollinations не сработал – баннер с нуля
        logger.warning("Pollinations не сработал, создаём баннер")
        return self.banner.create_banner(
            title=title or prompt[:50],
            subtitle=subtitle or "Подробности в посте",
            cta=cta or "ЧИТАТЬ",
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
        else:
            return "general"

    def _build_detailed_prompt(self, raw_prompt: str, category: str) -> str:
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                topic = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "Technology and innovation"

        templates = {
            "construction": f"Professional illustration about {topic}. Construction site, cranes, blueprints, hard hats, buildings, BIM model. High detail, 4K, flat design, vibrant colors: blue, orange, white. Vertical 9:16, no text, no people.",
            "business": f"Corporate illustration about {topic}. Growth charts, graphs, gears, handshake, dollar signs. Professional, clean, modern, high resolution, navy, gold, white, teal. Vertical 9:16, no text, no people.",
            "ai": f"Futuristic illustration about {topic}. Neural networks, AI chips, data streams, glowing circuits. Cyberpunk, neon, high-tech, 8K, purple, blue, cyan, gold. Vertical 9:16, no text, no people.",
            "general": f"Creative illustration about {topic}. Abstract icons, geometric shapes. Modern, clean, flat design, high quality, blue, purple, orange, white. Vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

multi_image = MultiImageGenerator()
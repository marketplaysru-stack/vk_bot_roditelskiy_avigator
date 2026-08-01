"""generators/image/multi.py – Pexels (основной), Pollinations, баннер"""
import logging
from typing import Optional
from .base import ImageGenerator
from .pexels import PexelsGenerator
from .pollinations import PollinationsGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.pexels = PexelsGenerator(timeout=30)
        self.pollinations = PollinationsGenerator(timeout=90)
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Анонсы – баннер (быстро)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category,
                is_announce=True
            )

        # Посты – сначала Pexels
        try:
            logger.info(f"Pexels: {prompt[:50]}...")
            result = self.pexels.generate(prompt)
            if result:
                logger.info(f"✅ Pexels успешно, {len(result)} байт")
                # Накладываем текст
                return self.banner.create_banner_from_image(
                    result,
                    title=title or prompt[:50],
                    subtitle=subtitle or "Подробности в посте",
                    cta=cta or "ЧИТАТЬ"
                )
        except Exception as e:
            logger.error(f"Pexels ошибка: {e}")

        # Если Pexels не сработал – Pollinations
        detailed_prompt = self._build_detailed_prompt(prompt, category)
        try:
            logger.info(f"Pollinations: {detailed_prompt[:150]}...")
            result = self.pollinations.generate(detailed_prompt)
            if result:
                logger.info(f"✅ Pollinations успешно, {len(result)} байт")
                return self.banner.create_banner_from_image(
                    result,
                    title=title or prompt[:50],
                    subtitle=subtitle or "Подробности в посте",
                    cta=cta or "ЧИТАТЬ"
                )
        except Exception as e:
            logger.error(f"Pollinations ошибка: {e}")

        # Если ничего не сработало – баннер
        logger.warning("Все генераторы не сработали, создаём баннер")
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
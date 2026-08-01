"""generators/image/multi.py – Pollinations (основной), Picsum, баннер (без HF/внешних API)"""
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

        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category,
                is_announce=True
            )

        # Формируем улучшенный промпт на английском с деталями
        detailed_prompt = self._build_detailed_prompt(prompt, category)

        # 1) Pollinations – основной генератор
        try:
            logger.info(f"Pollinations: {detailed_prompt[:150]}...")
            result = self.pollinations.generate(detailed_prompt)
            if result:
                logger.info(f"✅ Pollinations успешно, {len(result)} байт")
                return result
        except Exception as e:
            logger.error(f"Pollinations ошибка: {e}")

        # 2) Picsum + текст (если Pollinations упал)
        logger.warning("Pollinations не сработал, используем Picsum с текстом")
        try:
            bg_bytes = self.picsum.generate(prompt)
            if bg_bytes:
                return self.banner.create_banner_from_image(
                    bg_bytes,
                    title=title or prompt[:50],
                    subtitle=subtitle or "Подробности в посте",
                    cta=cta or "ЧИТАТЬ"
                )
        except Exception as e:
            logger.error(f"Picsum ошибка: {e}")

        # 3) Последний резерв – баннер
        logger.warning("Все генераторы не сработали, баннер-заглушка")
        return self.banner.create_banner(
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
            topic = "technology and innovation"

        # Улучшенные промпты с акцентом на реализм и детали
        templates = {
            "construction": f"Professional architectural visualization of {topic}. Construction site with cranes, blueprints, hard hats, modern buildings, BIM model. Photorealistic, 8K, cinematic lighting, vivid colors: blue, orange, white. Vertical composition 9:16, no text, no people.",
            "business": f"Corporate illustration of {topic}. Growth charts, financial graphs, gears, handshake, dollar signs. Clean, modern, flat vector with gradients. High detail, 4K, navy, gold, white, teal. Vertical 9:16, no text, no people.",
            "ai": f"Futuristic digital art of {topic}. Neural networks, AI chips, glowing data streams, abstract circuits. Cyberpunk, neon, high-tech. Ultra realistic, 8K, purple, blue, cyan, gold. Vertical 9:16, no text, no people.",
            "general": f"Creative vector illustration of {topic}. Abstract icons, geometric shapes, modern tech elements. High resolution, vibrant colors, blue, purple, orange, white. Vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

multi_image = MultiImageGenerator()
"""generators/image/multi.py – только GenAPI + резервы"""
import logging
from typing import Optional
from .base import ImageGenerator
from .genapi import GenAPIGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.genapi = GenAPIGenerator(timeout=180)
        self.picsum = PicsumGenerator()
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Анонсы – сразу баннер (быстро)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category
            )

        # Посты – GenAPI
        detailed_prompt = self._build_detailed_prompt(prompt, category)
        try:
            logger.info(f"GenAPI: {detailed_prompt[:150]}...")
            result = self.genapi.generate(detailed_prompt)
            if result:
                logger.info(f"✅ GenAPI успешно, {len(result)} байт")
                return result
        except Exception as e:
            logger.error(f"GenAPI ошибка: {e}")

        # Резерв – Picsum
        logger.warning("GenAPI не сработал, используем Picsum")
        try:
            result = self.picsum.generate(prompt)
            if result:
                return result
        except Exception as e:
            logger.error(f"Picsum ошибка: {e}")

        # Последний резерв – баннер
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
            topic = "Technology and innovation"

        templates = {
            "construction": f"Professional illustration about {topic}. Construction site, cranes, blueprints, hard hats, buildings, BIM model. Flat design, modern architecture, vibrant colors: blue, orange, white. Vertical 9:16, no text, no people.",
            "business": f"Corporate illustration about {topic}. Growth charts, graphs, gears, handshake, dollar signs. Clean, modern, flat vector. Navy, gold, white, teal. Vertical 9:16, no text, no people.",
            "ai": f"Futuristic illustration about {topic}. Neural networks, AI chips, data streams, glowing circuits. Cyberpunk, neon, high-tech. Purple, blue, cyan, gold. Vertical 9:16, no text, no people.",
            "general": f"Creative illustration about {topic}. Abstract icons, geometric shapes. Modern, clean, flat design. Blue, purple, orange, white. Vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

multi_image = MultiImageGenerator()
"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner_generator.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category
            )
        else:
            logger.info("Генерация баннера для поста")
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

multi_image = MultiImageGenerator()
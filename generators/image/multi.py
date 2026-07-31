"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .genapi import GenAPIGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            ("GenAPI", GenAPIGenerator(timeout=120)),
            ("Pollinations", PollinationsGenerator(timeout=90)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)

        # Для анонсов – сразу баннер (чтобы не ждать генерацию)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            try:
                return self.banner_generator.create_banner(
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ",
                    category=category
                )
            except Exception as e:
                logger.error(f"Ошибка баннера для анонса: {e}")
                # Если баннер не сработал, пробуем обычную генерацию (но не для анонса)

        # Для постов – пробуем генераторы по очереди
        detailed_prompt = self._build_detailed_prompt(prompt, category)
        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name}")
                # Для GenAPI передаём дополнительные параметры
                if name == "GenAPI":
                    # Параметры для GenAPI (можно настроить под свои нужды)
                    result = gen.generate(
                        detailed_prompt,
                        model="medium",
                        aspect_ratio="9:16",
                        creativity="high"
                    )
                else:
                    result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно через {name}, размер {len(result)} байт")
                    # Если это анонс (и мы не создали баннер) – накладываем текст
                    if is_announce:
                        return self.banner_generator.create_banner_from_image(
                            result,
                            title=title or "🔥 НОВОСТЬ",
                            subtitle=subtitle or prompt[:60],
                            cta=cta or "ПОДПИСЫВАЙСЯ"
                        )
                    return result
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        # Если ничего не сработало – баннер-заглушка
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
            "construction": f"Professional digital illustration about {topic}. Include construction site, cranes, blueprints, hard hats, buildings, BIM model. Style: flat design, modern architecture, vibrant colors: blue, orange, white, gray. High resolution, 4K, vertical 9:16, no text, no people.",
            "business": f"Corporate digital illustration about {topic}. Include growth charts, graphs, gears, handshake, dollar signs. Style: clean, modern, flat vector. Colors: navy, gold, white, teal. High resolution, 4K, vertical 9:16, no text, no people.",
            "ai": f"Futuristic digital illustration about {topic}. Include neural networks, AI chips, data streams, glowing circuits. Style: cyberpunk, neon, high-tech. Colors: purple, blue, cyan, gold. High resolution, 4K, vertical 9:16, no text, no people.",
            "education": f"Educational digital illustration about {topic}. Include books, graduation cap, light bulb, globe, pencils. Style: colorful, flat vector, playful. Colors: blue, yellow, green, white. High resolution, 4K, vertical 9:16, no text, no people.",
            "general": f"Creative digital illustration about {topic}. Include abstract icons, geometric shapes. Style: modern, clean, flat design. Colors: blue, purple, orange, white. High resolution, 4K, vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

multi_image = MultiImageGenerator()
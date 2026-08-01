"""generators/image/multi.py – GenAPI, Pollinations, Picsum с текстом для всех"""
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
        self.genapi = GenAPIGenerator(timeout=180)
        self.pollinations = PollinationsGenerator(timeout=90)
        self.picsum = PicsumGenerator()
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)
        detailed_prompt = self._build_detailed_prompt(prompt, category)

        # Пытаемся получить изображение от генераторов
        image_bytes = None
        error_messages = []

        # 1) GenAPI
        try:
            logger.info(f"GenAPI: {detailed_prompt[:150]}...")
            result = self.genapi.generate(detailed_prompt)
            if result:
                logger.info(f"✅ GenAPI успешно, {len(result)} байт")
                image_bytes = result
        except Exception as e:
            logger.error(f"GenAPI ошибка: {e}")
            error_messages.append(f"GenAPI: {e}")

        # 2) Pollinations
        if not image_bytes:
            try:
                logger.info(f"Pollinations: {detailed_prompt[:150]}...")
                result = self.pollinations.generate(detailed_prompt)
                if result:
                    logger.info(f"✅ Pollinations успешно, {len(result)} байт")
                    image_bytes = result
            except Exception as e:
                logger.error(f"Pollinations ошибка: {e}")
                error_messages.append(f"Pollinations: {e}")

        # 3) Picsum (без текста, просто фото)
        if not image_bytes:
            try:
                logger.info("Picsum: получение случайного фото")
                result = self.picsum.generate(prompt)
                if result:
                    logger.info(f"✅ Picsum успешно, {len(result)} байт")
                    image_bytes = result
            except Exception as e:
                logger.error(f"Picsum ошибка: {e}")
                error_messages.append(f"Picsum: {e}")

        # Если есть изображение – накладываем текст (для анонсов или постов)
        if image_bytes:
            try:
                if is_announce:
                    final = self.banner.create_banner_from_image(
                        image_bytes,
                        title=title or "🔥 НОВОСТЬ",
                        subtitle=subtitle or prompt[:60],
                        cta=cta or "ПОДПИСЫВАЙСЯ"
                    )
                else:
                    final = self.banner.create_banner_from_image(
                        image_bytes,
                        title=title or prompt[:50],
                        subtitle=subtitle or "Подробности в посте",
                        cta=cta or "ЧИТАТЬ"
                    )
                logger.info(f"Баннер с текстом создан, размер {len(final)} байт")
                return final
            except Exception as e:
                logger.error(f"Ошибка наложения текста: {e}")
                # Возвращаем изображение без текста, чтобы не потерять картинку
                return image_bytes

        # Если ничего не сработало – баннер-заглушка (последний резерв)
        logger.warning(f"Все генераторы не сработали: {error_messages}")
        if is_announce:
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category,
                is_announce=True
            )
        else:
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
"""generators/image/multi.py – Cloudflare (основной) + резервы"""
import logging
import requests
from typing import Optional
from .base import ImageGenerator
from .genapi import GenAPIGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from config import config

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.cloudflare_url = config.cloudflare_worker_url
        self.cloudflare_key = config.cloudflare_api_key
        self.genapi = GenAPIGenerator(timeout=180)
        self.pollinations = PollinationsGenerator(timeout=90)
        self.picsum = PicsumGenerator()
        self.banner = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        category = self._detect_category(prompt)
        detailed_prompt = self._build_detailed_prompt(prompt, category)

        # Анонсы – баннер (можно использовать те же генераторы, но оставим баннер)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            return self.banner.create_banner(
                title=title or "🔥 НОВОСТЬ",
                subtitle=subtitle or prompt[:60],
                cta=cta or "ПОДПИСЫВАЙСЯ",
                category=category,
                is_announce=True
            )

        # 1) Сначала пробуем Cloudflare
        if self.cloudflare_url:
            try:
                logger.info(f"Cloudflare: {detailed_prompt[:150]}...")
                result = self._cloudflare_generate(detailed_prompt)
                if result:
                    logger.info(f"✅ Cloudflare успешно, {len(result)} байт")
                    # Для постов возвращаем картинку без текста
                    return result
            except Exception as e:
                logger.error(f"Cloudflare ошибка: {e}")

        # 2) GenAPI
        try:
            logger.info(f"GenAPI: {detailed_prompt[:150]}...")
            result = self.genapi.generate(detailed_prompt)
            if result:
                logger.info(f"✅ GenAPI успешно, {len(result)} байт")
                return result
        except Exception as e:
            logger.error(f"GenAPI ошибка: {e}")

        # 3) Pollinations
        try:
            logger.info(f"Pollinations: {detailed_prompt[:150]}...")
            result = self.pollinations.generate(detailed_prompt)
            if result:
                logger.info(f"✅ Pollinations успешно, {len(result)} байт")
                return result
        except Exception as e:
            logger.error(f"Pollinations ошибка: {e}")

        # 4) Picsum с текстом
        logger.warning("Все генераторы не сработали, используем Picsum с текстом")
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

        # 5) Последний резерв – баннер
        logger.warning("Все генераторы не сработали, баннер-заглушка")
        return self.banner.create_banner(
            title=prompt[:50],
            subtitle="Подробности в посте",
            cta="ЧИТАТЬ",
            category=category
        )

    def _cloudflare_generate(self, prompt: str) -> bytes:
        headers = {"Content-Type": "application/json"}
        if self.cloudflare_key:
            headers["Authorization"] = f"Bearer {self.cloudflare_key}"
        resp = requests.post(
            self.cloudflare_url,
            json={"prompt": prompt},
            headers=headers,
            timeout=90
        )
        resp.raise_for_status()
        return resp.content

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
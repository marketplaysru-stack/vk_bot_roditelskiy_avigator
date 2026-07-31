"""generators/image/multi.py"""
import random
import logging
import re
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.background_generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        # Для анонсов – используем локальный баннер (без внешних запросов)
        if is_announce:
            logger.info("Генерация баннера для анонса")
            try:
                return self.banner_generator.create_banner(title=title, subtitle=subtitle, cta=cta)
            except Exception as e:
                logger.error(f"Ошибка создания баннера: {e}")
                return self._create_fallback_image()

        # Для постов – используем внешние генераторы с детальным промптом
        bg_prompt = self._build_detailed_prompt(prompt, is_announce=False)
        for gen in self.background_generators:
            try:
                logger.info(f"Попытка генерации фона через {gen.__class__.__name__} с промптом: {bg_prompt[:150]}...")
                result = gen.generate(bg_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"Фон получен, размер {len(result)} байт")
                    return result
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        return self._create_fallback_image()

    def _build_detailed_prompt(self, raw_prompt: str, is_announce: bool) -> str:
        # Извлекаем тему
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                else:
                    topic = parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "technology and innovation"

        keywords = topic.lower()
        if any(w in keywords for w in ['строитель', 'архитектур', 'здание', 'ремонт', 'стройка', 'bim']):
            category = "construction"
        elif any(w in keywords for w in ['бизнес', 'предприним', 'стартап', 'инвест']):
            category = "business"
        elif any(w in keywords for w in ['ии', 'нейросет', 'ai', 'машинн', 'интеллект']):
            category = "ai"
        else:
            category = "general"

        templates = {
            "construction": f"Professional vector illustration about {topic}. Include construction site, cranes, blueprints, hard hats, buildings, tools. Style: flat design, vibrant colors, modern architecture. Use blue, orange, white, gray. Vertical 9:16, no text, no people.",
            "business": f"Corporate illustration about {topic}. Include growth charts, graphs, gears, handshake, dollar signs. Style: professional, clean, modern, flat vector. Use navy, gold, white, teal. Vertical 9:16, no text, no people.",
            "ai": f"Futuristic illustration about {topic}. Include neural networks, AI chips, data streams, glowing circuits. Style: cyberpunk, neon, high-tech. Use purple, blue, cyan, gold. Vertical 9:16, no text, no people.",
            "general": f"Creative vector illustration about {topic}. Include abstract icons, geometric shapes. Style: modern, clean, flat design. Use blue, purple, orange, white. Vertical 9:16, no text, no people."
        }
        return templates.get(category, templates["general"])

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
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()
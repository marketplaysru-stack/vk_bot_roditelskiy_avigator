"""generators/image/multi.py"""
import random
import logging
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
        # Для анонсов – используем встроенный баннер
        if is_announce:
            logger.info("Генерация баннера для анонса")
            try:
                return self.banner_generator.generate(prompt=prompt, title=title, subtitle=subtitle, cta=cta)
            except Exception as e:
                logger.error(f"Ошибка генерации баннера: {e}")
                # fallback: заглушка
                return self._create_fallback_image()

        # Для постов – используем внешние генераторы (иллюстрация)
        prompt = self._build_background_prompt(prompt)
        for gen in self.background_generators:
            try:
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    return result
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        return self._create_fallback_image()

    def _build_background_prompt(self, raw_prompt: str) -> str:
        # как раньше (оставляем для иллюстраций)
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
        return (
            f"Modern flat vector illustration about {topic}. "
            f"Include abstract geometric shapes, icons, and simple graphics. "
            f"Use vibrant colors: blue, purple, gold, white. "
            f"Style: minimalistic, clean, professional, isometric. "
            f"Format: vertical 9:16, high resolution, bright, eye-catching. "
            f"No people, no faces, no text."
        )

    def _create_fallback_image(self) -> bytes:
        # заглушка (как раньше)
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
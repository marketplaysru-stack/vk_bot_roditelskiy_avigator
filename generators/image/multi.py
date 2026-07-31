"""generators/image/multi.py"""
import random
import logging
from typing import Optional
from .base import ImageGenerator
from .picsum import PicsumGenerator
from .pollinations import PollinationsGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            PollinationsGenerator(),
            PicsumGenerator(),
        ]

    def generate(self, prompt: str) -> Optional[bytes]:
        # Если промпт короткий или содержит "тему" или "Анонс", строим детальный промпт на английском
        if len(prompt) < 30 or "тему" in prompt or prompt.startswith("Анонс"):
            is_announce = "Анонс" in prompt
            prompt = self._build_promotional_prompt(prompt, is_announce)

        for gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {gen.__class__.__name__} с промптом (первые 100 символов): {prompt[:100]}...")
                result = gen.generate(prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"Успешно, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"Генератор вернул пустой результат")
            except Exception as e:
                logger.warning(f"{gen.__class__.__name__} не сработал: {e}")

        logger.info("Создаём локальную картинку-заглушку")
        return self._create_fallback_image()

    def _build_promotional_prompt(self, raw_prompt: str, is_announce: bool = False) -> str:
        """Формирует детальный рекламный промпт на английском."""
        # Извлекаем тему из промпта (убираем "Анонс:" и лишнее)
        topic = raw_prompt
        if "Анонс" in topic:
            # Убираем "Анонс:" и всё до двоеточия
            if ":" in topic:
                parts = topic.split(":", 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                else:
                    topic = parts[0].strip()
            # Убираем "— подпишись на ..." если есть
            if "—" in topic:
                topic = topic.split("—")[0].strip()

        # Если тема слишком короткая, используем заглушку
        if len(topic) < 5:
            topic = "technology and innovation"

        # Список объектов для разных категорий (выбираем случайно)
        objects_pool = [
            "charts, graphs, data visualization",
            "gears, circuit boards, microchips",
            "light bulbs, idea icons, brain with neural links",
            "abstract geometric shapes, isometric cubes, glowing hexagons",
            "business icons, handshake, target, money bags, arrows up",
            "cloud computing, servers, network nodes, wifi symbols",
            "education icons, books, graduation cap, pencil, ruler"
        ]
        # Выбираем 2–3 случайных набора
        selected = random.sample(objects_pool, k=min(2, len(objects_pool)))
        objects = " and ".join(selected)

        # Базовые стили
        styles = [
            "modern flat design, vibrant colors, professional infographic",
            "futuristic isometric illustration, neon accents, high detail",
            "minimalist vector art, clean lines, bright gradient background",
            "corporate style, polished, 3D elements, glossy surfaces"
        ]
        style = random.choice(styles)

        # Цвета
        palettes = [
            "blue, purple, gold",
            "dark blue, teal, white",
            "black, gold, silver",
            "indigo, pink, neon green",
            "orange, navy, white"
        ]
        colors = random.choice(palettes)

        # Для анонса добавляем призыв
        call_to_action = ""
        if is_announce:
            call_to_action = "with a clear call to action like 'Subscribe' or 'Join now', eye-catching buttons, energetic composition"

        # Собираем промпт на английском
        prompt = (
            f"Professional promotional illustration about {topic}. "
            f"Include {objects}. "
            f"Use {style}. "
            f"Color palette: {colors}. "
            f"{call_to_action} "
            f"Format: vertical 9:16, high resolution, bright, catchy, for social media ad. "
            f"No people, no faces, no text."
        )
        return prompt

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
            logger.error(f"Ошибка создания заглушки: {e}")
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()
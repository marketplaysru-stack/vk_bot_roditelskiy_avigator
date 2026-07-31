"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        # Основной генератор – Pollinations (бесплатный, без ключей)
        self.generators = [
            ("Pollinations", PollinationsGenerator(timeout=90)),
            ("Picsum", PicsumGenerator()),   # резерв
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        # Для постов и анонсов используем одинаковую логику: сначала пытаемся получить картинку от внешнего генератора
        detailed_prompt = self._build_detailed_prompt(prompt)
        logger.info(f"Промпт для генерации: {detailed_prompt[:200]}...")

        image_bytes = None
        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name} с таймаутом {getattr(gen, 'timeout', 'N/A')} сек")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно сгенерировано через {name}, размер {len(result)} байт")
                    image_bytes = result
                    break
                else:
                    logger.warning(f"{name} вернул пустой результат")
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        # Если внешние генераторы не дали результат – создаём простую заглушку
        if not image_bytes:
            logger.warning("Не удалось получить картинку, создаём заглушку")
            image_bytes = self._create_fallback_image()

        # Если это анонс – накладываем текст поверх картинки
        if is_announce:
            try:
                logger.info("Накладываем текст на картинку для анонса")
                return self.banner_generator.create_banner_from_image(
                    image_bytes,
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ"
                )
            except Exception as e:
                logger.error(f"Ошибка наложения текста: {e}")
                return image_bytes  # возвращаем картинку без текста

        # Для поста – возвращаем картинку как есть
        return image_bytes

    def _detect_category(self, prompt: str) -> str:
        # категория пока не используется, оставляем для совместимости
        return "general"

    def _build_detailed_prompt(self, raw_prompt: str) -> str:
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                topic = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "технологии и инновации"

        # Определяем категорию для более точного промпта
        keywords = topic.lower()
        if any(w in keywords for w in ['строитель', 'архитектур', 'здание', 'ремонт', 'стройка', 'bim', 'кран', 'чертёж']):
            category = "construction"
        elif any(w in keywords for w in ['бизнес', 'предприним', 'стартап', 'инвест', 'финанс']):
            category = "business"
        elif any(w in keywords for w in ['ии', 'нейросет', 'ai', 'машинн', 'интеллект', 'чатгпт']):
            category = "ai"
        else:
            category = "general"

        templates = {
            "construction": f"Professional illustration about {topic}. Include construction site, cranes, blueprints, hard hats, buildings, BIM model. Style: flat design, modern architecture, vibrant colors: blue, orange, white. Vertical 9:16, no text, no people.",
            "business": f"Corporate illustration about {topic}. Include growth charts, graphs, gears, handshake, dollar signs. Style: clean, modern, flat vector. Colors: navy, gold, white, teal. Vertical 9:16, no text, no people.",
            "ai": f"Futuristic illustration about {topic}. Include neural networks, AI chips, data streams, glowing circuits. Style: cyberpunk, neon, high-tech. Colors: purple, blue, cyan, gold. Vertical 9:16, no text, no people.",
            "general": f"Creative illustration about {topic}. Include abstract icons, geometric shapes. Style: modern, clean, flat design. Colors: blue, purple, orange, white. Vertical 9:16, no text, no people."
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
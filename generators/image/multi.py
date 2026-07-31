"""generators/image/multi.py"""
import logging
from typing import Optional
from .base import ImageGenerator
from .agnes import AgnesImageGenerator
from .huggingface import HuggingFaceGenerator
from .pollinations import PollinationsGenerator
from .picsum import PicsumGenerator
from .banner import BannerGenerator
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class MultiImageGenerator(ImageGenerator):
    def __init__(self):
        self.generators = [
            ("Agnes", AgnesImageGenerator(timeout=120)),
            ("HuggingFace", HuggingFaceGenerator(timeout=120)),
            ("Pollinations", PollinationsGenerator(timeout=60)),
            ("Picsum", PicsumGenerator()),
        ]
        self.banner_generator = BannerGenerator()

    def generate(self, prompt: str, is_announce: bool = False, title: str = "", subtitle: str = "", cta: str = "") -> Optional[bytes]:
        if is_announce:
            logger.info("Генерация баннера для анонса (локально)")
            try:
                return self.banner_generator.create_banner(
                    title=title or "🔥 НОВОСТЬ",
                    subtitle=subtitle or prompt[:60],
                    cta=cta or "ПОДПИСЫВАЙСЯ"
                )
            except Exception as e:
                logger.error(f"Ошибка создания баннера для анонса: {e}")
                return self._create_fallback_image()

        detailed_prompt = self._build_detailed_prompt(prompt)
        logger.info(f"Промпт для генерации: {detailed_prompt[:200]}...")

        for name, gen in self.generators:
            try:
                logger.info(f"Попытка генерации через {name} с таймаутом {getattr(gen, 'timeout', 'N/A')} сек")
                result = gen.generate(detailed_prompt)
                if result and isinstance(result, bytes) and len(result) > 0:
                    logger.info(f"✅ Успешно сгенерировано через {name}, размер {len(result)} байт")
                    return result
                else:
                    logger.warning(f"{name} вернул пустой результат")
            except Exception as e:
                logger.error(f"{name} ошибка: {e}")

        logger.warning("Все внешние генераторы не сработали, создаём баннер-заглушку")
        try:
            return self.banner_generator.create_banner(
                title=prompt[:50],
                subtitle="Подробности в посте",
                cta="ЧИТАТЬ"
            )
        except Exception as e:
            logger.error(f"Ошибка создания баннера-заглушки: {e}")
            return self._create_fallback_image()

    def _build_detailed_prompt(self, raw_prompt: str) -> str:
        # Упрощённая версия – можно расширить
        topic = raw_prompt
        if "Анонс" in topic:
            if ":" in topic:
                parts = topic.split(":", 1)
                topic = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            if "—" in topic:
                topic = topic.split("—")[0].strip()
        if len(topic) < 5:
            topic = "технологии и инновации"
        return f"Professional illustration about {topic}. Include relevant icons and graphics. Style: modern, flat design, vibrant colors. Vertical 9:16, no text, no people."

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
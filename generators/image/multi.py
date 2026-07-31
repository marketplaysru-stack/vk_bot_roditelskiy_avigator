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
        # Всегда создаём баннер через BannerGenerator
        logger.info("Генерация баннера для публикации")
        try:
            # Если это анонс, используем переданные title, subtitle, cta
            if is_announce:
                return self.banner_generator.create_banner(title=title, subtitle=subtitle, cta=cta)
            else:
                # Для поста генерируем баннер с темой как заголовком
                # Извлекаем тему из prompt
                topic = prompt
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
                    topic = "Технологии и инновации"
                # Создаём баннер для поста
                return self.banner_generator.create_banner(
                    title=topic[:50],
                    subtitle="Подробности в посте",
                    cta="ЧИТАТЬ"
                )
        except Exception as e:
            logger.error(f"Ошибка создания баннера: {e}")
            return self._create_fallback_image()

    def _create_fallback_image(self) -> bytes:
        # простая заглушка, если баннер не создался
        from PIL import Image, ImageDraw, ImageFont
        import io
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
        except:
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9c\x63\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'

multi_image = MultiImageGenerator()
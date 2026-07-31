"""generators/image/banner.py – генерация баннеров с текстом"""
import io
from PIL import Image, ImageDraw, ImageFont
import requests
from .base import ImageGenerator

class BannerGenerator(ImageGenerator):
    def __init__(self, background_generator=None):
        self.background_generator = background_generator

    def generate(self, prompt: str, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        """
        Генерирует баннер: берёт фон (иллюстрацию) и накладывает текст.
        """
        # 1) Получаем фон (иллюстрацию) от другого генератора
        if self.background_generator:
            bg_bytes = self.background_generator.generate(prompt)
        else:
            # Заглушка – просто синий фон
            bg_bytes = self._create_fallback_background()

        # 2) Загружаем изображение
        bg_img = Image.open(io.BytesIO(bg_bytes))

        # 3) Накладываем текст
        final_img = self._add_text(bg_img, title, subtitle, cta)

        # 4) Сохраняем в байты
        buf = io.BytesIO()
        final_img.save(buf, format='PNG')
        return buf.getvalue()

    def _add_text(self, img, title, subtitle, cta):
        """Накладывает текст на изображение."""
        # Создаём копию
        img = img.copy()
        draw = ImageDraw.Draw(img)

        # Размеры
        width, height = img.size

        # Шрифты (используем системные, если есть)
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Рисуем полупрозрачный фон для текста (чтобы читался)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        # Тёмный градиент снизу
        for y in range(height//2, height):
            alpha = int(200 * (1 - (y - height//2) / (height//2)))
            overlay_draw.rectangle((0, y, width, y+1), fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

        # Позиционируем текст снизу
        y_offset = height - 120
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 70

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 60

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            # Рисуем подложку под кнопку
            draw.rectangle((x-30, y_offset-20, x+tw+30, y_offset+60), fill='#FFD700', outline=None, width=0)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        return img

    def _create_fallback_background(self) -> bytes:
        # Создаём простой градиентный фон
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='#0a0a2e')
        # Добавим простой градиент
        for y in range(height):
            r = int(10 + (y / height) * 50)
            g = int(10 + (y / height) * 30)
            b = int(40 + (y / height) * 60)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
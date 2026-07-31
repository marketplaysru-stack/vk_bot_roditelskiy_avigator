"""generators/image/banner.py – накладывает текст на изображение"""
import io
from PIL import Image, ImageDraw, ImageFont
from .base import ImageGenerator

class BannerGenerator(ImageGenerator):
    def __init__(self):
        pass

    def generate(self, prompt: str = "", title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        """Генерирует баннер, но в нашем случае используется только для наложения текста на готовое изображение."""
        # Это заглушка, реальная работа через create_banner_from_image
        return self.create_banner_from_image(b'', title, subtitle, cta)

    def create_banner_from_image(self, image_bytes: bytes, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        """Принимает байты изображения и накладывает текст."""
        if not image_bytes:
            # Если нет изображения, создаём заглушку
            img = Image.new('RGB', (1024, 1024), color='#0a0a2e')
        else:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        draw = ImageDraw.Draw(img)

        width, height = img.size

        # Загружаем шрифты
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/14))
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height/20))
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/16))
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Полупрозрачный чёрный оверлей внизу
        overlay = Image.new('RGBA', (width, height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(height//2, height):
            alpha = int(180 * (1 - (y - height//2) / (height//2)))
            overlay_draw.rectangle((0, y, width, y+1), fill=(0,0,0,alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

        y_offset = height - 120
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= int(height/12)

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= int(height/15)

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            x = (width - tw) // 2
            draw.rectangle((x-30, y_offset-20, x+tw+30, y_offset+60), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        # Логотип вверху
        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/25))
            draw.text((30, 30), "AI Навигатор", fill='#FFFFFF', font=logo_font)
        except:
            pass

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
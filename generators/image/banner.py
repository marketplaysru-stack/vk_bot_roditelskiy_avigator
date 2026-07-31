"""generators/image/banner.py – генерация рекламных баннеров без внешних API"""
import io
import random
from PIL import Image, ImageDraw, ImageFont
from .base import ImageGenerator

class BannerGenerator(ImageGenerator):
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def generate(self, prompt: str = "", title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # Создаём изображение
        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # 1) Фон – градиент
        self._draw_gradient(draw)

        # 2) Геометрические фигуры (украшения)
        self._draw_shapes(draw)

        # 3) Иконки (Unicode)
        self._draw_icons(draw)

        # 4) Текст
        self._draw_text(draw, title, subtitle, cta)

        # Сохраняем
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _draw_gradient(self, draw):
        """Рисует градиентный фон."""
        # Создаём градиент от тёмно-синего к фиолетовому
        for y in range(self.height):
            r = int(10 + (y / self.height) * 40)
            g = int(20 + (y / self.height) * 60)
            b = int(60 + (y / self.height) * 120)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

    def _draw_shapes(self, draw):
        """Добавляет абстрактные фигуры (круги, линии)."""
        # Несколько кругов
        colors = ['#FFD700', '#00BFFF', '#FF6B6B', '#7B68EE']
        for _ in range(6):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(50, 150)
            color = random.choice(colors)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=3, fill=None)
            # Маленький залитый круг
            draw.ellipse((x-r//2, y-r//2, x+r//2, y+r//2), fill=color, outline=None)

    def _draw_icons(self, draw):
        """Рисует простые иконки из Unicode."""
        icons = ['⚙️', '📊', '🤖', '💡', '🚀', '🎯', '💎', '⚡', '📈', '🧠']
        font_size = 60
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Размещаем несколько иконок по углам
        positions = [
            (50, 50),
            (self.width-100, 50),
            (50, self.height-100),
            (self.width-100, self.height-100),
            (self.width//2-30, 100),
            (self.width//2-30, self.height-100)
        ]
        for i, pos in enumerate(positions):
            icon = random.choice(icons)
            draw.text(pos, icon, fill='#FFFFFF', font=font)

    def _draw_text(self, draw, title, subtitle, cta):
        """Накладывает текст поверх изображения."""
        # Загружаем шрифты
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Рисуем тёмный полупрозрачный фон под текстом внизу
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(180 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        draw.bitmap((0,0), overlay, fill=None)

        # Позиционируем текст снизу
        y_offset = self.height - 120
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 80

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 70

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            # Кнопка
            draw.rectangle((x-30, y_offset-20, x+tw+30, y_offset+60), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        # Добавляем логотип вверху
        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        except:
            logo_font = ImageFont.load_default()
        draw.text((30, 30), "AI Навигатор", fill='#FFFFFF', font=logo_font)
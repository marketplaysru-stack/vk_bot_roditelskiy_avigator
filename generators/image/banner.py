"""generators/image/banner.py – генерация ярких рекламных баннеров без внешних API"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # Создаём изображение
        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # 1) Градиентный фон (несколько цветов)
        self._draw_gradient(draw)

        # 2) Яркие геометрические фигуры (круги, треугольники, линии)
        self._draw_shapes(draw)

        # 3) Множество иконок (Unicode)
        self._draw_icons(draw)

        # 4) Эффект свечения (полупрозрачные круги)
        self._draw_glows(draw)

        # 5) Текст с тенями
        self._draw_text(draw, title, subtitle, cta)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _draw_gradient(self, draw):
        # Сложный градиент от синего к фиолетовому с переходом
        for y in range(self.height):
            ratio = y / self.height
            r = int(20 + ratio * 40)
            g = int(10 + ratio * 30)
            b = int(80 + ratio * 100)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

    def _draw_shapes(self, draw):
        # Круги разных размеров и цветов
        colors = ['#FFD700', '#00BFFF', '#FF6B6B', '#7B68EE', '#32CD32', '#FF4500', '#FF1493', '#00FA9A']
        for _ in range(12):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(40, 180)
            color = random.choice(colors)
            # Контур
            draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=4, fill=None)
            # Залитый круг внутри
            r2 = r // 3
            draw.ellipse((x-r2, y-r2, x+r2, y+r2), fill=color, outline=None)

        # Линии (диагональные, волнистые – но здесь просто линии)
        for _ in range(8):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=random.choice(colors), width=5)

        # Треугольники (простые)
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(30, 100)
            color = random.choice(colors)
            draw.polygon([(x, y-size), (x-size, y+size), (x+size, y+size)], outline=color, width=3)

    def _draw_icons(self, draw):
        icons = ['⚙️', '📊', '🤖', '💡', '🚀', '🎯', '💎', '⚡', '📈', '🧠', '🏗️', '📚', '💰', '🌐', '🔧', '🛠️']
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
        except:
            font = ImageFont.load_default()

        positions = [
            (40, 40),
            (self.width-100, 40),
            (40, self.height-100),
            (self.width-100, self.height-100),
            (self.width//2-50, 60),
            (self.width//2-50, self.height-60),
            (100, self.height//2-40),
            (self.width-120, self.height//2-40)
        ]
        for pos in positions:
            icon = random.choice(icons)
            draw.text(pos, icon, fill='#FFFFFF', font=font)

    def _draw_glows(self, draw):
        # Полупрозрачные круги для эффекта свечения
        glows = [(255, 215, 0, 80), (0, 191, 255, 60), (255, 105, 180, 70)]
        for _ in range(6):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(100, 250)
            color = random.choice(glows)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=color, outline=None)

    def _draw_text(self, draw, title, subtitle, cta):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Тёмный оверлей снизу (для читаемости текста)
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(220 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        img = Image.new('RGB', (self.width, self.height))
        img.paste(overlay, (0,0), overlay)
        draw = ImageDraw.Draw(img)

        y_offset = self.height - 150

        # Заголовок (с тенью)
        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            # Тень
            draw.text((x+4, y_offset+4), title, fill='black', font=font_title)
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 100

        # Подзаголовок
        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+2, y_offset+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 90

        # Кнопка CTA
        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            # Фон кнопки с закруглениями (имитация)
            draw.rectangle((x-40, y_offset-30, x+tw+40, y_offset+th+30), fill='#FFD700', outline=None)
            # Тень кнопки
            draw.rectangle((x-36, y_offset-26, x+tw+36, y_offset+th+26), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        # Логотип вверху
        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

        # Возвращаем изображение как байты
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
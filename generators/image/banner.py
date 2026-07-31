"""generators/image/banner.py – генерация рекламных баннеров с текстом"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "", category: str = "general") -> bytes:
        # Создаём холст
        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # Определяем тему
        theme = self._get_theme(category)

        # 1) Градиентный фон (из темы)
        self._draw_gradient(draw, theme)

        # 2) Геометрические фигуры (из темы)
        self._draw_shapes(draw, theme)

        # 3) Иконки (из темы)
        self._draw_icons(draw, theme)

        # 4) Свечение
        self._draw_glows(draw)

        # 5) Текст
        self._draw_text(draw, title, subtitle, cta)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _get_theme(self, category: str):
        themes = {
            "construction": {
                "colors": ['#FF8C00', '#1E90FF', '#FFD700', '#FFFFFF'],
                "icons": ['🏗️', '🚧', '🏠', '📐', '🔧', '⚙️', '🛠️', '🚜']
            },
            "business": {
                "colors": ['#FFD700', '#003366', '#FFFFFF', '#00CED1'],
                "icons": ['📈', '💰', '🤝', '🎯', '💼', '📊', '🔑']
            },
            "ai": {
                "colors": ['#6A0DAD', '#00FFFF', '#FF00FF', '#FFFFFF'],
                "icons": ['🤖', '🧠', '⚡', '💡', '🌐', '📡', '🔮']
            },
            "education": {
                "colors": ['#008080', '#FFD700', '#FFFFFF', '#32CD32'],
                "icons": ['📚', '🎓', '✏️', '📝', '🧪', '🔬', '🌍']
            },
            "general": {
                "colors": ['#1E90FF', '#FFD700', '#FFFFFF', '#FF69B4'],
                "icons": ['⚙️', '📊', '🤖', '💡', '🚀', '🎯', '💎']
            }
        }
        return themes.get(category, themes["general"])

    def _draw_gradient(self, draw, theme):
        c1 = self._hex_to_rgb(theme['colors'][0])
        c2 = self._hex_to_rgb(theme['colors'][1])
        for y in range(self.height):
            ratio = y / self.height
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

    def _draw_shapes(self, draw, theme):
        colors = theme['colors']
        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(40, 160)
            color = random.choice(colors)
            draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=4, fill=None)
            r2 = r // 3
            draw.ellipse((x-r2, y-r2, x+r2, y+r2), fill=color, outline=None)

    def _draw_icons(self, draw, theme):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
        except:
            font = ImageFont.load_default()
        icons = theme['icons']
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
        glows = ['#FFD70080', '#00BFFF80', '#FF6B6B80']
        for _ in range(6):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(100, 250)
            color = random.choice(glows)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=color, outline=None)

    def _draw_text(self, draw, title, subtitle, cta):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        # Полупрозрачный оверлей снизу
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(200 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        img = Image.new('RGB', (self.width, self.height))
        img.paste(overlay, (0,0), overlay)
        draw = ImageDraw.Draw(img)

        y_offset = self.height - 140

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+4, y_offset+4), title, fill='black', font=font_title)
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 90

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+2, y_offset+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 80

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            draw.rectangle((x-40, y_offset-30, x+tw+40, y_offset+th+30), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))
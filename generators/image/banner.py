"""generators/image/banner.py – создание баннеров с улучшенным дизайном"""
import io
import random
from PIL import Image, ImageDraw, ImageFont

class BannerGenerator:
    def __init__(self):
        self.width = 1024
        self.height = 1024

    def create_banner(self, title: str = "", subtitle: str = "", cta: str = "", category: str = "general", is_announce: bool = False) -> bytes:
        theme = self._get_theme(category)

        # Для анонсов – более яркая цветовая схема
        if is_announce:
            theme = self._get_announce_theme(category)

        img = Image.new('RGB', (self.width, self.height), color='#0a0a2e')
        draw = ImageDraw.Draw(img)

        # Фон
        self._draw_gradient(draw, theme)
        # Декоративные элементы (круги, линии)
        self._draw_decorations(draw, theme, is_announce)
        # Иконки (больше для анонсов)
        self._draw_icons(draw, theme, is_announce)
        # Полупрозрачный оверлей для текста
        self._draw_overlay(draw)
        # Текст
        self._draw_text(draw, title, subtitle, cta, theme, is_announce)
        # Рамка
        self._draw_frame(draw, theme)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def create_banner_from_image(self, image_bytes: bytes, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
        # (оставляем как было, для постов)
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        draw = ImageDraw.Draw(img)
        width, height = img.size
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/14))
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height/20))
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/16))
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        overlay = Image.new('RGBA', (width, height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(height//2, height):
            alpha = int(200 * (1 - (y - height//2) / (height//2)))
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

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    # ---- Тематические схемы ----
    def _get_theme(self, category: str):
        themes = {
            "construction": {
                "colors": ['#FF8C00', '#1E90FF', '#FFD700', '#FFFFFF'],
                "icons": ['🏗️', '🚧', '📐', '🔧', '⚙️'],
                "gradient": ('#1a1a2e', '#16213e', '#0f3460')
            },
            "business": {
                "colors": ['#FFD700', '#003366', '#FFFFFF', '#00CED1'],
                "icons": ['📈', '💰', '🤝', '🎯', '💼'],
                "gradient": ('#0d1b2a', '#1b263b', '#415a77')
            },
            "ai": {
                "colors": ['#6A0DAD', '#00FFFF', '#FF00FF', '#FFFFFF'],
                "icons": ['🤖', '🧠', '⚡', '💡', '🌐'],
                "gradient": ('#0a0a2e', '#1a0a3e', '#2d1b69')
            },
            "general": {
                "colors": ['#1E90FF', '#FFD700', '#FFFFFF', '#FF69B4'],
                "icons": ['⚙️', '📊', '💡', '🚀', '🎯'],
                "gradient": ('#0a0a2e', '#1a1a4e', '#2a2a6e')
            }
        }
        return themes.get(category, themes["general"])

    def _get_announce_theme(self, category: str):
        # Более яркие цвета для анонсов
        themes = {
            "construction": {
                "colors": ['#FF4500', '#00BFFF', '#FFD700', '#FFFFFF'],
                "icons": ['🏗️', '🚧', '📐', '🔧', '⚙️'],
                "gradient": ('#2d0a00', '#4a1a00', '#6b2a00')
            },
            "business": {
                "colors": ['#FFD700', '#00CED1', '#FFFFFF', '#FF4500'],
                "icons": ['📈', '💰', '🤝', '🎯', '💼'],
                "gradient": ('#002244', '#003366', '#004488')
            },
            "ai": {
                "colors": ['#FF00FF', '#00FFFF', '#FFFFFF', '#FFD700'],
                "icons": ['🤖', '🧠', '⚡', '💡', '🌐'],
                "gradient": ('#1a0033', '#2d0055', '#3d0077')
            },
            "general": {
                "colors": ['#FF69B4', '#1E90FF', '#FFD700', '#FFFFFF'],
                "icons": ['⚙️', '📊', '💡', '🚀', '🎯'],
                "gradient": ('#1a0a2e', '#2d1a4e', '#3d2a6e')
            }
        }
        return themes.get(category, themes["general"])

    # ---- Вспомогательные методы рисования ----
    def _draw_gradient(self, draw, theme):
        c1 = self._hex_to_rgb(theme['gradient'][0])
        c2 = self._hex_to_rgb(theme['gradient'][1])
        c3 = self._hex_to_rgb(theme['gradient'][2])
        for y in range(self.height):
            ratio = y / self.height
            if ratio < 0.5:
                r = int(c1[0] + (c2[0] - c1[0]) * ratio * 2)
                g = int(c1[1] + (c2[1] - c1[1]) * ratio * 2)
                b = int(c1[2] + (c2[2] - c1[2]) * ratio * 2)
            else:
                r = int(c2[0] + (c3[0] - c2[0]) * (ratio - 0.5) * 2)
                g = int(c2[1] + (c3[1] - c2[1]) * (ratio - 0.5) * 2)
                b = int(c2[2] + (c3[2] - c2[2]) * (ratio - 0.5) * 2)
            draw.rectangle((0, y, self.width, y+1), fill=(r, g, b))

    def _draw_decorations(self, draw, theme, is_announce):
        colors = theme['colors']
        num_shapes = 15 if is_announce else 8
        for _ in range(num_shapes):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(40, 200)
            color = random.choice(colors)
            # Рисуем контур и заливку для яркости
            draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=6, fill=None)
            r2 = r // 3
            draw.ellipse((x-r2, y-r2, x+r2, y+r2), fill=color, outline=None)

        # Случайные линии
        for _ in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=random.choice(colors), width=8)

    def _draw_icons(self, draw, theme, is_announce):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 140 if is_announce else 100)
        except:
            font = ImageFont.load_default()
        icons = theme['icons']
        positions = [
            (80, 80),
            (self.width-180, 80),
            (80, self.height-180),
            (self.width-180, self.height-180),
            (self.width//2-80, 80),
            (self.width//2-80, self.height-150)
        ]
        for pos in positions:
            icon = random.choice(icons)
            draw.text(pos, icon, fill='#FFFFFF80', font=font)

    def _draw_overlay(self, draw):
        overlay = Image.new('RGBA', (self.width, self.height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(self.height//2, self.height):
            alpha = int(200 * (1 - (y - self.height//2) / (self.height//2)))
            overlay_draw.rectangle((0, y, self.width, y+1), fill=(0,0,0,alpha))
        img = Image.new('RGB', (self.width, self.height))
        img.paste(overlay, (0,0), overlay)
        draw.bitmap((0,0), img, fill=None)

    def _draw_text(self, draw, title, subtitle, cta, theme, is_announce):
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100 if is_announce else 80)
            font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 55 if is_announce else 45)
            font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65 if is_announce else 55)
        except:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_cta = ImageFont.load_default()

        y_offset = self.height - 160

        if title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+4, y_offset+4), title, fill='black', font=font_title)
            draw.text((x, y_offset), title, fill='white', font=font_title)
            y_offset -= 110

        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
            tw = bbox[2] - bbox[0]
            x = (self.width - tw) // 2
            draw.text((x+2, y_offset+2), subtitle, fill='black', font=font_sub)
            draw.text((x, y_offset), subtitle, fill='#FFD700', font=font_sub)
            y_offset -= 100

        if cta:
            bbox = draw.textbbox((0, 0), cta, font=font_cta)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            draw.rectangle((x-40, y_offset-30, x+tw+40, y_offset+th+30), fill='#FFD700', outline=None)
            draw.text((x, y_offset), cta, fill='#0a0a2e', font=font_cta)

        try:
            logo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
            draw.text((30, 30), "AI Навигатор", fill='white', font=logo_font)
        except:
            pass

    def _draw_frame(self, draw, theme):
        color = theme['colors'][1]
        draw.rectangle((10, 10, self.width-10, self.height-10), outline=color, width=8)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))
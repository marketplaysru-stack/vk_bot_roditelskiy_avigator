def create_banner_from_image(self, image_bytes: bytes, title: str = "", subtitle: str = "", cta: str = "") -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
    width, height = img.size
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/14))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height/20))
        font_cta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(height/16))
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_cta = ImageFont.load_default()

    # Полупрозрачный оверлей снизу
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y in range(height//2, height):
        alpha = int(200 * (1 - (y - height//2) / (height//2)))
        overlay_draw.rectangle((0, y, width, y+1), fill=(0,0,0,alpha))
    img = Image.alpha_composite(img, overlay)
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

    rgb_img = img.convert('RGB')
    buf = io.BytesIO()
    rgb_img.save(buf, format='PNG')
    return buf.getvalue()
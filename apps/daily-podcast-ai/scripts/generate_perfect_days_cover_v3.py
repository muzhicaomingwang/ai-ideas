#!/usr/bin/env python3
"""
《完美的日子》影评播客封面生成 v3
更大的字号，更清晰的布局
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random


def generate_cover():
    """生成封面"""
    size = (1400, 1400)

    # 温暖的米色渐变背景
    color_top = (245, 240, 230)
    color_bottom = (220, 205, 185)

    img = Image.new("RGB", size, color_top)
    draw = ImageDraw.Draw(img)

    # 渐变
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        draw.rectangle([(0, y), (size[0], y + 1)], fill=(r, g, b))

    # 纹理
    random.seed(42)
    for _ in range(3000):
        x = random.randint(0, size[0] - 1)
        y = random.randint(0, size[1] - 1)
        brightness = random.randint(-5, 5)
        pixel = img.getpixel((x, y))
        new_pixel = tuple(max(0, min(255, p + brightness)) for p in pixel)
        img.putpixel((x, y), new_pixel)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    draw = ImageDraw.Draw(img)

    # 装饰线
    line_color = (180, 150, 120)
    draw.rectangle([(100, 120), (1300, 124)], fill=line_color)
    draw.rectangle([(100, 1276), (1300, 1280)], fill=line_color)

    # 光斑效果
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for _ in range(20):
        x = random.randint(300, 1100)
        y = random.randint(550, 850)
        radius = random.randint(40, 120)
        alpha = random.randint(20, 60)
        overlay_draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill=(255, 250, 235, alpha)
        )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 加载字体
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 1)
    title_font = font.font_variant(size=140)
    subtitle_font = font.font_variant(size=70)
    info_font = font.font_variant(size=52)

    text_color = (60, 50, 40)

    # 主标题
    title = "《完美的日子》"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x + 2, 202), title, fill=(200, 190, 175), font=title_font)
    draw.text((x, 200), title, fill=text_color, font=title_font)

    # 英文标题
    en_title = "Perfect Days"
    bbox = draw.textbbox((0, 0), en_title, font=subtitle_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, 360), en_title, fill=(120, 100, 80), font=subtitle_font)

    # 副标题
    subtitle = "深度影评播客"
    bbox = draw.textbbox((0, 0), subtitle, font=info_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, 460), subtitle, fill=(140, 120, 100), font=info_font)

    # 信息区域（更大字号）
    info_y = 1030
    line_spacing = 70

    # 导演
    director = "导演: 维姆·文德斯 (Wim Wenders)"
    bbox = draw.textbbox((0, 0), director, font=info_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, info_y), director, fill=(100, 85, 70), font=info_font)

    # 主演（使用更大字号确保清晰）
    actor = "主演: 役所广司"
    bbox = draw.textbbox((0, 0), actor, font=info_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, info_y + line_spacing), actor, fill=(100, 85, 70), font=info_font)

    # 时长
    duration = "36分钟 · 18个章节"
    bbox = draw.textbbox((0, 0), duration, font=info_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, info_y + line_spacing * 2), duration, fill=(140, 120, 100), font=info_font)

    # 背景音乐
    music_credit = "背景音乐作曲: 王植萌"
    small_font = font.font_variant(size=36)
    bbox = draw.textbbox((0, 0), music_credit, font=small_font)
    w = bbox[2] - bbox[0]
    x = (size[0] - w) // 2
    draw.text((x, info_y + line_spacing * 3 + 20), music_credit, fill=(120, 100, 80), font=small_font)

    # Logo
    logo_path = "logo/王植萌漫画形象.png"
    if Path(logo_path).exists():
        try:
            logo = Image.open(logo_path)
            logo_size = (180, 180)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
            logo_x = size[0] - logo_size[0] - 80
            logo_y = 1100
            if logo.mode == "RGBA":
                img.paste(logo, (logo_x, logo_y), logo)
            else:
                img.paste(logo, (logo_x, logo_y))
        except:
            pass

    # 保存
    output_path = "output/2026-01-08/cover-perfect-days-final.png"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)

    print(f"✅ 封面生成完成: {output_path}")
    return output_path


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🎬 《完美的日子》封面生成器 v3")
    print("=" * 50 + "\n")
    generate_cover()
    print("\n✅ 完成!")

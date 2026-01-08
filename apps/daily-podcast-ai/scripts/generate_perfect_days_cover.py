#!/usr/bin/env python3
"""
《完美的日子》影评播客封面生成
设计理念：简约、温暖、日系美学
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def create_gradient_background(size, color_top, color_bottom):
    """创建渐变背景"""
    img = Image.new("RGB", size, color_top)
    draw = ImageDraw.Draw(img)

    # 从上到下的渐变
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        draw.rectangle([(0, y), (size[0], y + 1)], fill=(r, g, b))

    return img


def generate_perfect_days_cover(
    output_path: str,
    logo_path: str = None,
):
    """
    生成《完美的日子》影评播客封面

    设计元素：
    - 温暖的米色/咖啡色调（符合电影的侘寂美学）
    - 简约的排版（体现极简主义）
    - 光影元素（呼应电影中的树叶光影）
    """
    # 画布尺寸
    size = (1400, 1400)

    # 配色方案：温暖的米色到浅咖啡色渐变
    color_top = (245, 240, 230)      # 米白色
    color_bottom = (220, 205, 185)   # 浅咖啡色

    # 创建渐变背景
    img = create_gradient_background(size, color_top, color_bottom)
    draw = ImageDraw.Draw(img)

    # 添加纹理效果（模拟纸张质感）
    import random
    for _ in range(3000):
        x = random.randint(0, size[0] - 1)
        y = random.randint(0, size[1] - 1)
        brightness = random.randint(-5, 5)
        pixel = img.getpixel((x, y))
        new_pixel = tuple(max(0, min(255, p + brightness)) for p in pixel)
        img.putpixel((x, y), new_pixel)

    # 轻微模糊，让纹理更自然
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    draw = ImageDraw.Draw(img)

    # 添加装饰元素：顶部和底部的细线（日式简约风格）
    line_color = (180, 150, 120)  # 深咖啡色
    draw.rectangle([(100, 120), (1300, 124)], fill=line_color)
    draw.rectangle([(100, 1276), (1300, 1280)], fill=line_color)

    # 加载字体
    # 尝试多个字体路径，优先使用 Arial Unicode（对日文汉字支持最好）
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
    ]

    title_font = None
    for font_path in font_paths:
        try:
            if Path(font_path).exists():
                title_font = ImageFont.truetype(font_path, 140)
                subtitle_font = ImageFont.truetype(font_path, 70)
                info_font = ImageFont.truetype(font_path, 50)
                small_font = ImageFont.truetype(font_path, 38)
                print(f"✅ 已加载字体: {font_path}")
                break
        except Exception as e:
            continue

    if not title_font:
        print("⚠️ 未找到合适的中文字体，使用默认字体")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    text_color = (60, 50, 40)  # 深褐色，易读

    # 主标题：电影名称
    title_text = "《完美的日子》"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (size[0] - title_width) // 2
    title_y = 200

    # 标题阴影（轻微）
    shadow_color = (200, 190, 175)
    draw.text((title_x + 2, title_y + 2), title_text, fill=shadow_color, font=title_font)
    # 标题正文
    draw.text((title_x, title_y), title_text, fill=text_color, font=title_font)

    # 英文标题
    en_title = "Perfect Days"
    en_bbox = draw.textbbox((0, 0), en_title, font=subtitle_font)
    en_width = en_bbox[2] - en_bbox[0]
    en_x = (size[0] - en_width) // 2
    en_y = 350
    draw.text((en_x, en_y), en_title, fill=(120, 100, 80), font=subtitle_font)

    # 副标题：深度影评
    subtitle = "深度影评播客"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=info_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (size[0] - subtitle_width) // 2
    subtitle_y = 450
    draw.text((subtitle_x, subtitle_y), subtitle, fill=(140, 120, 100), font=info_font)

    # 导演信息
    director = "导演: 维姆·文德斯 (Wim Wenders)"
    director_bbox = draw.textbbox((0, 0), director, font=small_font)
    director_width = director_bbox[2] - director_bbox[0]
    director_x = (size[0] - director_width) // 2
    director_y = 1050
    draw.text((director_x, director_y), director, fill=(100, 85, 70), font=small_font)

    # 主演信息
    actor = "主演: 役所广司"
    actor_bbox = draw.textbbox((0, 0), actor, font=small_font)
    actor_width = actor_bbox[2] - actor_bbox[0]
    actor_x = (size[0] - actor_width) // 2
    actor_y = 1110
    draw.text((actor_x, actor_y), actor, fill=(100, 85, 70), font=small_font)

    # 时长信息
    duration = "36分钟 · 18个章节"
    duration_bbox = draw.textbbox((0, 0), duration, font=small_font)
    duration_width = duration_bbox[2] - duration_bbox[0]
    duration_x = (size[0] - duration_width) // 2
    duration_y = 1180
    draw.text((duration_x, duration_y), duration, fill=(140, 120, 100), font=small_font)

    # 添加装饰性元素：简约的树叶剪影（呼应电影中的意象）
    # 在中央区域绘制抽象的光影图案
    center_y = 650

    # 绘制几个简单的圆形，模拟光斑
    light_color = (255, 250, 240, 100)  # 半透明的暖白色
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # 光斑效果
    import random
    random.seed(42)  # 固定种子，保证每次生成相同
    for _ in range(20):
        x = random.randint(300, 1100)
        y = random.randint(550, 850)
        radius = random.randint(40, 120)
        alpha = random.randint(20, 60)
        overlay_draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill=(255, 250, 235, alpha)
        )

    # 应用高斯模糊，让光斑更柔和
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 添加 Logo（如果提供）
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path)
            # Logo 放在右下角，作为签名
            logo_size = (180, 180)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

            logo_x = size[0] - logo_size[0] - 80
            logo_y = 1150

            if logo.mode == "RGBA":
                img.paste(logo, (logo_x, logo_y), logo)
            else:
                img.paste(logo, (logo_x, logo_y))
        except Exception as e:
            print(f"⚠️ Logo 加载失败: {e}")

    # 保存图片
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_file, quality=95, optimize=True)

    print(f"✅ 封面生成完成: {output_file}")
    return str(output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="《完美的日子》播客封面生成器")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output/2026-01-08/cover-perfect-days-v2.png",
        help="输出文件路径"
    )
    parser.add_argument(
        "--logo", "-l",
        type=str,
        default="logo/王植萌漫画形象.png",
        help="Logo 图片路径"
    )

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("🎬 《完美的日子》封面生成器")
    print("=" * 50 + "\n")

    result = generate_perfect_days_cover(
        output_path=args.output,
        logo_path=args.logo,
    )

    if result:
        print("\n✅ 封面生成成功!")
        print(f"📁 {result}")
    else:
        print("\n❌ 封面生成失败")

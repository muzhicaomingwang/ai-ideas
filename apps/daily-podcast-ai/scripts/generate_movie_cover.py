#!/usr/bin/env python3
"""
电影影评播客封面生成脚本
专门为影评播客生成定制封面
"""

import sys
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def generate_movie_cover(
    movie_title: str,
    output_path: str,
    logo_path: str = None,
    date_str: str = None,
):
    """
    生成电影影评播客封面

    Args:
        movie_title: 电影标题
        output_path: 输出文件路径
        logo_path: Logo 图片路径
        date_str: 日期字符串
    """
    # 画布尺寸（正方形，适合播客封面）
    size = (1400, 1400)

    # 创建渐变背景（深色调，符合《完美的日子》的氛围）
    img = Image.new("RGB", size, color="#1a1a1a")
    draw = ImageDraw.Draw(img)

    # 添加渐变效果（从深灰到黑）
    for y in range(size[1]):
        alpha = y / size[1]
        gray = int(26 * (1 - alpha * 0.5))  # 26 到 13
        color = (gray, gray, gray)
        draw.rectangle([(0, y), (size[0], y + 1)], fill=color)

    # 添加装饰线条（简约风格）
    draw.rectangle([(50, 50), (1350, 54)], fill="#d4af37")  # 金色线条
    draw.rectangle([(50, 1346), (1350, 1350)], fill="#d4af37")

    # 加载字体
    try:
        # 尝试加载系统中文字体
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 90)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 50)
        info_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
    except:
        # 回退到默认字体
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        info_font = ImageFont.load_default()

    # 绘制电影标题
    title_text = f"《{movie_title}》"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (size[0] - title_width) // 2
    title_y = 250

    # 标题阴影
    draw.text((title_x + 3, title_y + 3), title_text, fill="#000000", font=title_font)
    # 标题文字（金色）
    draw.text((title_x, title_y), title_text, fill="#d4af37", font=title_font)

    # 副标题
    subtitle = "深度影评播客"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (size[0] - subtitle_width) // 2
    subtitle_y = 400
    draw.text((subtitle_x, subtitle_y), subtitle, fill="#cccccc", font=subtitle_font)

    # 添加导演信息
    director = "维姆·文德斯 Wim Wenders"
    director_bbox = draw.textbbox((0, 0), director, font=info_font)
    director_width = director_bbox[2] - director_bbox[0]
    director_x = (size[0] - director_width) // 2
    director_y = 550
    draw.text((director_x, director_y), director, fill="#999999", font=info_font)

    # 添加时长信息
    if date_str:
        info_text = f"录制日期: {date_str}"
    else:
        info_text = "深度影评 · 约35分钟"

    info_bbox = draw.textbbox((0, 0), info_text, font=info_font)
    info_width = info_bbox[2] - info_bbox[0]
    info_x = (size[0] - info_width) // 2
    info_y = 1200
    draw.text((info_x, info_y), info_text, fill="#999999", font=info_font)

    # 添加 Logo（如果提供）
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path)
            # 调整 logo 大小
            logo_size = (300, 300)
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

            # 如果logo有透明通道，保持透明
            logo_x = (size[0] - logo_size[0]) // 2
            logo_y = 750

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

    parser = argparse.ArgumentParser(description="电影影评播客封面生成器")
    parser.add_argument("--title", "-t", type=str, default="完美的日子", help="电影标题")
    parser.add_argument("--output", "-o", type=str, required=True, help="输出文件路径")
    parser.add_argument("--logo", "-l", type=str, default=None, help="Logo 图片路径")
    parser.add_argument("--date", "-d", type=str, default=None, help="日期")

    args = parser.parse_args()

    if not args.date:
        args.date = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "=" * 50)
    print("🎬 电影影评播客封面生成器")
    print("=" * 50 + "\n")

    result = generate_movie_cover(
        movie_title=args.title,
        output_path=args.output,
        logo_path=args.logo,
        date_str=args.date
    )

    if result:
        print("\n✅ 封面生成成功!")
    else:
        print("\n❌ 封面生成失败")

#!/usr/bin/env python3
"""
播客封面图片生成器
使用 Pillow 生成简洁专业的播客封面
支持使用自定义logo替代程序化图标
"""

import argparse
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# 默认logo路径（相对于项目根目录）
DEFAULT_LOGO_PATH = "logo/王植萌漫画形象.png"


def get_chinese_weekday(date: datetime) -> str:
    """获取中文星期"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[date.weekday()]


def load_and_resize_logo(logo_path: str, target_size: int = 400) -> Image.Image:
    """
    加载并调整logo大小

    Args:
        logo_path: logo文件路径
        target_size: 目标尺寸（正方形边长）

    Returns:
        调整大小后的logo图片（RGBA模式）
    """
    logo = Image.open(logo_path)
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # 保持宽高比缩放
    logo.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
    return logo


def create_circular_mask(size: int) -> Image.Image:
    """创建圆形蒙版"""
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size, size], fill=255)
    return mask


# 定义多套颜色方案
COLOR_SCHEMES = {
    "ai": {  # AI/人工智能主题
        "primary": (88, 24, 92),      # 深紫
        "secondary": (140, 45, 145),   # 中紫
        "accent": (200, 100, 255),     # 亮紫
        "light": (220, 200, 255)
    },
    "tech": {  # 通用科技主题（默认）
        "primary": (24, 52, 92),       # 深蓝
        "secondary": (45, 85, 140),    # 中蓝
        "accent": (100, 180, 255),     # 亮蓝
        "light": (200, 220, 255)
    },
    "hardware": {  # 硬件/制造主题
        "primary": (60, 60, 60),       # 深灰
        "secondary": (100, 100, 100),  # 中灰
        "accent": (180, 180, 200),     # 亮灰
        "light": (220, 220, 235)
    },
    "business": {  # 商业/金融主题
        "primary": (92, 52, 24),       # 深橙
        "secondary": (140, 85, 45),    # 中橙
        "accent": (255, 150, 80),      # 亮橙
        "light": (255, 220, 200)
    },
    "green": {  # 新能源/环保主题
        "primary": (24, 70, 40),       # 深绿
        "secondary": (45, 110, 65),    # 中绿
        "accent": (100, 200, 130),     # 亮绿
        "light": (200, 240, 220)
    }
}


def detect_theme_from_categories(categories: dict) -> str:
    """
    根据新闻类别分布检测主题

    Args:
        categories: 类别统计字典 {"ai": 5, "hardware": 2, ...}

    Returns:
        主题名称（对应 COLOR_SCHEMES 的key）
    """
    if not categories:
        return "tech"

    # 按优先级检测关键词
    if categories.get("ai", 0) >= 3:
        return "ai"
    elif categories.get("hardware", 0) >= 3 or categories.get("chip", 0) >= 2:
        return "hardware"
    elif categories.get("business", 0) >= 4:
        return "business"
    elif categories.get("green", 0) >= 2:
        return "green"
    else:
        return "tech"  # 默认科技蓝


def create_gradient_background(width: int, height: int, color1: tuple, color2: tuple) -> Image.Image:
    """创建渐变背景"""
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))

    for y in range(height):
        # 对角渐变
        for x in range(width):
            # 计算渐变值 (0-255)
            gradient_val = int(255 * ((x + y) / (width + height)))
            mask.putpixel((x, y), gradient_val)

    base.paste(top, mask=mask)
    return base


def draw_decorative_elements(draw: ImageDraw.Draw, width: int, height: int):
    """绘制装饰元素"""
    # 右上角装饰圆
    draw.ellipse(
        [width - 200, -100, width + 100, 200],
        fill=(255, 255, 255, 30)
    )

    # 左下角装饰圆
    draw.ellipse(
        [-150, height - 250, 150, height + 50],
        fill=(255, 255, 255, 20)
    )

    # 细线装饰
    for i in range(3):
        y = 180 + i * 8
        draw.line([(50, y), (200, y)], fill=(255, 255, 255, 100), width=2)


def generate_cover(
    date: datetime,
    output_path: str,
    title: str = "今日科技早报",
    article_count: int = 10,
    width: int = 1400,
    height: int = 1400,
    logo_path: str = None,
    theme: str = None,
    category_stats: dict = None
) -> str:
    """
    生成播客封面图片

    Args:
        date: 播客日期
        output_path: 输出路径
        title: 播客标题
        article_count: 新闻数量
        width: 图片宽度
        height: 图片高度
        logo_path: 自定义logo路径
        theme: 主题名称（ai/tech/hardware/business/green）
        category_stats: 类别统计字典，用于自动检测主题

    Returns:
        生成的图片路径
    """
    # 如果提供了类别统计，自动检测主题
    if category_stats and not theme:
        theme = detect_theme_from_categories(category_stats)
        print(f"  🎨 根据新闻内容检测到主题: {theme}")

    # 选择颜色方案
    theme = theme or "tech"  # 默认科技蓝
    scheme = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["tech"])
    color_primary = scheme["primary"]
    color_secondary = scheme["secondary"]
    color_accent = scheme["accent"]
    color_light = scheme["light"]
    color_white = (255, 255, 255)

    # 创建渐变背景
    img = create_gradient_background(width, height, color_primary, color_secondary)
    draw = ImageDraw.Draw(img, "RGBA")

    # 绘制装饰元素
    draw_decorative_elements(draw, width, height)

    # 尝试加载字体（macOS 系统字体）
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]

    title_font = None
    date_font = None
    small_font = None

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                title_font = ImageFont.truetype(font_path, 120)
                date_font = ImageFont.truetype(font_path, 72)
                small_font = ImageFont.truetype(font_path, 48)
                break
            except Exception:
                continue

    # 如果没有找到中文字体，使用默认字体
    if title_font is None:
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 绘制 Logo 或麦克风图标
    logo_center_x = width // 2
    logo_center_y = 350

    # 解析 logo 路径
    actual_logo_path = logo_path
    if actual_logo_path is None:
        # 尝试使用默认 logo
        project_root = Path(__file__).parent.parent
        default_path = project_root / DEFAULT_LOGO_PATH
        if default_path.exists():
            actual_logo_path = str(default_path)

    if actual_logo_path and Path(actual_logo_path).exists():
        # 使用自定义 logo
        logo_size = 350  # logo 大小
        logo = load_and_resize_logo(actual_logo_path, logo_size)

        # 计算 logo 位置（居中）
        logo_x = logo_center_x - logo.width // 2
        logo_y = logo_center_y - logo.height // 2

        # 将 logo 合成到封面上（保留透明度）
        if logo.mode == 'RGBA':
            img.paste(logo, (logo_x, logo_y), logo)
        else:
            img.paste(logo, (logo_x, logo_y))
    else:
        # 回退：绘制麦克风图标
        mic_width = 120
        mic_height = 180
        draw.rounded_rectangle(
            [logo_center_x - mic_width//2, logo_center_y - mic_height//2,
             logo_center_x + mic_width//2, logo_center_y + mic_height//2],
            radius=60,
            fill=color_accent
        )

        # 麦克风支架
        draw.arc(
            [logo_center_x - 80, logo_center_y + 20,
             logo_center_x + 80, logo_center_y + 160],
            start=0, end=180,
            fill=color_accent,
            width=8
        )
        draw.line(
            [(logo_center_x, logo_center_y + 140), (logo_center_x, logo_center_y + 200)],
            fill=color_accent,
            width=8
        )
        draw.line(
            [(logo_center_x - 50, logo_center_y + 200), (logo_center_x + 50, logo_center_y + 200)],
            fill=color_accent,
            width=8
        )

        # 声波效果
        for i, offset in enumerate([100, 140, 180]):
            alpha = 200 - i * 50
            draw.arc(
                [logo_center_x - offset, logo_center_y - 60,
                 logo_center_x - offset + 40, logo_center_y + 60],
                start=120, end=240,
                fill=(color_accent[0], color_accent[1], color_accent[2], alpha),
                width=4
            )
            draw.arc(
                [logo_center_x + offset - 40, logo_center_y - 60,
                 logo_center_x + offset, logo_center_y + 60],
                start=-60, end=60,
                fill=(color_accent[0], color_accent[1], color_accent[2], alpha),
                width=4
            )

    # 绘制标题
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(
        ((width - title_width) // 2, 550),
        title,
        font=title_font,
        fill=color_white
    )

    # 绘制日期
    date_str = date.strftime("%Y年%m月%d日")
    weekday = get_chinese_weekday(date)
    full_date = f"{date_str} {weekday}"

    date_bbox = draw.textbbox((0, 0), full_date, font=date_font)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text(
        ((width - date_width) // 2, 720),
        full_date,
        font=date_font,
        fill=color_light
    )

    # 绘制分隔线
    line_y = 850
    line_width = 400
    draw.line(
        [(width//2 - line_width//2, line_y), (width//2 + line_width//2, line_y)],
        fill=color_accent,
        width=3
    )

    # 绘制新闻数量标签
    count_text = f"精选 {article_count} 条科技资讯"
    count_bbox = draw.textbbox((0, 0), count_text, font=small_font)
    count_width = count_bbox[2] - count_bbox[0]
    draw.text(
        ((width - count_width) // 2, 920),
        count_text,
        font=small_font,
        fill=color_light
    )

    # 绘制底部标语
    slogan = "AI 驱动 · 每日更新"
    slogan_bbox = draw.textbbox((0, 0), slogan, font=small_font)
    slogan_width = slogan_bbox[2] - slogan_bbox[0]
    draw.text(
        ((width - slogan_width) // 2, 1250),
        slogan,
        font=small_font,
        fill=(color_light[0], color_light[1], color_light[2], 180)
    )

    # 保存图片
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_file), "PNG", quality=95)

    return str(output_file)


def main():
    parser = argparse.ArgumentParser(description="生成播客封面图片")
    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="日期 (格式: YYYY-MM-DD，默认为今天)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出路径"
    )
    parser.add_argument(
        "--title", "-t",
        type=str,
        default="今日科技早报",
        help="播客标题"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="新闻数量"
    )
    parser.add_argument(
        "--logo", "-l",
        type=str,
        default=None,
        help="自定义logo路径 (默认使用 logo/王植萌漫画形象.png)"
    )

    args = parser.parse_args()

    # 解析日期
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_date = datetime.now()

    date_str = target_date.strftime("%Y-%m-%d")

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = f"output/{date_str}/cover-{date_str}.png"

    print(f"🎨 生成播客封面...")
    print(f"   日期: {date_str}")
    print(f"   标题: {args.title}")
    print(f"   新闻数: {args.count}")

    result = generate_cover(
        date=target_date,
        output_path=output_path,
        title=args.title,
        article_count=args.count,
        logo_path=args.logo
    )

    print(f"✅ 封面已生成: {result}")
    return result


if __name__ == "__main__":
    main()

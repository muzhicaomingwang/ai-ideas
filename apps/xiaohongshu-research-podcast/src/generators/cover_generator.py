"""
播客封面生成器 - 小红书主题设计
基于 daily-podcast-ai/scripts/generate_cover.py 改造
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..utils.logger import get_logger

logger = get_logger()


class CoverGenerator:
    """小红书研究播客封面生成器"""

    # 小红书品牌色
    XHS_RED_PRIMARY = (255, 36, 66)  # #FF2442
    XHS_RED_DARK = (204, 26, 53)  # #CC1A35
    XHS_RED_LIGHT = (255, 102, 130)  # #FF6682

    # 辅助色
    WHITE = (255, 255, 255)
    CARD_WHITE = (255, 255, 255, 230)  # 半透明白色
    TEXT_DARK = (51, 51, 51)  # #333333
    TEXT_GRAY = (102, 102, 102)  # #666666

    def __init__(self, width: int = 1400, height: int = 1400):
        """
        初始化

        Args:
            width: 封面宽度
            height: 封面高度
        """
        self.width = width
        self.height = height

        # 加载字体
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> dict:
        """加载字体"""
        fonts = {}

        # 字体路径候选列表
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]

        # 尝试加载
        for path in font_paths:
            if Path(path).exists():
                try:
                    fonts["title"] = ImageFont.truetype(path, 80)
                    fonts["topic"] = ImageFont.truetype(path, 50)
                    fonts["stats"] = ImageFont.truetype(path, 45)
                    fonts["date"] = ImageFont.truetype(path, 55)
                    logger.info(f"使用字体: {path}")
                    break
                except Exception as e:
                    logger.warning(f"加载字体失败 ({path}): {e}")
                    continue

        # 如果都失败，使用默认字体
        if not fonts:
            logger.warning("使用默认字体（可能不支持中文）")
            fonts["title"] = ImageFont.load_default()
            fonts["topic"] = ImageFont.load_default()
            fonts["stats"] = ImageFont.load_default()
            fonts["date"] = ImageFont.load_default()

        return fonts

    def generate(
        self,
        date: datetime,
        top_topics: list[str],
        stats: dict,
        output_path: str,
    ) -> str:
        """
        生成封面

        Args:
            date: 日期
            top_topics: Top 3话题标题列表
            stats: 统计数据，格式: {"total": 50, "top_category": "美妆", "trend": "+35%"}
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        logger.info("开始生成封面...")

        # 1. 创建渐变背景
        img = self._create_gradient_background()
        draw = ImageDraw.Draw(img, "RGBA")

        # 2. 绘制顶部标题区域
        self._draw_header(draw)

        # 3. 绘制中间白色卡片
        self._draw_content_card(draw, top_topics)

        # 4. 绘制底部统计信息
        self._draw_stats(draw, stats)

        # 5. 绘制底部日期
        self._draw_date(draw, date)

        # 6. 保存
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_file, quality=95)

        logger.info(f"封面生成完成: {output_path}")
        return str(output_file)

    def _create_gradient_background(self) -> Image.Image:
        """创建小红书红渐变背景"""
        # 创建基础图像
        img = Image.new("RGB", (self.width, self.height), self.XHS_RED_PRIMARY)
        overlay = Image.new("RGB", (self.width, self.height), self.XHS_RED_DARK)

        # 创建对角渐变蒙版
        mask = Image.new("L", (self.width, self.height))
        mask_draw = ImageDraw.Draw(mask)

        # 对角渐变（左上到右下）
        for y in range(self.height):
            for x in range(self.width):
                # 计算渐变值（0-255）
                gradient_val = int(255 * ((x + y) / (self.width + self.height)))
                mask.putpixel((x, y), gradient_val)

        # 应用蒙版
        img.paste(overlay, mask=mask)

        return img

    def _draw_header(self, draw: ImageDraw.Draw):
        """绘制顶部标题"""
        # 标题文字
        title = "每日小红书研究"
        title_font = self.fonts["title"]

        # 计算居中位置
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]

        x = (self.width - text_width) // 2
        y = 100

        # 添加文字阴影效果
        shadow_offset = 3
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            title,
            font=title_font,
            fill=(0, 0, 0, 100),
        )

        # 主文字（白色）
        draw.text((x, y), title, font=title_font, fill=self.WHITE)

    def _draw_content_card(self, draw: ImageDraw.Draw, top_topics: list[str]):
        """绘制中间白色卡片区域"""
        # 卡片位置
        card_left = 100
        card_top = 250
        card_right = self.width - 100
        card_bottom = 1000

        # 绘制圆角矩形（白色半透明）
        draw.rounded_rectangle(
            [(card_left, card_top), (card_right, card_bottom)],
            radius=30,
            fill=self.CARD_WHITE,
        )

        # 绘制"Top话题"标签
        label_text = "🔥 Top 3 话题"
        topic_font = self.fonts["topic"]

        draw.text(
            (card_left + 50, card_top + 40),
            label_text,
            font=topic_font,
            fill=self.XHS_RED_PRIMARY,
        )

        # 绘制Top 3话题
        y_offset = card_top + 120
        for i, topic in enumerate(top_topics[:3], 1):
            # 截断标题（最多18个字符）
            topic_text = topic[:18] + "..." if len(topic) > 18 else topic
            text = f"{i}. {topic_text}"

            draw.text(
                (card_left + 50, y_offset),
                text,
                font=topic_font,
                fill=self.TEXT_DARK,
            )
            y_offset += 100

        # 分隔线
        divider_y = card_bottom - 200
        draw.line(
            [(card_left + 50, divider_y), (card_right - 50, divider_y)],
            fill=self.TEXT_GRAY,
            width=2,
        )

    def _draw_stats(self, draw: ImageDraw.Draw, stats: dict):
        """绘制统计信息"""
        stats_font = self.fonts["stats"]
        card_left = 100
        y = 820

        # 话题总数
        total_text = f"📊 {stats.get('total', 0)}个热门话题"
        draw.text((card_left + 50, y), total_text, font=stats_font, fill=self.TEXT_GRAY)

        # 分类趋势
        trend_text = f"📈 {stats.get('top_category', '')}类热度{stats.get('trend', '')}"
        draw.text(
            (card_left + 50, y + 70), trend_text, font=stats_font, fill=self.XHS_RED_PRIMARY
        )

    def _draw_date(self, draw: ImageDraw.Draw, date: datetime):
        """绘制日期"""
        # 日期文字
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        date_str = date.strftime("%Y-%m-%d")
        weekday_str = weekdays[date.weekday()]
        full_date = f"{date_str}  {weekday_str}"

        date_font = self.fonts["date"]

        # 计算居中位置
        bbox = draw.textbbox((0, 0), full_date, font=date_font)
        text_width = bbox[2] - bbox[0]

        x = (self.width - text_width) // 2
        y = 1250

        # 绘制日期（白色）
        draw.text((x, y), full_date, font=date_font, fill=self.WHITE)


def main():
    """测试入口"""
    from dotenv import load_dotenv

    load_dotenv()

    logger.info("🎨 Cover Generator 测试")
    logger.info("=" * 50)

    generator = CoverGenerator()

    # 测试数据
    test_date = datetime(2026, 1, 15)
    test_topics = ["早八人的护肤routine", "新年第一周减脂计划打卡", "通勤穿搭灵感分享"]
    test_stats = {"total": 50, "top_category": "美妆", "trend": "+35%"}

    output_path = "output/test_cover.png"

    # 生成封面
    result = generator.generate(
        date=test_date, top_topics=test_topics, stats=test_stats, output_path=output_path
    )

    logger.info(f"✅ 封面生成成功: {result}")


if __name__ == "__main__":
    main()

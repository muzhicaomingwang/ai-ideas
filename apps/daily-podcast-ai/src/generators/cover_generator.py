"""
播客封面生成器 - 使用 OpenAI DALL-E 生成播客封面图片
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml
from openai import OpenAI


@dataclass
class CoverConfig:
    """封面配置"""
    podcast_title: str = "今日科技早报"
    style: str = "modern tech"
    size: str = "1024x1024"
    output_dir: str = "output"
    filename_template: str = "cover-{date}.png"


class CoverGenerator:
    """播客封面生成器"""

    def __init__(self, config_path: str = None):
        """
        初始化封面生成器

        Args:
            config_path: 配置文件路径，默认为 config/cover.yaml
        """
        self.config = self._load_config(config_path)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _load_config(self, config_path: str = None) -> CoverConfig:
        """加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "cover.yaml"

        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return CoverConfig(
                    podcast_title=data.get("podcast_title", "今日科技早报"),
                    style=data.get("style", "modern tech"),
                    size=data.get("size", "1024x1024"),
                    output_dir=data.get("output_dir", "output"),
                    filename_template=data.get("filename_template", "cover-{date}.png"),
                )
        return CoverConfig()

    def _parse_script_metadata(self, script_path: str) -> dict:
        """
        从脚本文件中解析元数据

        Args:
            script_path: 脚本文件路径

        Returns:
            包含日期、文章数、分类等信息的字典
        """
        metadata = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": "",
            "article_count": 0,
            "categories": [],
            "headlines": [],
        }

        if not Path(script_path).exists():
            return metadata

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析日期
        date_match = re.search(r"\*\*日期\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
        if date_match:
            metadata["date"] = date_match.group(1)

        # 解析星期
        weekday_match = re.search(r"星期([一二三四五六日])", content)
        if weekday_match:
            metadata["weekday"] = f"星期{weekday_match.group(1)}"

        # 解析文章数
        count_match = re.search(r"\*\*文章数\*\*:\s*(\d+)", content)
        if count_match:
            metadata["article_count"] = int(count_match.group(1))

        # 解析分类
        cat_match = re.search(r"\*\*分类\*\*:\s*(.+)", content)
        if cat_match:
            metadata["categories"] = [c.strip() for c in cat_match.group(1).split(",")]

        # 提取新闻标题（前3条作为亮点）
        headlines = re.findall(r"###\s*\d+\.\s*(.+)", content)
        metadata["headlines"] = headlines[:3] if headlines else []

        return metadata

    def _build_prompt(self, metadata: dict) -> str:
        """
        构建 DALL-E 提示词

        Args:
            metadata: 脚本元数据

        Returns:
            DALL-E 提示词
        """
        date_str = metadata.get("date", "")
        weekday = metadata.get("weekday", "")
        categories = ", ".join(metadata.get("categories", ["科技"]))

        # 构建一个专业的科技播客封面提示词
        prompt = f"""Create a professional podcast cover image for a Chinese tech news podcast called "今日科技早报" (Today's Tech Morning News).

Design requirements:
- Modern, clean, minimalist style with a tech/digital aesthetic
- Color scheme: Deep blue (#1a365d) and electric blue (#3182ce) gradient background
- Add subtle circuit board patterns or digital wave elements in the background
- Include a stylized microphone or podcast icon
- Add abstract tech elements like floating data points, network nodes, or AI-inspired geometric shapes
- The overall mood should be professional, trustworthy, and forward-looking

Text to include (in Chinese):
- Main title: "今日科技早报" (large, prominent, white or light colored)
- Date: "{date_str} {weekday}" (smaller, below title)
- Tagline: "AI驱动的每日科技资讯" (small, at bottom)

Style: {self.config.style}, professional broadcast quality, suitable for podcast platforms like Apple Podcasts and Spotify.
Do NOT include any English text, only Chinese characters as specified above.
Aspect ratio: 1:1 (square format for podcast cover)"""

        return prompt

    def generate(
        self,
        script_path: str = None,
        output_path: str = None,
        date: str = None
    ) -> str:
        """
        生成播客封面

        Args:
            script_path: 脚本文件路径，用于提取元数据
            output_path: 输出文件路径，不指定则自动生成
            date: 日期字符串，格式 YYYY-MM-DD

        Returns:
            生成的封面文件路径
        """
        print("🎨 开始生成播客封面...")

        # 解析元数据
        if script_path:
            metadata = self._parse_script_metadata(script_path)
        else:
            metadata = {
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "weekday": "",
                "categories": ["科技"],
                "headlines": [],
            }
            # 计算星期
            if metadata["date"]:
                try:
                    dt = datetime.strptime(metadata["date"], "%Y-%m-%d")
                    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
                    metadata["weekday"] = weekdays[dt.weekday()]
                except ValueError:
                    pass

        print(f"📅 日期: {metadata['date']} {metadata.get('weekday', '')}")

        # 构建提示词
        prompt = self._build_prompt(metadata)
        print(f"📝 生成提示词完成")

        # 调用 DALL-E API
        print("🤖 调用 DALL-E 生成图片...")
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=self.config.size,
                quality="hd",
                n=1,
            )

            image_url = response.data[0].url
            print(f"✅ 图片生成成功")

            # 下载图片
            import urllib.request

            # 确定输出路径
            if output_path is None:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = self.config.filename_template.format(date=metadata["date"])
                output_path = output_dir / filename
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

            # 下载并保存图片
            print(f"💾 下载图片到: {output_path}")
            urllib.request.urlretrieve(image_url, str(output_path))

            print(f"✅ 封面保存成功: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"❌ 生成封面失败: {e}")
            raise

    def generate_for_date(self, date: str) -> str:
        """
        为指定日期生成封面

        Args:
            date: 日期字符串，格式 YYYY-MM-DD

        Returns:
            生成的封面文件路径
        """
        # 尝试查找对应的脚本文件
        script_paths = [
            Path(self.config.output_dir) / f"script-{date}.md",
            Path("podcast_output") / f"script-{date}.md",
        ]

        script_path = None
        for path in script_paths:
            if path.exists():
                script_path = str(path)
                break

        return self.generate(script_path=script_path, date=date)


def main():
    """测试封面生成"""
    from dotenv import load_dotenv
    load_dotenv()

    generator = CoverGenerator()

    # 生成今日封面
    today = datetime.now().strftime("%Y-%m-%d")
    cover_path = generator.generate_for_date(today)
    print(f"\n🎉 封面已生成: {cover_path}")


if __name__ == "__main__":
    main()

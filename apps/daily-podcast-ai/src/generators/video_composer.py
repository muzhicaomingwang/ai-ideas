"""
视频合成模块
将漫画帧和音频合成为完整视频，并添加字幕
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont


@dataclass
class VideoMetadata:
    """视频元数据"""
    filepath: str
    duration_seconds: float
    total_frames: int
    resolution: str
    fps: int
    has_subtitles: bool


class VideoComposer:
    """视频合成器"""

    def __init__(self, config_path: str = "config/comic.yaml"):
        """
        初始化视频合成器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.video_config = self.config.get("video", {})
        self.subtitle_config = self.video_config.get("subtitle", {})

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        path = Path(config_path)
        if not path.exists():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / config_path

        if not path.exists():
            return self._default_config()

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "video": {
                "fps": 24,
                "codec": "libx264",
                "bitrate": "5000k",
                "resolution": "1920x1080",
                "subtitle": {
                    "font_size": 48,
                    "font_color": [255, 255, 255],
                    "bg_color": [0, 0, 0, 180],
                    "position": "bottom",
                    "margin": 60
                }
            }
        }

    def add_subtitles_to_image(
        self,
        image_path: str,
        subtitle: str,
        output_path: str
    ) -> str:
        """
        在图像上渲染字幕

        Args:
            image_path: 原始图像路径
            subtitle: 字幕文本
            output_path: 输出路径

        Returns:
            带字幕的图像路径
        """
        # 如果没有字幕，直接复制原图
        if not subtitle or subtitle.strip() == "":
            import shutil
            shutil.copy(image_path, output_path)
            return output_path

        img = Image.open(image_path)

        # 如果图像有 alpha 通道，转换为 RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        draw = ImageDraw.Draw(img, 'RGBA')

        # 获取字幕配置
        font_size = self.subtitle_config.get("font_size", 48)
        font_color = tuple(self.subtitle_config.get("font_color", [255, 255, 255]))
        bg_color = tuple(self.subtitle_config.get("bg_color", [0, 0, 0, 180]))
        margin = self.subtitle_config.get("margin", 60)

        # 尝试加载中文字体
        font_path = self.subtitle_config.get("font_path")
        try:
            if font_path and Path(font_path).exists():
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试系统字体
                for fallback_font in [
                    "/System/Library/Fonts/PingFang.ttc",  # macOS
                    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
                    "C:\\Windows\\Fonts\\msyh.ttc"  # Windows
                ]:
                    if Path(fallback_font).exists():
                        font = ImageFont.truetype(fallback_font, font_size)
                        break
                else:
                    # 使用默认字体
                    font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # 自动换行处理
        max_width = img.width - 2 * margin
        lines = self._wrap_text(subtitle, font, max_width, draw)

        # 计算字幕总高度
        line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
        total_height = sum(line_heights) + (len(lines) - 1) * 10  # 行间距10px

        # 计算位置
        position_type = self.subtitle_config.get("position", "bottom")
        if position_type == "bottom":
            y_start = img.height - total_height - margin
        elif position_type == "top":
            y_start = margin
        else:  # middle
            y_start = (img.height - total_height) / 2

        # 绘制半透明背景
        padding = 20
        bg_rect = [
            margin - padding,
            y_start - padding,
            img.width - margin + padding,
            y_start + total_height + padding
        ]
        draw.rectangle(bg_rect, fill=bg_color)

        # 绘制每行文字
        current_y = y_start
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) / 2  # 居中

            draw.text((x, current_y), line, font=font, fill=font_color)
            current_y += bbox[3] + 10  # 行间距

        img.save(output_path)
        return output_path

    def _wrap_text(self, text: str, font, max_width: int, draw) -> List[str]:
        """
        文本自动换行

        Args:
            text: 原始文本
            font: 字体对象
            max_width: 最大宽度
            draw: ImageDraw 对象

        Returns:
            分行后的文本列表
        """
        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def compose_video(
        self,
        frames: List,  # List[ComicFrame]
        audio_segments: List,  # List[AudioSegment]
        output_path: str,
        add_subtitles: bool = True,
        show_progress: bool = True
    ) -> Optional[VideoMetadata]:
        """
        将图像帧和音频合成为视频

        Args:
            frames: ComicFrame 列表
            audio_segments: AudioSegment 列表
            output_path: 输出路径
            add_subtitles: 是否添加字幕
            show_progress: 是否显示进度

        Returns:
            VideoMetadata 对象
        """
        if not frames or not audio_segments:
            print("❌ 缺少图像帧或音频片段")
            return None

        if len(frames) != len(audio_segments):
            print("⚠️ 图像帧和音频片段数量不匹配，将只处理较短的那个")
            min_len = min(len(frames), len(audio_segments))
            frames = frames[:min_len]
            audio_segments = audio_segments[:min_len]

        if show_progress:
            print(f"\n🎬 开始合成视频，共 {len(frames)} 个片段")
            print("-" * 40)

        # 创建临时目录
        temp_dir = Path(output_path).parent / "temp_subtitled"
        temp_dir.mkdir(parents=True, exist_ok=True)

        clips = []
        total_duration = 0

        for i, (frame, audio) in enumerate(zip(frames, audio_segments)):
            if show_progress:
                print(f"  [{i + 1}/{len(frames)}] 处理片段 {i}...")

            # 添加字幕
            if add_subtitles and frame.dialogue:
                subtitled_image = str(temp_dir / f"frame_{i:03d}_sub.png")
                self.add_subtitles_to_image(
                    frame.image_path,
                    frame.dialogue,
                    subtitled_image
                )
            else:
                subtitled_image = frame.image_path

            # 创建图像片段
            img_clip = ImageClip(subtitled_image, duration=audio.duration_seconds)

            # 添加音频
            if Path(audio.filepath).exists():
                audio_clip = AudioFileClip(audio.filepath)
                img_clip = img_clip.with_audio(audio_clip)

            clips.append(img_clip)
            total_duration += audio.duration_seconds

        if show_progress:
            print(f"\n  🔗 拼接 {len(clips)} 个视频片段...")

        # 拼接所有片段
        final_video = concatenate_videoclips(clips, method="compose")

        # 导出视频
        if show_progress:
            print(f"  💾 导出视频: {output_path}")

        fps = self.video_config.get("fps", 24)
        codec = self.video_config.get("codec", "libx264")
        bitrate = self.video_config.get("bitrate", "5000k")

        final_video.write_videofile(
            output_path,
            fps=fps,
            codec=codec,
            bitrate=bitrate,
            audio_codec="aac",
            logger=None if not show_progress else 'bar'
        )

        # 清理临时文件
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        # 关闭所有clips释放资源
        for clip in clips:
            clip.close()
        final_video.close()

        if show_progress:
            print("-" * 40)
            print(f"✅ 视频合成完成!")

        return VideoMetadata(
            filepath=output_path,
            duration_seconds=total_duration,
            total_frames=len(frames),
            resolution=self.video_config.get("resolution", "1920x1080"),
            fps=fps,
            has_subtitles=add_subtitles
        )


def main():
    """测试入口"""
    print("🎬 Video Composer 测试")
    print("=" * 50)

    # 检查是否有测试文件
    test_frames_dir = Path("output/frames")
    test_audio_dir = Path("output/audio")

    if not test_frames_dir.exists() or not test_audio_dir.exists():
        print("⚠️ 请先运行 nano_banana_generator.py 和 tts_generator.py 生成测试素材")
        return

    print("✅ 测试准备完成")
    print("💡 请使用完整的 generate_comic_drama.py 脚本进行测试")


if __name__ == "__main__":
    main()

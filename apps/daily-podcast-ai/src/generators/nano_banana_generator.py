"""
Nano Banana 图像生成模块
使用 Google Gemini API 生成漫画风格图像
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml
from google import genai
from google.genai import types


@dataclass
class ComicFrame:
    """漫画帧"""
    frame_index: int
    image_path: str
    description: str
    duration_seconds: float
    dialogue: str


class NanoBananaGenerator:
    """Nano Banana 图像生成器"""

    def __init__(self, config_path: str = "config/comic.yaml"):
        """
        初始化生成器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.image_config = self.config.get("image_generation", {})

        # 初始化 Gemini 客户端
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("未设置 GOOGLE_API_KEY 环境变量")

        self.client = genai.Client(api_key=api_key)

        # 获取配置
        self.model = self.image_config.get("model", "gemini-2.5-flash-image")
        self.aspect_ratio = self.image_config.get("aspect_ratio", "16:9")
        self.person_generation = self.image_config.get("person_generation", "allow_adult")
        self.style = self.image_config.get("style", "comic")

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
            "image_generation": {
                "model": "gemini-2.5-flash-image",
                "aspect_ratio": "16:9",
                "person_generation": "allow_adult",
                "style": "comic",
                "output_format": "png"
            }
        }

    def generate_frame(
        self,
        description: str,
        output_path: str,
        reference_images: Optional[List[str]] = None,
        character_consistency: bool = True
    ) -> Optional[str]:
        """
        生成单个漫画帧

        Args:
            description: 场景描述
            output_path: 输出路径
            reference_images: 参考图像路径列表（用于角色一致性）
            character_consistency: 是否保持角色一致性

        Returns:
            生成的图像路径，失败返回 None
        """
        try:
            # 构建提示词（加入风格控制）
            style_prompt = f"{self.style} style, high quality, detailed, vibrant colors"
            full_prompt = f"{description}. {style_prompt}"

            # 调用 Gemini API 生成图像
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )

            # 保存图像
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 从响应中提取图像
            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(str(output_file))
                    return str(output_file)

            print("❌ 未收到图像数据")
            return None

        except Exception as e:
            print(f"❌ 图像生成失败: {e}")
            return None

    def generate_comic_sequence(
        self,
        script_scenes: List[dict],
        output_dir: str = "output/frames",
        maintain_character: bool = True,
        show_progress: bool = True
    ) -> List[ComicFrame]:
        """
        根据剧本生成完整漫画序列

        Args:
            script_scenes: [
                {
                    "description": "场景描述",
                    "dialogue": "对话内容",
                    "duration": 5.0,
                    "character": "角色A"
                }
            ]
            output_dir: 输出目录
            maintain_character: 是否维持角色一致性
            show_progress: 是否显示进度

        Returns:
            ComicFrame 列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        frames = []
        reference_images = []  # 存储第一帧作为参考

        if show_progress:
            print(f"\n🎨 开始生成漫画序列，共 {len(script_scenes)} 帧")
            print("-" * 40)

        for i, scene in enumerate(script_scenes):
            if show_progress:
                desc_preview = scene['description'][:50] + "..." if len(scene['description']) > 50 else scene['description']
                print(f"  [{i + 1}/{len(script_scenes)}] 生成: {desc_preview}")

            filename = f"frame_{i:03d}.png"
            filepath = output_path / filename

            # 使用参考图像保持角色一致
            refs = reference_images if maintain_character and reference_images else None

            result = self.generate_frame(
                description=scene["description"],
                output_path=str(filepath),
                reference_images=refs,
                character_consistency=maintain_character
            )

            if result:
                frames.append(ComicFrame(
                    frame_index=i,
                    image_path=result,
                    description=scene["description"],
                    duration_seconds=scene.get("duration", 3.0),
                    dialogue=scene.get("dialogue", "")
                ))

                # 将第一帧作为后续参考
                if i == 0 and maintain_character:
                    reference_images.append(result)

                if show_progress:
                    print(f"    ✅ 完成")
            else:
                if show_progress:
                    print(f"    ❌ 失败")

        if show_progress:
            print("-" * 40)
            print(f"✅ 图像生成完成，共 {len(frames)} 帧")

        return frames

    def edit_frame(
        self,
        original_image_path: str,
        edit_instruction: str,
        output_path: str
    ) -> Optional[str]:
        """
        编辑已有图像（修改表情、背景等）

        Args:
            original_image_path: 原图路径
            edit_instruction: 编辑指令（如"将背景改为夜晚"）
            output_path: 输出路径

        Returns:
            编辑后的图像路径
        """
        try:
            # 读取原图
            with open(original_image_path, "rb") as f:
                image_data = f.read()

            # 准备配置
            edit_config = types.EditImageConfig(
                aspect_ratio=self.aspect_ratio,
            )

            # 调用编辑 API
            response = self.client.models.edit_image(
                model=self.model,
                source=types.Image.from_bytes(image_data),
                prompt=edit_instruction,
                config=edit_config
            )

            # 保存编辑后的图像
            if response and len(response.generated_images) > 0:
                edited_image = response.generated_images[0].image
                edited_image.save(output_path)
                return output_path

            return None

        except Exception as e:
            print(f"❌ 图像编辑失败: {e}")
            return None


def main():
    """测试入口"""
    from dotenv import load_dotenv
    load_dotenv()

    print("🎨 Nano Banana Generator 测试")
    print("=" * 50)

    generator = NanoBananaGenerator()

    # 测试生成单帧
    test_scene = {
        "description": "一个可爱的蓝色机器人在科技感办公室里，日本动漫风格，温馨色调",
        "dialogue": "你好，我是AI助手！",
        "duration": 5.0
    }

    print(f"\n📝 测试场景: {test_scene['description']}")
    print(f"📁 输出路径: output/test_frame.png")

    result = generator.generate_frame(
        description=test_scene["description"],
        output_path="output/test_frame.png"
    )

    if result:
        print(f"✅ 测试成功: {result}")
        print(f"💡 提示: 使用 'open {result}' 查看生成的图像")
    else:
        print("❌ 测试失败")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
漫画短剧生成器
整合 Nano Banana (图像) + ElevenLabs (配音) + MoviePy (视频合成)
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.generators.nano_banana_generator import NanoBananaGenerator
from src.generators.tts_generator import TTSGenerator, AudioSegment
from src.generators.video_composer import VideoComposer


def generate_comic_drama(
    script: dict,
    output_dir: str = "output/comic-drama",
    date: Optional[str] = None
) -> Optional[str]:
    """
    生成漫画短剧

    Args:
        script: {
            "title": "短剧标题",
            "scenes": [
                {
                    "description": "场景描述（用于生成图像）",
                    "character": "角色名",
                    "dialogue": "对话内容",
                    "voice_id": "ElevenLabs语音ID",
                    "duration": 5.0
                }
            ]
        }
        output_dir: 输出目录
        date: 日期标识（默认今天）

    Returns:
        生成的视频路径，失败返回 None
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    output_path = Path(output_dir) / date
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"🎬 开始生成漫画短剧: {script['title']}")
    print("=" * 60)

    # 步骤 1: 生成漫画帧
    print(f"\n📍 步骤 1/3: 生成漫画图像（共 {len(script['scenes'])} 帧）")
    print("-" * 60)

    try:
        comic_gen = NanoBananaGenerator()
        frames = comic_gen.generate_comic_sequence(
            script_scenes=script["scenes"],
            output_dir=str(output_path / "frames"),
            maintain_character=True  # 保持角色一致性
        )

        if not frames:
            print("❌ 图像生成失败")
            return None

    except Exception as e:
        print(f"❌ 图像生成模块初始化失败: {e}")
        print("💡 提示: 请检查 GOOGLE_API_KEY 是否已设置")
        return None

    # 步骤 2: 生成角色配音
    print(f"\n📍 步骤 2/3: 生成角色配音（共 {len(script['scenes'])} 段）")
    print("-" * 60)

    try:
        tts_gen = TTSGenerator()
        audio_segments = []

        for i, scene in enumerate(script["scenes"]):
            print(f"  [{i + 1}/{len(script['scenes'])}] 配音: {scene['character']}...")

            filename = f"dialogue_{i:03d}.mp3"
            filepath = output_path / "audio" / filename

            result = tts_gen.generate_audio(
                text=scene["dialogue"],
                output_path=str(filepath),
                voice_id=scene["voice_id"]
            )

            if result:
                audio_segments.append(AudioSegment(
                    filepath=result,
                    duration_seconds=scene["duration"],
                    text=scene["dialogue"],
                    segment_index=i
                ))
                print(f"    ✅ 完成")
            else:
                print(f"    ❌ 失败")

        if not audio_segments:
            print("❌ 配音生成失败")
            return None

    except Exception as e:
        print(f"❌ 配音生成模块初始化失败: {e}")
        print("💡 提示: 请检查 ELEVENLABS_API_KEY 是否已设置")
        return None

    # 步骤 3: 合成视频
    print(f"\n📍 步骤 3/3: 合成最终视频")
    print("-" * 60)

    try:
        video_composer = VideoComposer()
        video_filename = f"{script['title']}.mp4"
        final_video_path = str(output_path / video_filename)

        video_meta = video_composer.compose_video(
            frames=frames,
            audio_segments=audio_segments,
            output_path=final_video_path,
            add_subtitles=True
        )

        if not video_meta:
            print("❌ 视频合成失败")
            return None

        print("\n" + "=" * 60)
        print(f"✅ 漫画短剧生成完成！")
        print(f"📁 输出文件: {video_meta.filepath}")
        print(f"📊 统计:")
        print(f"   - 图像帧数: {video_meta.total_frames}")
        print(f"   - 总时长: {video_meta.duration_seconds:.1f} 秒 ({video_meta.duration_seconds/60:.1f} 分钟)")
        print(f"   - 分辨率: {video_meta.resolution}")
        print(f"   - 帧率: {video_meta.fps} FPS")
        print(f"   - 字幕: {'是' if video_meta.has_subtitles else '否'}")
        print("=" * 60)
        print(f"\n💡 使用以下命令播放:")
        print(f"   open {video_meta.filepath}")

        return video_meta.filepath

    except Exception as e:
        print(f"❌ 视频合成失败: {e}")
        return None


# ========== 测试脚本 ==========

def create_test_script() -> dict:
    """创建测试剧本"""
    return {
        "title": "AI助手的一天",
        "scenes": [
            {
                "description": "科技感办公室，一个可爱的蓝色机器人坐在电脑前，日本动漫风格，温馨色调，明亮的氛围",
                "character": "AI助手",
                "dialogue": "早上好！我是你的AI助手小蓝，今天有什么可以帮你的吗？",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # 需要替换为实际语音ID
                "duration": 5.0
            },
            {
                "description": "办公室场景，一个年轻人手持咖啡杯，露出思考的表情，漫画风格，柔和的光线",
                "character": "用户小王",
                "dialogue": "我想做一个漫画短剧，但不知道从哪里开始...",
                "voice_id": "pNInz6obpgDQGcFmaJgB",  # 需要替换为实际语音ID
                "duration": 4.0
            },
            {
                "description": "蓝色机器人做出鼓励的手势，背景出现发光的想法泡泡，充满活力的色彩，动漫风格",
                "character": "AI助手",
                "dialogue": "别担心！用Nano Banana生成图像，用ElevenLabs配音，很简单的！",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "duration": 5.0
            },
            {
                "description": "电脑屏幕上显示生成的漫画作品，年轻人露出惊喜的表情，星星眼，背景有彩带和光效",
                "character": "用户小王",
                "dialogue": "哇！真的太棒了！我也要试试！",
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "duration": 3.0
            }
        ]
    }


if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()

    print("\n🍌 漫画短剧生成器 - Nano Banana + ElevenLabs")
    print("=" * 60)

    # 检查必需的环境变量
    required_env_vars = ["GOOGLE_API_KEY", "ELEVENLABS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ 缺少必需的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 请在 .env 文件中设置这些变量")
        print("   参考 .env.example 文件获取获取地址")
        sys.exit(1)

    # 创建测试剧本
    test_script = create_test_script()

    print("\n📋 剧本信息:")
    print(f"   标题: {test_script['title']}")
    print(f"   场景数: {len(test_script['scenes'])}")
    print(f"   预计时长: {sum(s['duration'] for s in test_script['scenes']):.0f} 秒")

    # 生成短剧
    print("\n" + "=" * 60)
    result = generate_comic_drama(test_script)

    if result:
        print(f"\n🎉 成功！视频已保存到:")
        print(f"   {result}")
        print(f"\n💡 快速预览:")
        print(f"   open {result}")
    else:
        print("\n❌ 生成失败，请检查日志")
        sys.exit(1)

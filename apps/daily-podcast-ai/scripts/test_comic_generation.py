#!/usr/bin/env python3
"""
漫画生成测试脚本
快速测试各个模块是否正常工作
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv


def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境配置...")
    print("-" * 60)

    load_dotenv()

    required_vars = {
        "GOOGLE_API_KEY": "Google AI (Nano Banana)",
        "ELEVENLABS_API_KEY": "ElevenLabs (配音)"
    }

    all_ok = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已设置 ({desc})")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            all_ok = False

    return all_ok


def test_image_generation():
    """测试图像生成"""
    print("\n🎨 测试 Nano Banana 图像生成...")
    print("-" * 60)

    try:
        from src.generators.nano_banana_generator import NanoBananaGenerator

        generator = NanoBananaGenerator()
        print("  ✅ 模块导入成功")

        # 测试生成单帧
        test_description = "一个可爱的蓝色机器人在咖啡厅里，日本动漫风格，温馨色调"
        output_path = "output/test/test_frame.png"

        print(f"  📝 测试场景: {test_description}")
        print(f"  🎨 开始生成...")

        result = generator.generate_frame(
            description=test_description,
            output_path=output_path
        )

        if result:
            print(f"  ✅ 图像生成成功: {result}")
            return True
        else:
            print(f"  ❌ 图像生成失败")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_voice_generation():
    """测试语音生成"""
    print("\n🎙️ 测试 ElevenLabs 语音生成...")
    print("-" * 60)

    try:
        from src.generators.tts_generator import TTSGenerator

        generator = TTSGenerator()
        print("  ✅ 模块导入成功")

        # 列出可用语音
        print("  📋 获取可用语音列表...")
        voices = generator.list_voices()

        if voices:
            print(f"  ✅ 找到 {len(voices)} 个可用语音")
            print("\n  前5个语音:")
            for i, voice in enumerate(voices[:5]):
                print(f"    {i+1}. {voice['name']} - {voice['voice_id']}")

            # 测试生成音频
            if generator.voice_id:
                test_text = "这是一个测试语音，听起来如何？"
                output_path = "output/test/test_audio.mp3"

                print(f"\n  📝 测试文本: {test_text}")
                print(f"  🎤 开始生成...")

                result = generator.generate_audio(
                    text=test_text,
                    output_path=output_path
                )

                if result:
                    print(f"  ✅ 语音生成成功: {result}")
                    return True
                else:
                    print(f"  ❌ 语音生成失败")
                    return False
            else:
                print(f"  ⚠️ 未配置 voice_id，跳过音频生成测试")
                print(f"  💡 运行 'python scripts/setup_voice.py' 配置语音")
                return True
        else:
            print(f"  ❌ 未找到可用语音")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_video_composition():
    """测试视频合成（需要先有图像和音频）"""
    print("\n🎬 测试视频合成...")
    print("-" * 60)

    # 检查是否有测试素材
    test_frame = Path("output/test/test_frame.png")
    test_audio = Path("output/test/test_audio.mp3")

    if not test_frame.exists() or not test_audio.exists():
        print("  ⚠️ 缺少测试素材，跳过视频合成测试")
        print("  💡 需要先运行图像和语音测试")
        return True

    try:
        from src.generators.video_composer import VideoComposer
        from src.generators.nano_banana_generator import ComicFrame
        from src.generators.tts_generator import AudioSegment

        composer = VideoComposer()
        print("  ✅ 模块导入成功")

        # 创建测试数据
        frames = [ComicFrame(
            frame_index=0,
            image_path=str(test_frame),
            description="测试帧",
            duration_seconds=3.0,
            dialogue="这是测试字幕"
        )]

        audio_segments = [AudioSegment(
            filepath=str(test_audio),
            duration_seconds=3.0,
            text="这是测试语音",
            segment_index=0
        )]

        output_path = "output/test/test_video.mp4"
        print(f"  🎬 开始合成视频...")

        result = composer.compose_video(
            frames=frames,
            audio_segments=audio_segments,
            output_path=output_path,
            add_subtitles=True,
            show_progress=False
        )

        if result:
            print(f"  ✅ 视频合成成功: {result.filepath}")
            return True
        else:
            print(f"  ❌ 视频合成失败")
            return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🧪 漫画短剧生成系统 - 测试套件")
    print("=" * 60)

    # 1. 检查环境
    if not check_environment():
        print("\n❌ 环境配置不完整，请先配置 API Keys")
        print("💡 参考 .env.example 文件")
        sys.exit(1)

    results = {
        "环境配置": True,
        "图像生成": False,
        "语音生成": False,
        "视频合成": False
    }

    # 2. 测试图像生成
    results["图像生成"] = test_image_generation()

    # 3. 测试语音生成
    results["语音生成"] = test_voice_generation()

    # 4. 测试视频合成
    if results["图像生成"] and results["语音生成"]:
        results["视频合成"] = test_video_composition()

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过！系统已就绪！")
        print("\n💡 下一步:")
        print("   1. 运行 'python scripts/generate_comic_drama.py' 生成完整短剧")
        print("   2. 或修改 generate_comic_drama.py 中的剧本内容")
        print("   3. 或使用 example_scripts.py 中的其他示例剧本")
    else:
        print("\n⚠️ 部分测试未通过，请检查上方错误信息")

    print("=" * 60)


if __name__ == "__main__":
    main()

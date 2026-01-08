#!/usr/bin/env python3
"""
展示所有可用功能和剧本
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from werewolf_game_scripts import WEREWOLF_SCRIPTS
from example_scripts import AVAILABLE_SCRIPTS


def print_banner():
    """打印横幅"""
    print("\n" + "=" * 70)
    print("🎬 漫画短剧生成系统 - 功能总览")
    print("=" * 70)


def show_werewolf_scripts():
    """展示狼人杀剧本"""
    print("\n🐺 狼人杀复盘系列（4个剧本）")
    print("-" * 70)

    for i, (key, func) in enumerate(WEREWOLF_SCRIPTS.items(), 1):
        script = func()
        total_duration = sum(s['duration'] for s in script['scenes'])

        print(f"\n  {i}. [{key}]")
        print(f"     标题: {script['title']}")
        print(f"     场景数: {len(script['scenes'])}")
        print(f"     时长: {total_duration:.0f}秒 ({total_duration/60:.1f}分钟)")

        # 预估成本
        image_cost = len(script['scenes']) * 0.008
        voice_cost = total_duration / 60 * 2.5
        total_cost = image_cost + voice_cost
        print(f"     预估成本: ¥{total_cost:.2f}")

    print("\n  💡 生成命令:")
    print("     python scripts/generate_werewolf_drama.py <key>")


def show_general_scripts():
    """展示通用剧本"""
    print("\n🎨 通用题材系列（4个剧本）")
    print("-" * 70)

    for i, (key, func) in enumerate(AVAILABLE_SCRIPTS.items(), 1):
        script = func()
        total_duration = sum(s['duration'] for s in script['scenes'])

        print(f"\n  {i}. [{key}]")
        print(f"     标题: {script['title']}")
        print(f"     场景数: {len(script['scenes'])}")
        print(f"     时长: {total_duration:.0f}秒")

    print("\n  💡 使用方法:")
    print("     在 generate_comic_drama.py 中导入:")
    print("     from example_scripts import get_coffee_shop_story")


def show_technical_specs():
    """展示技术规格"""
    print("\n⚙️ 技术规格")
    print("-" * 70)

    print("\n  🎨 图像生成: Google Nano Banana")
    print("     - 模型: gemini-2.5-flash-image")
    print("     - 分辨率: 1920x1080 (16:9)")
    print("     - 风格: 漫画/动漫/写实可选")
    print("     - 成本: ¥0.008/张")

    print("\n  🎙️ 语音合成: ElevenLabs")
    print("     - 模型: eleven_multilingual_v2")
    print("     - 格式: MP3 44.1kHz 128kbps")
    print("     - 成本: ¥2.5/分钟")

    print("\n  🎬 视频合成: MoviePy + FFmpeg")
    print("     - 编码: H.264")
    print("     - 帧率: 24 FPS")
    print("     - 音频: AAC")
    print("     - 字幕: 内嵌 PNG")


def show_cost_comparison():
    """成本对比"""
    print("\n💰 成本对比（1分钟短剧）")
    print("-" * 70)

    comparisons = [
        {
            "方案": "Nano Banana + ElevenLabs",
            "图像": "12帧 × ¥0.008 = ¥0.096",
            "配音": "¥2.50",
            "总计": "¥2.60",
            "推荐": "⭐⭐⭐⭐⭐"
        },
        {
            "方案": "Midjourney + ElevenLabs",
            "图像": "12帧 × ¥0.20 = ¥2.40",
            "配音": "¥2.50",
            "总计": "¥4.90",
            "推荐": "⭐⭐⭐"
        },
        {
            "方案": "ComfyUI本地 + ElevenLabs",
            "图像": "免费（需显卡）",
            "配音": "¥2.50",
            "总计": "¥2.50",
            "推荐": "⭐⭐⭐⭐"
        }
    ]

    for comp in comparisons:
        print(f"\n  {comp['方案']}")
        print(f"     图像: {comp['图像']}")
        print(f"     配音: {comp['配音']}")
        print(f"     总计: {comp['总计']}")
        print(f"     推荐: {comp['推荐']}")


def show_quick_commands():
    """展示快速命令"""
    print("\n⚡ 快速命令")
    print("-" * 70)

    commands = [
        ("测试系统", "python scripts/test_comic_generation.py"),
        ("生成狼人杀", "python scripts/generate_werewolf_drama.py"),
        ("生成通用短剧", "python scripts/generate_comic_drama.py"),
        ("查看狼人杀剧本", "python scripts/werewolf_game_scripts.py"),
        ("查看通用剧本", "python scripts/example_scripts.py"),
        ("配置语音", "python scripts/setup_voice.py"),
    ]

    for desc, cmd in commands:
        print(f"\n  📌 {desc}")
        print(f"     {cmd}")


def show_documentation():
    """展示文档"""
    print("\n📚 文档资源")
    print("-" * 70)

    docs = [
        ("狼人杀3分钟快速开始", "QUICKSTART_WEREWOLF.md"),
        ("狼人杀详细指南", "docs/WEREWOLF_DRAMA_GUIDE.md"),
        ("通用漫画短剧指南", "docs/COMIC_DRAMA_QUICKSTART.md"),
        ("配置文件说明", "config/comic.yaml"),
    ]

    for desc, path in docs:
        print(f"\n  📖 {desc}")
        print(f"     {path}")


def main():
    """主函数"""
    print_banner()
    show_werewolf_scripts()
    show_general_scripts()
    show_technical_specs()
    show_cost_comparison()
    show_quick_commands()
    show_documentation()

    print("\n" + "=" * 70)
    print("💡 推荐新手路径:")
    print("=" * 70)
    print("\n  1️⃣ 阅读快速开始: QUICKSTART_WEREWOLF.md")
    print("  2️⃣ 运行测试: python scripts/test_comic_generation.py")
    print("  3️⃣ 生成第一个视频: python scripts/generate_werewolf_drama.py")
    print("  4️⃣ 自定义剧本: 编辑 werewolf_game_scripts.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

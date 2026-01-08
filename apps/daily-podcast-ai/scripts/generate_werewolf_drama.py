#!/usr/bin/env python3
"""
狼人杀复盘短剧生成器
专门用于生成狼人杀游戏复盘视频
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from datetime import datetime
from dotenv import load_dotenv

from werewolf_game_scripts import WEREWOLF_SCRIPTS, list_werewolf_scripts, get_werewolf_script
from generate_comic_drama import generate_comic_drama


def main():
    """主函数"""
    load_dotenv()

    print("\n" + "=" * 60)
    print("🐺 狼人杀复盘短剧生成器")
    print("=" * 60)

    # 检查环境变量
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ 未设置 GOOGLE_API_KEY")
        print("💡 获取地址: https://aistudio.google.com/apikey")
        sys.exit(1)

    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ 未设置 ELEVENLABS_API_KEY")
        print("💡 获取地址: https://elevenlabs.io/app/settings/api-keys")
        sys.exit(1)

    # 解析命令行参数
    script_name = None
    for arg in sys.argv[1:]:
        if arg not in ['--yes', '-y']:
            script_name = arg
            break

    # 如果提供了剧本名称参数
    if script_name:
        try:
            script = get_werewolf_script(script_name)
        except ValueError as e:
            print(f"\n❌ {e}\n")
            list_werewolf_scripts()
            sys.exit(1)
    else:
        # 默认使用经典胜利局
        print("\n💡 未指定剧本，使用默认剧本: classic_win")
        print("   使用方法: python scripts/generate_werewolf_drama.py <script_name>")
        print("")
        list_werewolf_scripts()
        print("\n" + "=" * 60)

        script_name = "classic_win"
        script = get_werewolf_script(script_name)

    # 显示剧本信息
    total_duration = sum(s['duration'] for s in script['scenes'])
    print(f"\n📋 剧本信息:")
    print(f"   名称: {script_name}")
    print(f"   标题: {script['title']}")
    print(f"   场景数: {len(script['scenes'])}")
    print(f"   预计时长: {total_duration:.0f}秒 ({total_duration/60:.1f}分钟)")

    # 预估成本
    num_frames = len(script['scenes'])
    image_cost = num_frames * 0.008
    voice_cost = total_duration / 60 * 2.5
    total_cost = image_cost + voice_cost

    print(f"\n💰 预估成本:")
    print(f"   图像生成: {num_frames}帧 × ¥0.008 = ¥{image_cost:.3f}")
    print(f"   配音: {total_duration/60:.1f}分钟 × ¥2.5 ≈ ¥{voice_cost:.2f}")
    print(f"   总计: ¥{total_cost:.2f}")

    # 确认生成（支持 --yes 参数跳过）
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv

    if not auto_confirm:
        print("\n" + "=" * 60)
        try:
            confirm = input("是否开始生成？(y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                print("❌ 已取消")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\n⚡ 自动确认模式")
    else:
        print("\n" + "=" * 60)
        print("⚡ 自动确认模式，开始生成...")

    # 开始生成
    date = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"output/werewolf-drama/{script_name}"

    result = generate_comic_drama(
        script=script,
        output_dir=output_dir,
        date=date
    )

    if result:
        print("\n" + "=" * 60)
        print("🎉 狼人杀复盘短剧生成成功！")
        print("=" * 60)
        print(f"\n📁 视频位置:")
        print(f"   {result}")
        print(f"\n💡 快速预览:")
        print(f"   open {result}")
        print(f"\n📤 分享到:")
        print(f"   - 抖音/快手（竖屏版本：修改 config/comic.yaml 中 aspect_ratio 为 '9:16'）")
        print(f"   - B站/YouTube（当前16:9格式）")
        print(f"   - 小红书（需要裁剪为正方形）")
    else:
        print("\n❌ 生成失败，请检查日志")
        sys.exit(1)


if __name__ == "__main__":
    main()

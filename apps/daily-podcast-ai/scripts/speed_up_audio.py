#!/usr/bin/env python3
"""
音频加速工具
使用 pydub 对已生成的音频进行速度调整，突破 ElevenLabs API 1.2倍速限制
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pydub import AudioSegment


def speed_up_audio(input_path: str, output_path: str, speed: float, verbose: bool = False):
    """
    加速音频文件

    Args:
        input_path: 输入音频文件路径
        output_path: 输出音频文件路径
        speed: 加速倍数 (1.0-3.0，推荐1.25-2.0)
        verbose: 是否显示详细信息

    Returns:
        是否成功
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        return False

    if verbose:
        print(f"📂 加载音频: {input_path}")

    try:
        # 加载音频
        audio = AudioSegment.from_file(input_path)

        if verbose:
            original_duration = len(audio) / 1000.0
            print(f"   原始时长: {original_duration:.1f} 秒 ({original_duration/60:.1f} 分钟)")
            print(f"   采样率: {audio.frame_rate} Hz")
            print(f"   声道数: {audio.channels}")

        # 调整速度（改变采样率来加速）
        new_sample_rate = int(audio.frame_rate * speed)

        if verbose:
            print(f"\n⚡ 加速处理中 ({speed}x)...")

        audio_fast = audio._spawn(audio.raw_data, overrides={
            "frame_rate": new_sample_rate
        })

        # 恢复正常采样率（保持音高不变）
        audio_fast = audio_fast.set_frame_rate(audio.frame_rate)

        if verbose:
            new_duration = len(audio_fast) / 1000.0
            print(f"   新时长: {new_duration:.1f} 秒 ({new_duration/60:.1f} 分钟)")
            print(f"   时长缩短: {(1 - new_duration/original_duration)*100:.1f}%")

        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 导出
        if verbose:
            print(f"\n💾 导出音频: {output_path}")

        audio_fast.export(output_path, format="mp3", bitrate="192k")

        # 显示文件大小
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ 已生成 {speed}x 速度音频: {output_path}")
        print(f"   文件大小: {file_size:.1f} MB")

        return True

    except Exception as e:
        print(f"❌ 加速失败: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="音频加速工具 - 突破 ElevenLabs 1.2倍速限制",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成1.5倍速版本
  python speed_up_audio.py podcast-2026-01-14-1.2x.mp3 --speed 1.5

  # 生成1.8倍速版本
  python speed_up_audio.py podcast-2026-01-14-1.2x.mp3 --speed 1.8

  # 生成2倍速版本
  python speed_up_audio.py podcast-2026-01-14-1.2x.mp3 --speed 2.0

  # 自定义输出路径
  python speed_up_audio.py podcast-2026-01-14-1.2x.mp3 \\
      --speed 1.5 \\
      --output my-fast-podcast.mp3

速度建议:
  1.25x - 微快，声音自然
  1.5x  - 明显加快，仍可听清（推荐）
  1.75x - 很快，需要集中注意力
  2.0x  - 极快，可能影响理解
        """
    )

    parser.add_argument(
        "input",
        help="输入音频文件路径"
    )

    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=1.5,
        help="加速倍数 (1.0-3.0，推荐1.25-2.0，默认1.5)"
    )

    parser.add_argument(
        "--output", "-o",
        help="输出文件路径 (默认: 在输入文件名后添加速度标识)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )

    args = parser.parse_args()

    # 验证速度范围
    if args.speed < 1.0 or args.speed > 3.0:
        print("⚠️ 警告: 速度建议在 1.0-3.0 之间")
        if args.speed > 3.0:
            print("   速度过快可能严重影响音质和可听性")
        elif args.speed < 1.0:
            print("   速度过慢，建议直接使用原始文件或调整 config/voice.yaml")

    # 生成输出文件名
    if args.output:
        output_path = args.output
    else:
        input_file = Path(args.input)
        # 智能生成文件名: podcast-2026-01-14-1.2x.mp3 -> podcast-2026-01-14-1.5x.mp3
        base_name = input_file.stem  # podcast-2026-01-14-1.2x

        # 移除旧的速度标识（如果有）
        if "-" in base_name and "x" in base_name.split("-")[-1]:
            parts = base_name.split("-")
            base_name = "-".join(parts[:-1])  # 移除最后的速度部分

        new_name = f"{base_name}-{args.speed}x{input_file.suffix}"
        output_path = str(input_file.parent / new_name)

    print()
    print("=" * 50)
    print("⚡ 音频加速工具")
    print("=" * 50)
    print(f"📂 输入: {args.input}")
    print(f"📁 输出: {output_path}")
    print(f"⚡ 速度: {args.speed}x")
    print()

    # 执行加速
    success = speed_up_audio(args.input, output_path, args.speed, verbose=args.verbose)

    if success:
        print()
        print("🎉 处理完成!")
        sys.exit(0)
    else:
        print()
        print("❌ 处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()

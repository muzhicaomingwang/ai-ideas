#!/usr/bin/env python3
"""
合并音频片段为最终播客
"""

import sys
from pathlib import Path
from pydub import AudioSegment


def merge_audio_sections(
    audio_dir: str,
    output_path: str,
    silence_duration: int = 2000,
):
    """
    合并所有音频章节

    Args:
        audio_dir: 音频片段目录
        output_path: 输出文件路径
        silence_duration: 章节间静音时长（毫秒）
    """
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        print(f"❌ 音频目录不存在: {audio_dir}")
        return False

    # 获取所有 section 音频文件（按编号排序）
    section_files = sorted(audio_path.glob("section_*.mp3"))

    if not section_files:
        print(f"❌ 未找到音频文件")
        return False

    print(f"📂 找到 {len(section_files)} 个音频片段")
    print("-" * 50)

    # 合并音频
    combined = AudioSegment.empty()
    total_duration = 0

    for i, section_file in enumerate(section_files, 1):
        print(f"  [{i}/{len(section_files)}] {section_file.name}")

        try:
            audio = AudioSegment.from_mp3(section_file)
            duration = len(audio) / 1000.0
            combined += audio
            total_duration += duration

            # 章节之间加静音
            if i < len(section_files):
                combined += AudioSegment.silent(duration=silence_duration)
                total_duration += silence_duration / 1000.0

            print(f"      ✅ {duration:.1f}秒")

        except Exception as e:
            print(f"      ❌ 错误: {e}")
            continue

    # 导出最终音频
    print("-" * 50)
    print(f"💾 导出音频...")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    combined.export(
        str(output_file),
        format="mp3",
        bitrate="192k",
        parameters=["-q:a", "2"]  # VBR quality
    )

    print(f"✅ 播客生成完成!")
    print(f"📁 文件: {output_file}")
    print(f"⏱️  时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)")
    print(f"💾 大小: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="合并音频片段")
    parser.add_argument(
        "--audio-dir", "-a",
        type=str,
        default="output/2026-01-08/audio",
        help="音频片段目录"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output/2026-01-08/podcast-perfect-days-review-2026-01-08-fixed.mp3",
        help="输出文件路径"
    )
    parser.add_argument(
        "--silence", "-s",
        type=int,
        default=2000,
        help="章节间静音时长（毫秒）"
    )

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("🎧 音频合并工具")
    print("=" * 50 + "\n")

    result = merge_audio_sections(
        audio_dir=args.audio_dir,
        output_path=args.output,
        silence_duration=args.silence,
    )

    if result:
        print("\n✅ 合并成功!")
        sys.exit(0)
    else:
        print("\n❌ 合并失败")
        sys.exit(1)

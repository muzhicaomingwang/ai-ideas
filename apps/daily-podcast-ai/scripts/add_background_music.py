#!/usr/bin/env python3
"""
为播客添加背景音乐
支持多首音乐交叉播放
"""

import sys
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play


def add_background_music(
    podcast_path: str,
    music_files: list[str],
    output_path: str,
    music_volume_ratio: float = 0.2,
    crossfade_duration: int = 5000,
):
    """
    为播客添加背景音乐

    Args:
        podcast_path: 播客音频文件路径
        music_files: 背景音乐文件路径列表
        output_path: 输出文件路径
        music_volume_ratio: 背景音乐音量比例（默认0.2，即20%）
        crossfade_duration: 音乐切换时的淡入淡出时长（毫秒）

    Returns:
        输出文件路径
    """
    print("📂 加载播客文件...")
    podcast = AudioSegment.from_mp3(podcast_path)
    podcast_duration = len(podcast)
    print(f"   播客时长: {podcast_duration / 1000:.1f} 秒")

    print("\n🎵 加载背景音乐...")
    music_tracks = []
    for i, music_file in enumerate(music_files, 1):
        if not Path(music_file).exists():
            print(f"   ⚠️ 文件不存在: {music_file}")
            continue

        try:
            music = AudioSegment.from_file(music_file)
            print(f"   [{i}] {Path(music_file).name} ({len(music) / 1000:.1f}秒)")
            music_tracks.append(music)
        except Exception as e:
            print(f"   ❌ 加载失败: {music_file} - {e}")

    if not music_tracks:
        print("\n❌ 没有可用的背景音乐")
        return None

    # 降低音乐音量
    print(f"\n🔊 调整音量到 {music_volume_ratio * 100:.0f}%...")
    volume_db = -20 * (1 - music_volume_ratio) * 2  # 大约 -32dB for 20%
    music_tracks = [music + volume_db for music in music_tracks]

    # 创建背景音乐循环（交叉播放）
    print("\n🔄 创建背景音乐循环...")
    background = AudioSegment.empty()
    track_index = 0
    total_plays = {}

    while len(background) < podcast_duration:
        current_track = music_tracks[track_index % len(music_tracks)]
        track_name = Path(music_files[track_index % len(music_files)]).stem

        # 统计播放次数
        total_plays[track_name] = total_plays.get(track_name, 0) + 1

        # 添加音乐片段
        if len(background) == 0:
            # 第一段，淡入
            background = current_track.fade_in(3000)
        else:
            # 后续片段，交叉淡入淡出
            background = background.append(current_track, crossfade=crossfade_duration)

        print(f"   添加: {track_name} (第{total_plays[track_name]}次)")
        track_index += 1

    # 裁剪背景音乐到播客长度
    background = background[:podcast_duration]

    # 在结尾淡出
    background = background.fade_out(5000)

    print(f"\n📊 播放统计:")
    for track_name, count in total_plays.items():
        print(f"   {track_name}: {count}次")

    # 混音
    print("\n🎚️  混合音频...")
    final = podcast.overlay(background)

    # 导出
    print(f"\n💾 导出最终音频...")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    final.export(
        str(output_file),
        format="mp3",
        bitrate="192k",
        parameters=["-q:a", "2"]
    )

    final_size = output_file.stat().st_size / 1024 / 1024

    print(f"\n✅ 生成完成!")
    print(f"📁 文件: {output_file}")
    print(f"⏱️  时长: {len(final) / 1000:.1f} 秒 ({len(final) / 60000:.1f} 分钟)")
    print(f"💾 大小: {final_size:.1f} MB")

    return str(output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="为播客添加背景音乐")
    parser.add_argument("podcast", type=str, help="播客文件路径")
    parser.add_argument(
        "--music", "-m",
        type=str,
        nargs="+",
        required=True,
        help="背景音乐文件路径（可多个）"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="输出文件路径"
    )
    parser.add_argument(
        "--volume", "-v",
        type=float,
        default=0.2,
        help="背景音乐音量比例（0.0-1.0，默认0.2）"
    )
    parser.add_argument(
        "--crossfade", "-c",
        type=int,
        default=5000,
        help="音乐切换时淡入淡出时长（毫秒，默认5000）"
    )

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("🎵 播客背景音乐添加工具")
    print("=" * 50 + "\n")

    result = add_background_music(
        podcast_path=args.podcast,
        music_files=args.music,
        output_path=args.output,
        music_volume_ratio=args.volume,
        crossfade_duration=args.crossfade,
    )

    if result:
        print("\n🎉 处理完成!")
        sys.exit(0)
    else:
        print("\n❌ 处理失败")
        sys.exit(1)

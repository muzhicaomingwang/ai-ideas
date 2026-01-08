#!/usr/bin/env python3
"""
生成环境背景音乐
使用简单的音频合成技术创建平静的背景音
"""

import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
import random


def generate_ambient_piano_like(
    duration_seconds: int = 180,
    output_path: str = "music/my-dream.mp3",
    title: str = "My Dream"
):
    """
    生成类似钢琴的环境音乐

    使用多个正弦波叠加模拟和声效果
    """
    print(f"🎵 正在生成: {title}")
    print(f"   时长: {duration_seconds}秒")

    # 创建空音轨
    duration_ms = duration_seconds * 1000
    sample_rate = 44100

    # 使用钢琴音域的音符（C大调）
    # 基础频率（Hz）
    notes = {
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
    }

    # 选择和弦进行（C大调，宁静的和弦）
    chord_progressions = [
        ['C4', 'E4', 'G4'],  # C major
        ['A3', 'C4', 'E4'],  # A minor
        ['F3', 'A3', 'C4'],  # F major
        ['G3', 'B3', 'D4'],  # G major
        ['E3', 'G3', 'B3'],  # E minor
        ['D3', 'F3', 'A3'],  # D minor
    ]

    # 创建基础音轨
    base_track = AudioSegment.silent(duration=0)

    # 每个和弦持续时间（秒）
    chord_duration = 8
    num_chords = duration_seconds // chord_duration

    random.seed(42)  # 固定随机种子，保证每次生成相同

    for i in range(num_chords):
        # 随机选择和弦
        chord = random.choice(chord_progressions)

        # 叠加和弦中的所有音符
        chord_sound = AudioSegment.silent(duration=chord_duration * 1000)

        for note_name in chord:
            freq = notes[note_name]
            # 生成正弦波
            tone = Sine(freq).to_audio_segment(duration=chord_duration * 1000)
            # 降低音量
            tone = tone - 20
            # 添加淡入淡出
            tone = tone.fade_in(1000).fade_out(1000)
            # 叠加
            chord_sound = chord_sound.overlay(tone)

        # 添加到主音轨
        base_track += chord_sound

    # 添加轻微的白噪音（模拟环境感）
    noise = WhiteNoise().to_audio_segment(duration=len(base_track))
    noise = noise - 45  # 非常轻的噪音
    base_track = base_track.overlay(noise)

    # 整体淡入淡出
    base_track = base_track.fade_in(3000).fade_out(3000)

    # 整体降低音量（适合做背景）
    base_track = base_track - 5

    # 导出
    base_track.export(output_path, format="mp3", bitrate="128k")

    print(f"✅ 生成完成: {output_path}")
    print(f"   时长: {len(base_track)/1000:.1f}秒")

    return output_path


def main():
    """生成两首背景音乐"""
    print("\n" + "=" * 50)
    print("🎼 环境背景音乐生成器")
    print("=" * 50 + "\n")

    # 第1首：My Dream（深沉、宁静）
    print("生成第1首...")
    track1 = generate_ambient_piano_like(
        duration_seconds=240,  # 4分钟
        output_path="music/my-dream.mp3",
        title="My Dream"
    )

    print()

    # 第2首：Nostalgic Moments（怀旧、温暖）
    print("生成第2首...")
    track2 = generate_ambient_piano_like(
        duration_seconds=200,  # 3分20秒
        output_path="music/nostalgic-moments.mp3",
        title="Nostalgic Moments"
    )

    print("\n" + "=" * 50)
    print("✅ 两首背景音乐生成完成!")
    print("=" * 50)
    print(f"\n📁 {track1}")
    print(f"📁 {track2}")
    print("\n💡 现在可以运行混音脚本了")


if __name__ == "__main__":
    main()

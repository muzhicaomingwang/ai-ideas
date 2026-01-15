"""
音频混合与后处理模块
将多个音频片段合并为完整的播客，并添加背景音乐
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from pydub import AudioSegment as PydubSegment


@dataclass
class MixedAudio:
    """混合后的音频"""
    filepath: str
    duration_seconds: float
    total_segments: int
    has_bgm: bool
    has_intro_jingle: bool
    has_outro_jingle: bool


class AudioMixer:
    """音频混合器"""

    def __init__(self, config_path: str = "config/voice.yaml"):
        """
        初始化音频混合器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.audio_config = self.config.get("audio", {})

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
            "audio": {
                "output_format": "mp3",
                "bitrate": "192k",
                "sample_rate": 44100,
                "normalize": True,
                "fade_duration_ms": 500,
                "segment_gap_ms": 800,
                "bgm_volume_reduction_db": -20
            }
        }

    def _load_audio(self, filepath: str) -> Optional[PydubSegment]:
        """
        加载音频文件

        Args:
            filepath: 音频文件路径

        Returns:
            PydubSegment 对象，失败返回 None
        """
        try:
            return PydubSegment.from_file(filepath)
        except Exception as e:
            print(f"❌ 加载音频失败 ({filepath}): {e}")
            return None

    def _apply_fade(
        self,
        audio: PydubSegment,
        fade_in: bool = True,
        fade_out: bool = True
    ) -> PydubSegment:
        """
        应用淡入淡出效果

        Args:
            audio: 音频片段
            fade_in: 是否淡入
            fade_out: 是否淡出

        Returns:
            处理后的音频
        """
        fade_duration = self.audio_config.get("fade_duration_ms", 500)

        if fade_in:
            audio = audio.fade_in(fade_duration)
        if fade_out:
            audio = audio.fade_out(fade_duration)

        return audio

    def _normalize_audio(self, audio: PydubSegment) -> PydubSegment:
        """
        标准化音频音量

        Args:
            audio: 音频片段

        Returns:
            标准化后的音频
        """
        target_dbfs = -20.0
        change_in_dbfs = target_dbfs - audio.dBFS
        return audio.apply_gain(change_in_dbfs)

    def concatenate_segments(
        self,
        segment_files: list[str],
        output_path: str,
        add_gaps: bool = True,
        normalize: bool = True,
        show_progress: bool = True
    ) -> Optional[MixedAudio]:
        """
        将多个音频片段合并为一个

        Args:
            segment_files: 音频文件路径列表
            output_path: 输出文件路径
            add_gaps: 是否在片段之间添加间隔
            normalize: 是否标准化音量
            show_progress: 是否显示进度

        Returns:
            MixedAudio 对象，失败返回 None
        """
        if not segment_files:
            print("❌ 没有音频片段")
            return None

        if show_progress:
            print(f"\n🎧 开始合并音频，共 {len(segment_files)} 个片段")
            print("-" * 40)

        gap_duration = self.audio_config.get("segment_gap_ms", 800)
        gap = PydubSegment.silent(duration=gap_duration)

        combined = PydubSegment.empty()

        for i, filepath in enumerate(segment_files):
            if show_progress:
                print(f"  [{i + 1}/{len(segment_files)}] 处理: {Path(filepath).name}")

            segment = self._load_audio(filepath)
            if segment is None:
                continue

            # 标准化
            if normalize:
                segment = self._normalize_audio(segment)

            # 添加到合并音频
            if len(combined) > 0 and add_gaps:
                combined += gap
            combined += segment

        if len(combined) == 0:
            print("❌ 合并失败，没有有效的音频")
            return None

        # 应用整体淡入淡出
        combined = self._apply_fade(combined)

        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 导出
        bitrate = self.audio_config.get("bitrate", "192k")
        combined.export(output_path, format="mp3", bitrate=bitrate)

        duration_seconds = len(combined) / 1000.0

        if show_progress:
            print("-" * 40)
            print(f"✅ 合并完成: {output_path}")
            print(f"   时长: {duration_seconds:.1f} 秒")

        return MixedAudio(
            filepath=str(output_file),
            duration_seconds=duration_seconds,
            total_segments=len(segment_files),
            has_bgm=False,
            has_intro_jingle=False,
            has_outro_jingle=False
        )

    def add_background_music(
        self,
        voice_audio_path: str,
        bgm_path: str,
        output_path: str,
        bgm_volume_db: Optional[float] = None
    ) -> Optional[str]:
        """
        为音频添加背景音乐

        Args:
            voice_audio_path: 人声音频路径
            bgm_path: 背景音乐路径
            output_path: 输出路径
            bgm_volume_db: 背景音乐音量调整（dB）

        Returns:
            输出文件路径，失败返回 None
        """
        voice = self._load_audio(voice_audio_path)
        bgm = self._load_audio(bgm_path)

        if voice is None or bgm is None:
            return None

        # 调整背景音乐音量
        if bgm_volume_db is None:
            bgm_volume_db = self.audio_config.get("bgm_volume_reduction_db", -20)
        bgm = bgm + bgm_volume_db

        # 循环背景音乐以匹配人声长度
        voice_duration = len(voice)
        if len(bgm) < voice_duration:
            loops_needed = (voice_duration // len(bgm)) + 1
            bgm = bgm * loops_needed
        bgm = bgm[:voice_duration]

        # 为背景音乐添加淡入淡出
        bgm = self._apply_fade(bgm)

        # 混合
        mixed = voice.overlay(bgm)

        # 导出
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        bitrate = self.audio_config.get("bitrate", "192k")
        mixed.export(output_path, format="mp3", bitrate=bitrate)

        return str(output_file)

    def add_jingles(
        self,
        main_audio_path: str,
        output_path: str,
        intro_jingle_path: Optional[str] = None,
        outro_jingle_path: Optional[str] = None
    ) -> Optional[str]:
        """
        添加片头片尾音效

        Args:
            main_audio_path: 主音频路径
            output_path: 输出路径
            intro_jingle_path: 片头音效路径
            outro_jingle_path: 片尾音效路径

        Returns:
            输出文件路径，失败返回 None
        """
        main_audio = self._load_audio(main_audio_path)
        if main_audio is None:
            return None

        result = PydubSegment.empty()

        # 添加片头
        if intro_jingle_path:
            intro = self._load_audio(intro_jingle_path)
            if intro:
                intro = self._apply_fade(intro, fade_in=True, fade_out=True)
                result += intro
                # 添加短暂间隔
                result += PydubSegment.silent(duration=500)

        # 添加主音频
        result += main_audio

        # 添加片尾
        if outro_jingle_path:
            outro = self._load_audio(outro_jingle_path)
            if outro:
                # 添加短暂间隔
                result += PydubSegment.silent(duration=500)
                outro = self._apply_fade(outro, fade_in=True, fade_out=True)
                result += outro

        # 导出
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        bitrate = self.audio_config.get("bitrate", "192k")
        result.export(output_path, format="mp3", bitrate=bitrate)

        return str(output_file)

    def create_final_podcast(
        self,
        audio_segments,
        output_path: str,
        bgm_path: Optional[str] = None,
        intro_jingle_path: Optional[str] = None,
        outro_jingle_path: Optional[str] = None,
        show_progress: bool = True
    ) -> Optional[MixedAudio]:
        """
        创建最终的播客音频

        Args:
            audio_segments: AudioSegment 对象列表（来自 TTSGenerator）
            output_path: 最终输出路径
            bgm_path: 背景音乐路径（可选）
            intro_jingle_path: 片头音效路径（可选）
            outro_jingle_path: 片尾音效路径（可选）
            show_progress: 是否显示进度

        Returns:
            MixedAudio 对象
        """
        # 提取文件路径
        segment_files = [seg.filepath for seg in audio_segments]

        # 临时文件路径
        temp_dir = Path(output_path).parent / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 步骤1: 合并所有片段
        if show_progress:
            print("\n📀 步骤 1/3: 合并音频片段")

        temp_merged = str(temp_dir / "merged.mp3")
        merged = self.concatenate_segments(
            segment_files,
            temp_merged,
            show_progress=show_progress
        )

        if merged is None:
            return None

        current_audio = temp_merged
        has_bgm = False
        has_intro = False
        has_outro = False

        # 步骤2: 添加背景音乐（如果提供）
        if bgm_path and Path(bgm_path).exists():
            if show_progress:
                print("\n🎵 步骤 2/3: 添加背景音乐")

            temp_with_bgm = str(temp_dir / "with_bgm.mp3")
            result = self.add_background_music(
                current_audio,
                bgm_path,
                temp_with_bgm
            )
            if result:
                current_audio = result
                has_bgm = True
                if show_progress:
                    print("  ✅ 背景音乐添加完成")
        else:
            if show_progress:
                print("\n🎵 步骤 2/3: 跳过（无背景音乐）")

        # 步骤3: 添加片头片尾（如果提供）
        intro_exists = intro_jingle_path and Path(intro_jingle_path).exists()
        outro_exists = outro_jingle_path and Path(outro_jingle_path).exists()

        if intro_exists or outro_exists:
            if show_progress:
                print("\n🎶 步骤 3/3: 添加片头片尾")

            result = self.add_jingles(
                current_audio,
                output_path,
                intro_jingle_path if intro_exists else None,
                outro_jingle_path if outro_exists else None
            )
            if result:
                has_intro = intro_exists
                has_outro = outro_exists
                if show_progress:
                    print("  ✅ 片头片尾添加完成")
        else:
            if show_progress:
                print("\n🎶 步骤 3/3: 跳过（无片头片尾）")
            # 复制最终文件
            import shutil
            shutil.copy(current_audio, output_path)

        # 清理临时文件
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        # 获取最终音频信息
        final_audio = self._load_audio(output_path)
        if final_audio:
            duration = len(final_audio) / 1000.0
        else:
            duration = merged.duration_seconds

        if show_progress:
            print("\n" + "=" * 40)
            print(f"🎉 播客生成完成!")
            print(f"   📁 文件: {output_path}")
            print(f"   ⏱️ 时长: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
            print(f"   🎵 背景音乐: {'是' if has_bgm else '否'}")
            print(f"   🎬 片头: {'是' if has_intro else '否'}")
            print(f"   🏁 片尾: {'是' if has_outro else '否'}")

        return MixedAudio(
            filepath=output_path,
            duration_seconds=duration,
            total_segments=len(audio_segments),
            has_bgm=has_bgm,
            has_intro_jingle=has_intro,
            has_outro_jingle=has_outro
        )


def main():
    """测试入口"""
    print("🎧 Audio Mixer 测试")
    print("=" * 50)

    mixer = AudioMixer()

    # 检查测试文件
    test_dir = Path("output/audio")
    if not test_dir.exists():
        print("⚠️ 测试目录不存在，请先运行 TTS 生成器")
        return

    # 查找测试文件
    test_files = list(test_dir.glob("*.mp3"))
    if not test_files:
        print("⚠️ 没有找到测试音频文件")
        return

    print(f"\n📋 找到 {len(test_files)} 个音频文件")

    # 测试合并
    output_path = "output/test_podcast.mp3"
    result = mixer.concatenate_segments(
        [str(f) for f in test_files[:3]],  # 只测试前3个
        output_path
    )

    if result:
        print(f"\n✅ 测试完成: {result.filepath}")
        print(f"   时长: {result.duration_seconds:.1f} 秒")


if __name__ == "__main__":
    main()

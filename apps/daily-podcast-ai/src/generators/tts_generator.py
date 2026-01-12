"""
TTS 语音合成模块
使用 ElevenLabs API 将文本转换为语音
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from elevenlabs import ElevenLabs, VoiceSettings


@dataclass
class AudioSegment:
    """音频片段"""
    filepath: str
    duration_seconds: float
    text: str
    segment_index: int


class TTSGenerator:
    """ElevenLabs TTS 语音生成器"""

    def __init__(self, config_path: str = "config/voice.yaml"):
        """
        初始化 TTS 生成器

        Args:
            config_path: 语音配置文件路径
        """
        self.config = self._load_config(config_path)
        self.tts_config = self.config.get("tts", {})

        # 初始化 ElevenLabs 客户端
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("未设置 ELEVENLABS_API_KEY 环境变量")

        self.client = ElevenLabs(api_key=api_key)

        # 获取配置
        self.voice_id = self.tts_config.get("voice_id", "")
        self.model_id = self.tts_config.get("model", "eleven_multilingual_v2")
        self.output_format = self.tts_config.get("output_format", "mp3_44100_128")

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
            "tts": {
                "model": "eleven_multilingual_v2",
                "output_format": "mp3_44100_128",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
        }

    def _get_voice_settings(self, speed: Optional[float] = None) -> VoiceSettings:
        """获取语音设置"""
        settings = self.tts_config.get("voice_settings", {})
        # 获取语速设置（范围 0.7-1.2）
        speech_speed = speed or self.tts_config.get("speed", 1.0)
        speech_speed = max(0.7, min(1.2, speech_speed))  # 限制范围
        
        return VoiceSettings(
            stability=settings.get("stability", 0.5),
            similarity_boost=settings.get("similarity_boost", 0.75),
            style=settings.get("style", 0.0),
            use_speaker_boost=settings.get("use_speaker_boost", True),
            speed=speech_speed
        )

    def list_voices(self) -> list[dict]:
        """
        列出可用的语音

        Returns:
            语音列表
        """
        try:
            response = self.client.voices.get_all()
            voices = []
            for voice in response.voices:
                voices.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "labels": voice.labels
                })
            return voices
        except Exception as e:
            print(f"❌ 获取语音列表失败: {e}")
            return []

    def get_voice_info(self, voice_id: str) -> Optional[dict]:
        """
        获取指定语音的详细信息

        Args:
            voice_id: 语音 ID

        Returns:
            语音信息字典
        """
        try:
            voice = self.client.voices.get(voice_id)
            return {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "labels": voice.labels,
                "description": voice.description
            }
        except Exception as e:
            print(f"❌ 获取语音信息失败: {e}")
            return None

    def generate_audio(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None
    ) -> Optional[str]:
        """
        将文本转换为音频

        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            voice_id: 语音 ID（可选，默认使用配置中的）
            speed: 语速（0.7-1.2，默认使用配置中的）

        Returns:
            生成的音频文件路径，失败返回 None
        """
        voice_id = voice_id or self.voice_id
        if not voice_id:
            print("❌ 未指定 voice_id")
            return None

        try:
            # 调用 ElevenLabs API（语速通过 VoiceSettings 传递）
            audio = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=self.model_id,
                output_format=self.output_format,
                voice_settings=self._get_voice_settings(speed)
            )

            # 确保输出目录存在
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存音频
            with open(output_file, "wb") as f:
                for chunk in audio:
                    f.write(chunk)

            return str(output_file)

        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return None

    def generate_podcast_audio(
        self,
        script,
        output_dir: str = "output/audio",
        show_progress: bool = True
    ) -> list[AudioSegment]:
        """
        为整个播客脚本生成音频

        Args:
            script: PodcastScript 对象
            output_dir: 输出目录
            show_progress: 是否显示进度

        Returns:
            AudioSegment 列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        segments = []

        # 收集所有需要转换的文本
        texts = []

        # 开场白
        texts.append(("intro", script.intro))

        # 新闻片段
        for i, segment in enumerate(script.segments):
            texts.append((f"segment_{i}", segment["text"]))
            if segment.get("transition"):
                texts.append((f"transition_{i}", segment["transition"]))

        # 结束语
        texts.append(("outro", script.outro))

        if show_progress:
            print(f"\n🎙️ 开始生成音频，共 {len(texts)} 个片段")
            print("-" * 40)

        rate_limit_delay = self.tts_config.get("rate_limit_delay", 1.0)

        for i, (name, text) in enumerate(texts):
            if show_progress:
                print(f"  [{i + 1}/{len(texts)}] 生成: {name}...")

            filename = f"{script.date}_{name}.mp3"
            filepath = output_path / filename

            result = self.generate_audio(text, str(filepath))

            if result:
                # 获取音频时长（简单估算，实际可用 pydub 计算）
                # 中文语速约 3-4 字/秒
                estimated_duration = len(text) / 3.5

                segments.append(AudioSegment(
                    filepath=result,
                    duration_seconds=estimated_duration,
                    text=text,
                    segment_index=i
                ))

                if show_progress:
                    print(f"    ✅ 完成")
            else:
                if show_progress:
                    print(f"    ❌ 失败")

            # 速率限制
            if i < len(texts) - 1:
                time.sleep(rate_limit_delay)

        if show_progress:
            print("-" * 40)
            print(f"✅ 音频生成完成，共 {len(segments)} 个片段")

        return segments

    def generate_dialogue_audio(
        self,
        dialogue_script,  # DialogueScript object
        output_dir: str = "output/dialogue_audio",
        show_progress: bool = True
    ) -> list[AudioSegment]:
        """
        生成双人对话音频
        
        Args:
            dialogue_script: DialogueScript 对象 (来自 dialogue_writer.py)
            output_dir: 输出目录
            show_progress: 是否显示进度
            
        Returns:
            AudioSegment 列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        segments = []
        
        # 获取主持人配置
        host_config = self.config.get("hosts", {})
        voice_map = {
            "Host A": host_config.get("host_a", {}).get("voice_id", self.voice_id),
            "Host B": host_config.get("host_b", {}).get("voice_id", "")
        }
        
        # 如果没有配置 Host B，使用默认列表中的备选或 fallback
        if not voice_map["Host B"]:
            print("⚠️ 未配置 Host B 声音 ID，尝试使用默认备选 'Adam'...")
            voice_map["Host B"] = "pNInz6obpgDQGcFmaJgB" # Default Adam
            
        rate_limit_delay = self.tts_config.get("rate_limit_delay", 0.5)
        
        if show_progress:
            print(f"\n🎙️ 开始生成双人对话音频，共 {len(dialogue_script.lines)} 句对话")
            print(f"   Host A Voice: {voice_map['Host A']}")
            print(f"   Host B Voice: {voice_map['Host B']}")
            print("-" * 40)
            
        for i, line in enumerate(dialogue_script.lines):
            speaker = line.speaker
            text = line.text
            voice_id = voice_map.get(speaker, voice_map["Host A"])
            
            # 简单的表情处理 (可以通过 stability 调整，暂未深度实现)
            # emotion = line.emotion 
            
            filename = f"{dialogue_script.date}_line_{i:03d}_{speaker.replace(' ', '')}.mp3"
            filepath = output_path / filename
            
            if show_progress:
                speaker_icon = "🗣️" if speaker == "Host A" else "🤖"
                print(f"  [{i+1}/{len(dialogue_script.lines)}] {speaker_icon} {speaker}: {text[:20]}...")
            
            # 检查文件是否已存在 (避免重复生成节省 Credit)
            if filepath.exists():
                if show_progress:
                    print("    ⏩ 跳过 (已存在)")
                segments.append(AudioSegment(
                    filepath=str(filepath),
                    duration_seconds=0, # 需重新计算，或读取文件元数据
                    text=text,
                    segment_index=i
                ))
                continue

            result = self.generate_audio(text, str(filepath), voice_id=voice_id)
            
            if result:
                segments.append(AudioSegment(
                    filepath=result,
                    duration_seconds=len(text)/3.5, # 估算
                    text=text,
                    segment_index=i
                ))
            else:
                print(f"    ❌ 生成失败")
                
            time.sleep(rate_limit_delay)
            
        return segments


def main():
    """测试入口"""
    from dotenv import load_dotenv
    load_dotenv()

    print("🎙️ TTS Generator 测试")
    print("=" * 50)

    generator = TTSGenerator()

    # 列出可用语音
    print("\n📋 可用语音列表:")
    voices = generator.list_voices()
    for voice in voices[:5]:  # 只显示前5个
        print(f"  - {voice['name']} ({voice['voice_id'][:8]}...)")

    # 测试生成
    if generator.voice_id:
        print(f"\n🎤 使用语音 ID: {generator.voice_id}")

        test_text = "大家好，欢迎收听今日科技早报。今天我们为大家带来最新的科技资讯。"
        output_path = "output/test_audio.mp3"

        print(f"📝 测试文本: {test_text}")
        print(f"📁 输出路径: {output_path}")

        result = generator.generate_audio(test_text, output_path)

        if result:
            print(f"✅ 音频生成成功: {result}")
        else:
            print("❌ 音频生成失败")
    else:
        print("\n⚠️ 未配置 voice_id，请先在 config/voice.yaml 中设置")


if __name__ == "__main__":
    main()

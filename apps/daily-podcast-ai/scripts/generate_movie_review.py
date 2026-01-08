#!/usr/bin/env python3
"""
电影影评播客生成脚本
专门用于生成长篇影评内容的播客
"""

import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / ".env")


def generate_movie_review_podcast(
    content_file: str,
    output_dir: str = "output",
    voice_id: str = None,
    verbose: bool = False,
):
    """
    生成电影影评播客

    Args:
        content_file: 影评内容文件路径（markdown）
        output_dir: 输出目录
        voice_id: ElevenLabs 语音 ID
        verbose: 详细输出
    """
    from generators import TTSGenerator
    from generators.tts_generator import AudioSegment

    # 读取影评内容
    content_path = Path(content_file)
    if not content_path.exists():
        print(f"❌ 内容文件不存在: {content_file}")
        return None

    with open(content_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析内容
    lines = content.split("\n")
    title = ""
    sections = []
    current_section = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 提取标题
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue

        # 提取章节
        if line.startswith("## "):
            if current_section and current_text:
                sections.append({
                    "title": current_section,
                    "content": "\n\n".join(current_text)
                })
            current_section = line[3:].strip()
            current_text = []
            continue

        # 跳过元数据
        if line.startswith("**") and ":" in line and len(line) < 50:
            continue

        # 跳过分隔线
        if line == "---":
            continue

        # 收集段落
        if current_section:
            current_text.append(line)

    # 添加最后一个章节
    if current_section and current_text:
        sections.append({
            "title": current_section,
            "content": "\n\n".join(current_text)
        })

    print(f"📖 解析完成: {title}")
    print(f"📚 共 {len(sections)} 个章节")

    # 创建输出目录
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = Path(output_dir) / date_str
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成完整脚本
    full_script = f"{title}\n\n"
    for section in sections:
        full_script += f"{section['title']}\n\n{section['content']}\n\n"

    # 保存脚本
    script_path = output_path / f"script-perfect-days-review-{date_str}.md"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_script)
    print(f"✅ 脚本已保存: {script_path}")

    # 生成音频
    print("\n🎙️ 开始语音合成...")
    print("-" * 50)

    try:
        tts = TTSGenerator()
        if voice_id:
            tts.voice_id = voice_id

        if not tts.voice_id:
            print("❌ 未配置 voice_id")
            return None

        print(f"🎤 使用语音 ID: {tts.voice_id[:16]}...")

        # 为每个章节生成音频
        audio_dir = output_path / "audio"
        audio_dir.mkdir(exist_ok=True)

        audio_segments = []

        for i, section in enumerate(sections, 1):
            print(f"\n  [{i}/{len(sections)}] {section['title'][:40]}...")

            # 生成章节音频
            text = f"{section['title']}\n\n{section['content']}"
            audio_path = str(audio_dir / f"section_{i:02d}.mp3")

            try:
                result = tts.generate_audio(text, audio_path)
                if result:
                    # 获取音频时长
                    from pydub import AudioSegment as PyDubSegment
                    audio = PyDubSegment.from_mp3(audio_path)
                    duration = len(audio) / 1000.0

                    audio_segments.append(
                        AudioSegment(filepath=audio_path, duration_seconds=duration, text=text, segment_index=i)
                    )
                    print(f"    ✅ 完成 ({duration:.1f}秒)")
                else:
                    print(f"    ⚠️ 生成失败，跳过")

                # API 速率限制
                if i < len(sections):
                    import time
                    time.sleep(1.0)

            except Exception as e:
                print(f"    ❌ 错误: {e}")
                continue

        if not audio_segments:
            print("\n❌ 没有成功生成任何音频")
            return None

        print(f"\n✅ 共生成 {len(audio_segments)} 个音频片段")

        # 合并音频
        print("\n🎧 合并音频片段...")
        from pydub import AudioSegment as PyDubSegment

        combined = PyDubSegment.empty()
        total_duration = 0

        for segment in audio_segments:
            audio = PyDubSegment.from_mp3(segment.filepath)
            combined += audio
            total_duration += segment.duration_seconds

            # 章节之间加入2秒静音
            combined += PyDubSegment.silent(duration=2000)

        # 导出最终音频
        final_path = output_path / f"podcast-perfect-days-review-{date_str}.mp3"
        combined.export(str(final_path), format="mp3", bitrate="192k")

        print(f"✅ 播客生成完成!")
        print(f"📝 脚本: {script_path}")
        print(f"🎧 音频: {final_path}")
        print(f"⏱️  时长: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)")

        return {
            "script_path": str(script_path),
            "audio_path": str(final_path),
            "duration": total_duration,
            "section_count": len(sections),
        }

    except ValueError as e:
        print(f"❌ TTS 初始化失败: {e}")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="电影影评播客生成器")
    parser.add_argument(
        "content_file", type=str, help="影评内容文件路径（markdown）"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output", help="输出目录"
    )
    parser.add_argument("--voice-id", type=str, default=None, help="语音ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("🎬 电影影评播客生成器")
    print("=" * 50 + "\n")

    result = generate_movie_review_podcast(
        content_file=args.content_file,
        output_dir=args.output,
        voice_id=args.voice_id,
        verbose=args.verbose,
    )

    if result:
        print("\n" + "=" * 50)
        print("🎉 生成完成!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n❌ 生成失败")
        sys.exit(1)

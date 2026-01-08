#!/usr/bin/env python3
"""
重新生成指定章节的音频
用于修复发音问题
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")


def regenerate_sections(
    content_file: str,
    section_numbers: list[int],
    output_dir: str = "output/2026-01-08/audio",
    voice_id: str = None,
):
    """
    重新生成指定章节的音频

    Args:
        content_file: 内容文件路径
        section_numbers: 要重新生成的章节编号列表（1-based）
        output_dir: 输出目录
        voice_id: 语音ID
    """
    from generators import TTSGenerator

    # 读取内容
    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析章节
    lines = content.split("\n")
    sections = []
    current_section = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):
            continue

        if line.startswith("## "):
            if current_section and current_text:
                sections.append({
                    "title": current_section,
                    "content": "\n\n".join(current_text)
                })
            current_section = line[3:].strip()
            current_text = []
            continue

        if line.startswith("**") and ":" in line and len(line) < 50:
            continue

        if line == "---":
            continue

        if current_section:
            current_text.append(line)

    if current_section and current_text:
        sections.append({
            "title": current_section,
            "content": "\n\n".join(current_text)
        })

    print(f"📖 共解析 {len(sections)} 个章节")
    print(f"🔄 需要重新生成: {section_numbers}")
    print("-" * 50)

    # 初始化 TTS
    try:
        tts = TTSGenerator()
        if voice_id:
            tts.voice_id = voice_id

        if not tts.voice_id:
            print("❌ 未配置 voice_id")
            return False

        print(f"🎤 使用语音 ID: {tts.voice_id[:16]}...\n")

    except ValueError as e:
        print(f"❌ TTS 初始化失败: {e}")
        return False

    # 重新生成指定章节
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    success_count = 0

    for section_num in section_numbers:
        if section_num < 1 or section_num > len(sections):
            print(f"⚠️ 章节 {section_num} 不存在，跳过")
            continue

        section = sections[section_num - 1]
        print(f"[{section_num}/{len(sections)}] {section['title'][:40]}...")

        text = f"{section['title']}\n\n{section['content']}"
        audio_path = str(output_path / f"section_{section_num:02d}.mp3")

        try:
            result = tts.generate_audio(text, audio_path)
            if result:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(audio_path)
                duration = len(audio) / 1000.0
                print(f"  ✅ 重新生成成功 ({duration:.1f}秒)\n")
                success_count += 1
            else:
                print(f"  ❌ 生成失败\n")

            time.sleep(1.0)  # API 速率限制

        except Exception as e:
            print(f"  ❌ 错误: {e}\n")
            continue

    print("-" * 50)
    print(f"✅ 重新生成完成: {success_count}/{len(section_numbers)} 个章节")

    return success_count == len(section_numbers)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="重新生成指定章节音频")
    parser.add_argument("content_file", type=str, help="内容文件路径")
    parser.add_argument(
        "--sections", "-s",
        type=str,
        required=True,
        help="要重新生成的章节编号（逗号分隔，如: 1,5,10）"
    )
    parser.add_argument("--output", "-o", type=str, default="output/2026-01-08/audio", help="输出目录")
    parser.add_argument("--voice-id", type=str, default=None, help="语音ID")

    args = parser.parse_args()

    # 解析章节编号
    section_numbers = [int(n.strip()) for n in args.sections.split(",")]

    print("\n" + "=" * 50)
    print("🔄 重新生成章节音频")
    print("=" * 50 + "\n")

    result = regenerate_sections(
        content_file=args.content_file,
        section_numbers=section_numbers,
        output_dir=args.output,
        voice_id=args.voice_id,
    )

    if result:
        print("\n✅ 所有章节重新生成成功！")
        print("💡 提示: 需要重新运行合并脚本来更新最终音频")
    else:
        print("\n⚠️ 部分章节重新生成失败")

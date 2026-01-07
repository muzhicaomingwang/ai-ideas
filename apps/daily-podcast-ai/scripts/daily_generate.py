#!/usr/bin/env python3
"""
每日播客生成脚本
整合所有模块，一键生成完整的播客音频
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / ".env")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="每日播客生成器 - 将新闻自动转换为播客音频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成今日播客（使用AI摘要）
  python daily_generate.py

  # 生成指定日期的播客
  python daily_generate.py --date 2026-01-07

  # 限制文章数量
  python daily_generate.py --max-articles 5

  # 仅生成脚本（不合成音频）
  python daily_generate.py --script-only

  # 使用简单摘要（不调用OpenAI）
  python daily_generate.py --no-ai

  # 指定输出目录
  python daily_generate.py --output ./my-podcasts
        """
    )

    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="播客日期 (格式: YYYY-MM-DD，默认为今天)"
    )

    parser.add_argument(
        "--max-articles", "-n",
        type=int,
        default=10,
        help="最大文章数量 (默认: 10)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="输出目录 (默认: output)"
    )

    parser.add_argument(
        "--script-only",
        action="store_true",
        help="仅生成脚本，不合成音频"
    )

    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="使用简单摘要，不调用 OpenAI API"
    )

    parser.add_argument(
        "--no-tts",
        action="store_true",
        help="跳过 TTS 语音合成（需要已有音频文件）"
    )

    parser.add_argument(
        "--bgm",
        type=str,
        default=None,
        help="背景音乐文件路径"
    )

    parser.add_argument(
        "--intro-jingle",
        type=str,
        default=None,
        help="片头音效文件路径"
    )

    parser.add_argument(
        "--outro-jingle",
        type=str,
        default=None,
        help="片尾音效文件路径"
    )

    parser.add_argument(
        "--group-by-category",
        action="store_true",
        help="按分类组织新闻"
    )

    parser.add_argument(
        "--voice-id",
        type=str,
        default=None,
        help="ElevenLabs 语音 ID（覆盖配置文件）"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演示模式，不实际生成文件"
    )

    args = parser.parse_args()

    # 解析日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ 日期格式错误: {args.date}，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    else:
        target_date = datetime.now()

    date_str = target_date.strftime("%Y-%m-%d")

    # 打印横幅
    print_banner(date_str)

    if args.dry_run:
        print("🔍 演示模式 - 不会生成实际文件")
        print("-" * 50)

    # 运行生成流程
    try:
        result = generate_podcast(
            target_date=target_date,
            max_articles=args.max_articles,
            output_dir=args.output,
            script_only=args.script_only,
            use_ai=not args.no_ai,
            skip_tts=args.no_tts,
            bgm_path=args.bgm,
            intro_jingle_path=args.intro_jingle,
            outro_jingle_path=args.outro_jingle,
            group_by_category=args.group_by_category,
            voice_id=args.voice_id,
            verbose=args.verbose,
            dry_run=args.dry_run
        )

        if result:
            print_summary(result)
            sys.exit(0)
        else:
            print("\n❌ 播客生成失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_banner(date_str: str):
    """打印横幅"""
    print()
    print("=" * 50)
    print("🎙️  每日播客生成器")
    print("=" * 50)
    print(f"📅 日期: {date_str}")
    print()


def print_summary(result: dict):
    """打印生成摘要"""
    print()
    print("=" * 50)
    print("🎉 播客生成完成!")
    print("=" * 50)

    if result.get("script_path"):
        print(f"📝 脚本文件: {result['script_path']}")

    if result.get("audio_path"):
        print(f"🎧 音频文件: {result['audio_path']}")

    if result.get("duration"):
        minutes = result["duration"] / 60
        print(f"⏱️  时长: {result['duration']:.1f} 秒 ({minutes:.1f} 分钟)")

    if result.get("article_count"):
        print(f"📰 文章数: {result['article_count']}")

    if result.get("categories"):
        print(f"📂 分类: {', '.join(result['categories'])}")

    print()


def generate_podcast(
    target_date: datetime,
    max_articles: int = 10,
    output_dir: str = "output",
    script_only: bool = False,
    use_ai: bool = True,
    skip_tts: bool = False,
    bgm_path: str = None,
    intro_jingle_path: str = None,
    outro_jingle_path: str = None,
    group_by_category: bool = False,
    voice_id: str = None,
    verbose: bool = False,
    dry_run: bool = False
) -> dict:
    """
    生成播客的主流程

    Args:
        target_date: 目标日期
        max_articles: 最大文章数
        output_dir: 输出目录
        script_only: 仅生成脚本
        use_ai: 使用AI摘要
        skip_tts: 跳过TTS
        bgm_path: 背景音乐路径
        intro_jingle_path: 片头音效路径
        outro_jingle_path: 片尾音效路径
        group_by_category: 按分类分组
        voice_id: 语音ID
        verbose: 详细输出
        dry_run: 演示模式

    Returns:
        结果字典
    """
    from news_sources import RSSFetcher
    from processors.summarizer import ArticleSummarizer, SimpleSummarizer
    from processors.script_writer import ScriptWriter
    from generators import TTSGenerator, AudioMixer

    date_str = target_date.strftime("%Y-%m-%d")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = {
        "date": date_str,
        "script_path": None,
        "audio_path": None,
        "duration": None,
        "article_count": 0,
        "categories": []
    }

    # ========== 步骤 1: 获取新闻 ==========
    print("📰 步骤 1/5: 获取新闻")
    print("-" * 40)

    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    if not articles:
        print("❌ 没有获取到任何文章")
        return None

    # 限制文章数量
    articles = articles[:max_articles]
    print(f"✅ 获取到 {len(articles)} 篇文章")

    if dry_run:
        for i, article in enumerate(articles, 1):
            print(f"   {i}. [{article.category}] {article.title[:40]}...")
        result["article_count"] = len(articles)
        result["categories"] = list(set(a.category for a in articles))
        return result

    # ========== 步骤 2: 内容摘要 ==========
    print("\n📝 步骤 2/5: 内容处理")
    print("-" * 40)

    if use_ai:
        try:
            summarizer = ArticleSummarizer()
            print("  使用 AI 摘要 (OpenAI GPT-4o-mini)")
        except ValueError as e:
            print(f"  ⚠️ {e}")
            print("  降级使用简单摘要")
            summarizer = SimpleSummarizer()
    else:
        summarizer = SimpleSummarizer()
        print("  使用简单摘要")

    summarized = summarizer.summarize_batch(articles, show_progress=verbose)
    print(f"✅ 处理完成 {len(summarized)} 篇文章")

    # ========== 步骤 3: 生成脚本 ==========
    print("\n📜 步骤 3/5: 生成脚本")
    print("-" * 40)

    writer = ScriptWriter()
    script = writer.generate_script(
        summarized,
        date=target_date,
        group_by_category=group_by_category
    )

    # 保存脚本
    script_path = script.save_to_file(str(output_path))
    result["script_path"] = script_path
    result["article_count"] = script.total_articles
    result["categories"] = script.categories

    print(f"✅ 脚本已保存: {script_path}")

    if verbose:
        print("\n--- 脚本预览 ---")
        full_text = script.to_full_text()
        preview = full_text[:500] + "..." if len(full_text) > 500 else full_text
        print(preview)
        print("--- 预览结束 ---\n")

    if script_only:
        print("\n⏭️ 跳过音频生成（--script-only 模式）")
        return result

    # ========== 步骤 4: 语音合成 ==========
    print("\n🎙️ 步骤 4/5: 语音合成")
    print("-" * 40)

    audio_dir = output_path / "audio"
    audio_segments = []

    if skip_tts:
        print("  ⏭️ 跳过 TTS（--no-tts 模式）")
        # 尝试查找已存在的音频文件
        existing_files = list(audio_dir.glob(f"{date_str}_*.mp3"))
        if existing_files:
            print(f"  📂 找到 {len(existing_files)} 个已存在的音频文件")
            # 创建模拟的 AudioSegment 对象
            from dataclasses import dataclass

            @dataclass
            class MockSegment:
                filepath: str

            audio_segments = [MockSegment(filepath=str(f)) for f in sorted(existing_files)]
        else:
            print("  ⚠️ 没有找到已存在的音频文件，无法继续")
            return result
    else:
        try:
            tts = TTSGenerator()
            if voice_id:
                tts.voice_id = voice_id

            if not tts.voice_id:
                print("  ❌ 未配置 voice_id，请先运行 setup_voice.py 设置语音")
                print("     或使用 --voice-id 参数指定")
                return result

            print(f"  🎤 使用语音 ID: {tts.voice_id[:16]}...")
            audio_segments = tts.generate_podcast_audio(
                script,
                output_dir=str(audio_dir),
                show_progress=True
            )

            if not audio_segments:
                print("  ❌ 音频生成失败")
                return result

            print(f"✅ 生成 {len(audio_segments)} 个音频片段")

        except ValueError as e:
            print(f"  ❌ TTS 初始化失败: {e}")
            return result

    # ========== 步骤 5: 音频后处理 ==========
    print("\n🎧 步骤 5/5: 音频后处理")
    print("-" * 40)

    mixer = AudioMixer()
    final_audio_path = str(output_path / f"podcast-{date_str}.mp3")

    final = mixer.create_final_podcast(
        audio_segments,
        final_audio_path,
        bgm_path=bgm_path,
        intro_jingle_path=intro_jingle_path,
        outro_jingle_path=outro_jingle_path,
        show_progress=True
    )

    if final:
        result["audio_path"] = final.filepath
        result["duration"] = final.duration_seconds
        print(f"✅ 播客音频生成完成: {final.filepath}")
    else:
        print("  ❌ 音频后处理失败")

    return result


if __name__ == "__main__":
    main()

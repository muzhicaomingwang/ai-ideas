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
from news_sources.rss_fetcher import Article

# 加载环境变量
load_dotenv(project_root / ".env")


def filter_low_quality_news(articles: list) -> list:
    """
    过滤低质量新闻
    
    排除：股票减持/增持、ST股票、纯财务公告等
    保留：有实质内容的科技新闻
    """
    # 严格排除的关键词（标题包含即排除）
    exclude_keywords = [
        "减持", "增持", "*ST", "ST声迅", "ST股",
        "涨停", "跌停", "连板",
        "公司股份", "股东减持",
        "主力买", "主力资金", "A股主力"
    ]
    
    # 保留关键词（即使有其他关键词也保留）
    keep_keywords = [
        "AI", "人工智能", "大模型", "GPT", "Claude",
        "苹果", "Apple", "库克", "Cook",
        "特斯拉", "Tesla", "马斯克",
        "华为", "小米", "吉利",
        "卫星", "航天", "芯片",
        "发布", "推出", "升级"
    ]
    
    filtered = []
    for article in articles:
        title = article.title if hasattr(article, 'title') else ""
        summary = article.summary if hasattr(article, 'summary') else ""
        content = title + summary
        
        # 检查是否包含保留关键词
        has_keep_keyword = any(kw in content for kw in keep_keywords)
        
        # 检查是否包含排除关键词
        has_exclude_keyword = any(kw in title for kw in exclude_keywords)
        
        # 如果有保留关键词，优先保留；否则排除低质量
        if has_keep_keyword or not has_exclude_keyword:
            filtered.append(article)
    
    removed = len(articles) - len(filtered)
    if removed > 0:
        print(f"  🗑️ 移除 {removed} 篇低质量新闻")
    
    return filtered


def load_articles_from_cache(date_str: str) -> list:
    """
    从缓存加载新闻

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        Article 对象列表
    """
    import json

    cache_path = project_root / "cache" / f"{date_str}-news.json"

    if not cache_path.exists():
        print(f"  ⚠️ 缓存文件不存在: {cache_path}")
        return []

    with open(cache_path, "r", encoding="utf-8") as f:
        news_list = json.load(f)

    # 转换为 Article 对象
    articles = []
    for news in news_list:
        article = Article(
            title=news["title"],
            summary=news["summary"],
            link=news["link"],
            source=news["source"],
            category=news["category"],
            published=datetime.fromisoformat(news["published"]) if news.get("published") else None
        )
        articles.append(article)

    print(f"  📂 从缓存加载 {len(articles)} 篇新闻")
    return articles


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

    parser.add_argument(
        "--from-cache",
        action="store_true",
        help="从缓存读取新闻并使用 AI 优选（每小时收集模式）"
    )

    parser.add_argument(
        "--classic",
        action="store_true",
        help="使用经典单人播报模式 (禁用 Deep Dive 双人对话)"
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
            dry_run=args.dry_run,
            from_cache=args.from_cache,
            deep_dive=not args.classic
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
    dry_run: bool = False,
    from_cache: bool = False,
    deep_dive: bool = True
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
        deep_dive: 是否使用深度对话模式 (Deep Dive)

    Returns:
        结果字典
    """
    from news_sources import RSSFetcher
    from processors.summarizer import ArticleSummarizer, SimpleSummarizer
    from processors.script_writer import ScriptWriter
    from processors.dialogue_writer import DialogueWriter
    from generators import TTSGenerator, AudioMixer
    import yaml

    date_str = target_date.strftime("%Y-%m-%d")
    
    # 加载配置以获取主持人名称
    config_path = project_root / "config" / "voice.yaml"
    host_a_slug = "host_a"
    host_b_slug = "host_b"
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            hosts = config.get("hosts", {})
            
            # 简单的中文名转拼音映射 (针对特定需求)
            name_map = {
                "植萌": "zhimeng",
                "小雅": "xiaoya",
                "Alex": "alex",
                "Jamie": "jamie"
            }
            
            h_a = hosts.get("host_a", {}).get("name", "HostA")
            h_b = hosts.get("host_b", {}).get("name", "HostB")
            
            host_a_slug = name_map.get(h_a, h_a.lower())
            host_b_slug = name_map.get(h_b, h_b.lower())

    # 构建新的输出路径结构: output/{date}/dailytechnews/
    base_output_path = Path(output_dir)
    if deep_dive:
        output_path = base_output_path / date_str / "dailytechnews"
    else:
        output_path = base_output_path
        
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

    if from_cache:
        # 从缓存读取全天收集的新闻
        articles = load_articles_from_cache(date_str)
        if not articles:
            print("⚠️ 缓存为空，回退到实时获取")
            from_cache = False  # 回退

    if not from_cache:
        # 实时获取新闻
        fetcher = RSSFetcher()
        raw_articles = fetcher.fetch_all()

        if not raw_articles:
            print("❌ 没有获取到任何文章")
            return None

        articles = raw_articles

    print(f"📊 候选新闻: {len(articles)} 篇")

    # 过滤低质量新闻
    articles = filter_low_quality_news(articles)
    print(f"📊 过滤后: {len(articles)} 篇")

    # 使用 AI 优选
    if from_cache and len(articles) > max_articles:
        print(f"🤖 步骤 1.5: AI 优选新闻 (从 {len(articles)} 篇中选出 {max_articles} 篇)")
        print("-" * 40)
        from processors.news_ranker import NewsRanker
        ranker = NewsRanker()
        articles = ranker.rank_articles(articles, max_count=max_articles)
    else:
        # 简单截取
        articles = articles[:max_articles]

    print(f"✅ 最终选定 {len(articles)} 篇文章")

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
    print(f"\n📜 步骤 3/5: 生成脚本 ({'Deep Dive 对话模式' if deep_dive else '单人播报模式'})")
    print("-" * 40)

    if deep_dive:
        # 优先使用 Claude 对话生成器
        try:
            from processors.claude_dialogue_writer import ClaudeDialogueWriter
            writer = ClaudeDialogueWriter()
            print("  🤖 使用 Anthropic Claude 生成高质量对话")
        except (ImportError, ValueError) as e:
            print(f"  ⚠️ Claude 不可用 ({e})，回退到 Gemini")
            writer = DialogueWriter()
        
        script = writer.generate_dialogue(summarized, date=target_date)
        result["article_count"] = len(summarized)
    else:
        writer = ScriptWriter()
        script = writer.generate_script(
            summarized,
            date=target_date,
            group_by_category=group_by_category
        )
        result["article_count"] = script.total_articles
        result["categories"] = script.categories

    # 保存脚本
    script_path = script.save_to_file(str(output_path))
    result["script_path"] = script_path
    
    print(f"✅ 脚本已保存: {script_path}")

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
            
            if deep_dive:
                # Deep Dive 双人对话模式
                audio_segments = tts.generate_dialogue_audio(
                    script,
                    output_dir=str(audio_dir),
                    show_progress=True
                )
            else:
                # 单人播报模式
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
    
    # 构造文件名: podcast-{date}-{host_a}-{host_b}.mp3
    if deep_dive:
        filename = f"podcast-{date_str}-{host_a_slug}-{host_b_slug}.mp3"
    else:
        filename = f"podcast-{date_str}.mp3"
        
    final_audio_path = str(output_path / filename)

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

    # ========== 步骤 6: 封面生成 ==========
    print("\n🎨 步骤 6/6: 封面生成")
    print("-" * 40)
    
    try:
        # 使用 PIL 生成封面（更稳定，无需外部 API）
        from generate_cover import generate_cover as pil_generate_cover
        
        cover_filename = f"cover-{date_str}.png"
        cover_path = str(output_path / cover_filename)
        
        podcast_title = "今日科技早报"
        if deep_dive:
            podcast_title += " Deep Dive"
            
        generated_cover = pil_generate_cover(
            date=target_date,
            output_path=cover_path,
            title=podcast_title,
            article_count=len(summarized)
        )
        
        if generated_cover:
            print(f"✅ 封面生成完成: {generated_cover}")
            result["cover_path"] = generated_cover
        else:
            print("❌ 封面生成失败")
            
    except Exception as e:
        print(f"❌ 封面生成出错: {e}")
        if verbose:
            import traceback
            traceback.print_exc()

    return result


if __name__ == "__main__":
    main()

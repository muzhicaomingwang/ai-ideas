#!/usr/bin/env python3
"""
每日小红书研究播客生成脚本
整合所有模块，一键生成完整的播客内容
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / ".env")

# 导入模块
from scrapers.newrank_scraper import NewrankScraper
from analyzers.topic_analyzer import TopicAnalyzer
from analyzers.trend_analyzer import TrendAnalyzer
from analyzers.insight_generator import InsightGenerator
from processors.dialogue_writer import DialogueWriter, PodcastScript
from generators.tts_generator import TTSGenerator
from generators.audio_mixer import AudioMixer
from generators.cover_generator import CoverGenerator
from generators.report_generator import ReportGenerator
from utils.logger import get_logger
from utils.cache import CacheManager

logger = get_logger()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="每日小红书研究播客生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成今日播客（完整流程）
  python scripts/daily_generate.py

  # 生成指定日期
  python scripts/daily_generate.py --date 2026-01-15

  # 仅生成报告和封面（跳过音频）
  python scripts/daily_generate.py --skip-audio

  # 使用缓存数据（跳过数据抓取）
  python scripts/daily_generate.py --skip-scrape

  # 指定输出目录
  python scripts/daily_generate.py --output ./custom-output
        """,
    )

    # 参数定义
    parser.add_argument(
        "--date",
        "-d",
        type=str,
        default=None,
        help="指定日期 (格式: YYYY-MM-DD，默认为今天)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output",
        help="输出目录 (默认: output)",
    )

    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="跳过数据抓取，使用缓存数据",
    )

    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="跳过音频生成（仅生成报告和封面）",
    )

    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="跳过报告生成",
    )

    parser.add_argument(
        "--skip-cover",
        action="store_true",
        help="跳过封面生成",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细日志",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演示模式（不实际生成文件）",
    )

    args = parser.parse_args()

    # 解析日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ 日期格式错误: {args.date}（应为 YYYY-MM-DD）")
            sys.exit(1)
    else:
        target_date = datetime.now()

    date_str = target_date.strftime("%Y-%m-%d")

    # 打印横幅
    print_banner(date_str, args.dry_run)

    # 运行生成流程
    try:
        result = generate_podcast(
            target_date=target_date,
            output_dir=args.output,
            skip_scrape=args.skip_scrape,
            skip_audio=args.skip_audio,
            skip_report=args.skip_report,
            skip_cover=args.skip_cover,
            verbose=args.verbose,
            dry_run=args.dry_run,
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
        logger.exception(f"发生错误: {e}")
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


def generate_podcast(
    target_date: datetime,
    output_dir: str = "output",
    skip_scrape: bool = False,
    skip_audio: bool = False,
    skip_report: bool = False,
    skip_cover: bool = False,
    verbose: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    生成播客的主流程

    Args:
        target_date: 目标日期
        output_dir: 输出目录
        skip_scrape: 跳过数据抓取
        skip_audio: 跳过音频生成
        skip_report: 跳过报告生成
        skip_cover: 跳过封面生成
        verbose: 详细日志
        dry_run: 演示模式

    Returns:
        生成结果字典
    """
    date_str = target_date.strftime("%Y-%m-%d")
    output_path = Path(output_dir) / date_str
    output_path.mkdir(parents=True, exist_ok=True)

    result = {
        "date": date_str,
        "success": False,
        "outputs": {},
    }

    # 步骤1: 数据抓取
    print("\n[步骤 1/7] 数据抓取")
    print("-" * 50)

    cache_manager = CacheManager(project_root / "cache")

    if skip_scrape:
        logger.info("  跳过数据抓取，从缓存加载...")
        topics = cache_manager.load_topics(date_str)

        if not topics:
            print(f"  ❌ 缓存中没有 {date_str} 的数据")
            print(f"  提示：移除 --skip-scrape 参数重新抓取")
            return None
    else:
        logger.info("  开始抓取新榜数据...")
        if dry_run:
            print("  🔍 演示模式：跳过实际抓取")
            topics = []
        else:
            scraper = NewrankScraper()
            topics = scraper.fetch_hot_topics(max_count=50)

            if not topics:
                print("  ❌ 未抓取到数据")
                return None

            # 保存到缓存
            cache_manager.save_topics(topics, date_str)

    print(f"  ✓ 获取 {len(topics)} 个热门话题")

    # 步骤2: 话题分析
    print("\n[步骤 2/7] 话题分析")
    print("-" * 50)

    analyzer = TopicAnalyzer()
    analysis_result = analyzer.analyze(topics, date_str)

    print(f"  ✓ 总热度: {analysis_result.total_heat / 10000:.1f}万")
    print(f"  ✓ 提取热词: {len(analysis_result.top_keywords)}个")
    print(f"  ✓ 分类统计: {len(analysis_result.category_stats)}个分类")

    # 步骤3: 趋势分析
    print("\n[步骤 3/7] 趋势分析")
    print("-" * 50)

    trend_analyzer = TrendAnalyzer(cache_dir=project_root / "cache")
    trend_result = trend_analyzer.analyze_trends(topics, date_str)

    # 合并趋势数据到分析结果
    analysis_result.rising_topics = trend_result.get("rising", [])
    analysis_result.new_topics = trend_result.get("new", [])

    print(f"  ✓ 热度上升: {len(analysis_result.rising_topics)}个")
    print(f"  ✓ 新话题: {len(analysis_result.new_topics)}个")

    # 步骤4: AI洞察生成
    print("\n[步骤 4/7] AI洞察生成")
    print("-" * 50)

    insight_generator = InsightGenerator()
    ai_insight = insight_generator.generate(analysis_result, topics)

    print(f"  ✓ 用户行为洞察: {len(ai_insight.user_behavior)}条")
    print(f"  ✓ 趋势预测: {len(ai_insight.trend_predictions)}条")
    print(f"  ✓ 创作者建议: {len(ai_insight.creator_tips)}条")

    # 步骤5: 生成对话脚本
    print("\n[步骤 5/7] 生成播客脚本")
    print("-" * 50)

    dialogue_writer = DialogueWriter()
    script = dialogue_writer.generate(
        analysis_result=analysis_result,
        ai_insight=ai_insight,
        target_duration=540,  # 9分钟
    )

    # 保存脚本
    if not dry_run:
        json_path, md_path = script.save_to_file(output_path)
        result["outputs"]["script_json"] = str(json_path)
        result["outputs"]["script_md"] = str(md_path)
        print(f"  ✓ 脚本已保存")
        print(f"    - JSON: {json_path.name}")
        print(f"    - Markdown: {md_path.name}")
        print(f"  ✓ 对话行数: {len(script.lines)}")

    # 步骤6: 生成音频（可选）
    if not skip_audio and not dry_run:
        print("\n[步骤 6/7] 生成播客音频")
        print("-" * 50)

        try:
            # 6.1 TTS语音合成
            print("  [6.1] 语音合成...")
            tts_generator = TTSGenerator(config_path=project_root / "config/voice.yaml")

            audio_segments = tts_generator.generate_dialogue_audio(
                script=script, output_dir=output_path / "audio_segments"
            )

            print(f"    ✓ 生成 {len(audio_segments)} 个音频片段")

            # 6.2 音频混音
            print("  [6.2] 音频混音...")
            audio_mixer = AudioMixer()

            # 合成最终音频
            final_audio_path = output_path / f"podcast-{date_str}.mp3"
            mixed_audio = audio_mixer.mix_dialogue_podcast(
                audio_segments=audio_segments,
                output_path=final_audio_path,
                bgm_path=None,  # 可选：添加背景音乐
                intro_jingle_path=None,  # 可选：片头音效
                outro_jingle_path=None,  # 可选：片尾音效
            )

            result["outputs"]["audio"] = str(final_audio_path)
            print(f"    ✓ 音频已保存: {final_audio_path.name}")
            print(f"    ✓ 时长: {mixed_audio.duration_seconds:.1f}秒")

        except Exception as e:
            logger.error(f"音频生成失败: {e}")
            print(f"  ⚠️ 音频生成失败: {e}")
    else:
        print("\n[步骤 6/7] 音频生成 - 已跳过")

    # 步骤7: 生成附件（报告和封面）
    print("\n[步骤 7/7] 生成附件")
    print("-" * 50)

    # 7.1 Markdown报告
    if not skip_report and not dry_run:
        print("  [7.1] 生成Markdown报告...")
        report_generator = ReportGenerator()
        report_path = output_path / f"report-{date_str}.md"

        report_generator.generate(
            analysis_result=analysis_result,
            ai_insight=ai_insight,
            output_path=report_path,
        )

        result["outputs"]["report"] = str(report_path)
        print(f"    ✓ 报告已保存: {report_path.name}")
    else:
        print("  [7.1] Markdown报告 - 已跳过")

    # 7.2 播客封面
    if not skip_cover and not dry_run:
        print("  [7.2] 生成播客封面...")
        cover_generator = CoverGenerator()
        cover_path = output_path / f"cover-{date_str}.png"

        cover_generator.generate(
            date=date_str,
            title="每日小红书研究",
            stats_text=f"{analysis_result.total_topics}个话题 · {analysis_result.total_heat / 10000:.0f}万热度",
            output_path=cover_path,
        )

        result["outputs"]["cover"] = str(cover_path)
        print(f"    ✓ 封面已保存: {cover_path.name}")
    else:
        print("  [7.2] 播客封面 - 已跳过")

    result["success"] = True
    return result


def print_banner(date_str: str, dry_run: bool = False):
    """打印横幅"""
    mode_tag = " [演示模式]" if dry_run else ""
    print()
    print("=" * 60)
    print(f"🎙️  每日小红书研究播客生成器{mode_tag}")
    print("=" * 60)
    print(f"📅 日期: {date_str}")
    print()


def print_summary(result: dict):
    """打印生成摘要"""
    print()
    print("=" * 60)
    print("🎉 播客生成完成！")
    print("=" * 60)
    print()

    outputs = result.get("outputs", {})

    if "script_json" in outputs:
        print(f"📝 脚本文件:")
        print(f"   - JSON: {Path(outputs['script_json']).name}")
        if "script_md" in outputs:
            print(f"   - Markdown: {Path(outputs['script_md']).name}")

    if "audio" in outputs:
        print(f"🎧 音频文件: {Path(outputs['audio']).name}")

    if "report" in outputs:
        print(f"📄 研究报告: {Path(outputs['report']).name}")

    if "cover" in outputs:
        print(f"🎨 播客封面: {Path(outputs['cover']).name}")

    print()
    print("查看输出目录:")
    print(f"  ls {Path(outputs.get('audio', 'output')).parent}")
    print()


if __name__ == "__main__":
    main()

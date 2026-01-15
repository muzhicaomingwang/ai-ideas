#!/usr/bin/env python3
"""
安装验证脚本
检查所有模块是否正确安装和配置
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def check_imports():
    """检查模块导入"""
    print_section("📦 检查模块导入")

    modules = [
        ("scrapers.newrank_scraper", "NewrankScraper"),
        ("scrapers.browser_manager", "BrowserManager"),
        ("models.topic", "XHSTopic, TopicAnalysisResult, AIInsight"),
        ("analyzers.topic_analyzer", "TopicAnalyzer"),
        ("analyzers.trend_analyzer", "TrendAnalyzer"),
        ("analyzers.insight_generator", "InsightGenerator"),
        ("processors.dialogue_writer", "DialogueWriter, PodcastScript"),
        ("generators.tts_generator", "TTSGenerator"),
        ("generators.audio_mixer", "AudioMixer"),
        ("generators.cover_generator", "CoverGenerator"),
        ("generators.report_generator", "ReportGenerator"),
        ("utils.logger", "get_logger"),
        ("utils.cache", "CacheManager"),
    ]

    failed = []
    for module_path, class_name in modules:
        try:
            exec(f"from {module_path} import {class_name}")
            print(f"  ✓ {module_path}")
        except Exception as e:
            print(f"  ✗ {module_path} - {e}")
            failed.append(module_path)

    return len(failed) == 0


def check_dependencies():
    """检查Python依赖"""
    print_section("📚 检查Python依赖")

    deps = [
        "playwright",
        "google.generativeai",
        "pydantic",
        "pandas",
        "sklearn",
        "jieba",
        "PIL",
        "pydub",
        "elevenlabs",
        "dotenv",
        "yaml",
    ]

    failed = []
    for dep in deps:
        try:
            __import__(dep.split(".")[0])
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep}")
            failed.append(dep)

    if failed:
        print(f"\n  ⚠️ 缺失 {len(failed)} 个依赖")
        print("  运行: poetry install")
        return False

    return True


def check_config_files():
    """检查配置文件"""
    print_section("⚙️ 检查配置文件")

    config_files = [
        "config/scraper.yaml",
        "config/voice.yaml",
        ".env.example",
    ]

    missing = []
    for filepath in config_files:
        path = Path(filepath)
        if path.exists():
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} (缺失)")
            missing.append(filepath)

    return len(missing) == 0


def check_env_vars():
    """检查环境变量"""
    print_section("🔐 检查环境变量")

    import os
    from dotenv import load_dotenv

    load_dotenv()

    vars_to_check = [
        ("GOOGLE_API_KEY", "Google Gemini API密钥", False),
        ("GEMINI_API_KEY", "Google Gemini API密钥（备选）", False),
        ("ELEVENLABS_API_KEY", "ElevenLabs TTS密钥", False),
    ]

    has_google = False
    has_elevenlabs = False

    for var_name, description, required in vars_to_check:
        value = os.getenv(var_name)
        if value and value != f"your_{var_name.lower()}":
            print(f"  ✓ {var_name} 已配置")
            if "GOOGLE" in var_name or "GEMINI" in var_name:
                has_google = True
            if "ELEVENLABS" in var_name:
                has_elevenlabs = True
        else:
            print(f"  ⚠️ {var_name} 未配置 ({description})")

    if not has_google:
        print("\n  ❌ 缺少 Google API 密钥")
        print("  设置: export GOOGLE_API_KEY=your_key")
        print("  或在 .env 文件中配置")

    if not has_elevenlabs:
        print("\n  ⚠️ 缺少 ElevenLabs API 密钥")
        print("  音频生成功能将不可用")
        print("  可以使用 --skip-audio 跳过")

    return has_google


def check_directories():
    """检查目录结构"""
    print_section("📁 检查目录结构")

    required_dirs = [
        "src/scrapers",
        "src/models",
        "src/analyzers",
        "src/processors",
        "src/generators",
        "src/utils",
        "config",
        "scripts",
        "docs",
    ]

    auto_create_dirs = ["output", "logs", "cache"]

    missing = []
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ (缺失)")
            missing.append(dir_path)

    # 自动创建输出目录
    for dir_path in auto_create_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✨ {dir_path}/ (已创建)")
        else:
            print(f"  ✓ {dir_path}/")

    return len(missing) == 0


def check_playwright():
    """检查Playwright浏览器"""
    print_section("🌐 检查Playwright浏览器")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # 尝试启动chromium
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("  ✓ Playwright Chromium 已安装")
                return True
            except Exception as e:
                print(f"  ✗ Playwright Chromium 未安装")
                print(f"  运行: poetry run playwright install chromium")
                return False

    except Exception as e:
        print(f"  ✗ Playwright 导入失败: {e}")
        return False


def main():
    """主函数"""
    print()
    print("🔍 小红书研究播客 - 安装验证")
    print()

    checks = [
        ("模块导入", check_imports),
        ("Python依赖", check_dependencies),
        ("配置文件", check_config_files),
        ("目录结构", check_directories),
        ("环境变量", check_env_vars),
        ("Playwright浏览器", check_playwright),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n  ❌ 检查失败: {e}")
            results[name] = False

    # 打印总结
    print_section("📊 验证总结")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print()
    print(f"  通过: {passed}/{total}")

    if passed == total:
        print()
        print("  🎉 所有检查通过！你可以开始使用了。")
        print()
        print("  下一步:")
        print("    1. 配置 .env 文件（如未配置）")
        print("    2. 运行: poetry run python scripts/daily_generate.py --skip-audio")
        print("    3. 查看: ls output/$(date +%Y-%m-%d)/")
        print()
        return 0
    else:
        print()
        print("  ⚠️ 有些检查未通过，请修复后重试。")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

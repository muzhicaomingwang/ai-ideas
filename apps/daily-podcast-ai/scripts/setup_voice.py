#!/usr/bin/env python3
"""
ElevenLabs 语音设置脚本
列出可用语音、克隆语音、配置语音ID
"""

import argparse
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / ".env")

import yaml
from elevenlabs import ElevenLabs


def get_client() -> ElevenLabs:
    """获取 ElevenLabs 客户端"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ 未设置 ELEVENLABS_API_KEY 环境变量")
        print("   请在 .env 文件中添加: ELEVENLABS_API_KEY=your_api_key")
        sys.exit(1)
    return ElevenLabs(api_key=api_key)


def list_voices(client: ElevenLabs, show_all: bool = False):
    """列出可用语音"""
    print("\n🎤 可用语音列表")
    print("=" * 60)

    try:
        response = client.voices.get_all()
        voices = response.voices

        # 分类显示
        premade = [v for v in voices if v.category == "premade"]
        cloned = [v for v in voices if v.category == "cloned"]
        professional = [v for v in voices if v.category == "professional"]

        if cloned:
            print("\n📌 你的克隆语音:")
            print("-" * 40)
            for voice in cloned:
                labels = voice.labels or {}
                accent = labels.get("accent", "")
                gender = labels.get("gender", "")
                age = labels.get("age", "")
                desc = " | ".join(filter(None, [accent, gender, age]))
                print(f"  🎙️ {voice.name}")
                print(f"     ID: {voice.voice_id}")
                if desc:
                    print(f"     标签: {desc}")
                print()

        if professional:
            print("\n⭐ 专业语音:")
            print("-" * 40)
            for voice in professional[:5]:  # 只显示前5个
                print(f"  🎤 {voice.name} ({voice.voice_id[:12]}...)")

        if show_all:
            print("\n🌐 预制语音 (部分):")
            print("-" * 40)
            # 筛选中文/多语言语音
            chinese_voices = []
            for voice in premade:
                labels = voice.labels or {}
                if "chinese" in str(labels).lower() or "multilingual" in voice.name.lower():
                    chinese_voices.append(voice)

            display_voices = chinese_voices if chinese_voices else premade[:10]
            for voice in display_voices[:10]:
                labels = voice.labels or {}
                accent = labels.get("accent", "")
                print(f"  🎤 {voice.name} ({voice.voice_id[:12]}...) {accent}")

        print(f"\n📊 总计: {len(voices)} 个语音")
        print(f"   - 克隆语音: {len(cloned)}")
        print(f"   - 专业语音: {len(professional)}")
        print(f"   - 预制语音: {len(premade)}")

        return voices

    except Exception as e:
        print(f"❌ 获取语音列表失败: {e}")
        return []


def clone_voice(
    client: ElevenLabs,
    name: str,
    audio_files: list[str],
    description: str = ""
):
    """
    克隆语音

    Args:
        client: ElevenLabs 客户端
        name: 语音名称
        audio_files: 音频文件路径列表
        description: 语音描述
    """
    print(f"\n🎙️ 开始克隆语音: {name}")
    print("=" * 60)

    # 检查文件
    valid_files = []
    for filepath in audio_files:
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️ 文件不存在: {filepath}")
            continue

        # 检查文件大小 (最大 10MB)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 10:
            print(f"⚠️ 文件过大 ({size_mb:.1f}MB): {filepath}")
            continue

        valid_files.append(filepath)
        print(f"✅ {path.name} ({size_mb:.2f}MB)")

    if not valid_files:
        print("❌ 没有有效的音频文件")
        return None

    print(f"\n📤 上传 {len(valid_files)} 个音频文件...")

    try:
        # 打开文件
        file_handles = []
        for filepath in valid_files:
            f = open(filepath, "rb")
            file_handles.append(f)

        # 调用克隆 API
        voice = client.clone(
            name=name,
            description=description or f"克隆语音 - {name}",
            files=file_handles
        )

        # 关闭文件
        for f in file_handles:
            f.close()

        print(f"\n🎉 语音克隆成功!")
        print(f"   名称: {voice.name}")
        print(f"   ID: {voice.voice_id}")

        return voice

    except Exception as e:
        print(f"❌ 语音克隆失败: {e}")
        return None


def set_voice_id(voice_id: str):
    """
    设置语音 ID 到配置文件

    Args:
        voice_id: 语音 ID
    """
    config_path = project_root / "config" / "voice.yaml"

    print(f"\n⚙️ 配置语音 ID")
    print("=" * 60)
    print(f"   语音 ID: {voice_id}")
    print(f"   配置文件: {config_path}")

    # 加载现有配置
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    # 更新配置
    if "tts" not in config:
        config["tts"] = {}

    old_id = config["tts"].get("voice_id")
    config["tts"]["voice_id"] = voice_id

    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存配置
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    if old_id:
        print(f"   原 ID: {old_id[:16]}...")
    print(f"✅ 配置已更新")


def test_voice(client: ElevenLabs, voice_id: str, text: str = None):
    """
    测试语音

    Args:
        client: ElevenLabs 客户端
        voice_id: 语音 ID
        text: 测试文本
    """
    if text is None:
        text = "大家好，欢迎收听今日科技早报。我是你的AI播报员，接下来为大家带来今天的科技新闻。"

    print(f"\n🎧 测试语音")
    print("=" * 60)
    print(f"   语音 ID: {voice_id[:16]}...")
    print(f"   测试文本: {text[:50]}...")

    try:
        # 获取语音信息
        voice = client.voices.get(voice_id)
        print(f"   语音名称: {voice.name}")

        # 生成测试音频
        print("\n🔊 生成测试音频...")

        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # 保存测试音频
        output_dir = project_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "test_voice.mp3"

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"\n✅ 测试音频已保存: {output_path}")
        print("\n   可以使用以下命令播放:")
        print(f"   macOS: afplay {output_path}")
        print(f"   Linux: mpv {output_path}")
        print(f"   Windows: start {output_path}")

        return str(output_path)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None


def get_account_info(client: ElevenLabs):
    """获取账户信息"""
    print("\n👤 账户信息")
    print("=" * 60)

    try:
        user = client.user.get()
        subscription = user.subscription

        print(f"   用户 ID: {user.xi_api_key[:8]}...")

        if subscription:
            print(f"   套餐: {subscription.tier}")
            print(f"   字符配额: {subscription.character_limit:,}")
            print(f"   已使用: {subscription.character_count:,}")
            remaining = subscription.character_limit - subscription.character_count
            print(f"   剩余: {remaining:,} ({remaining/subscription.character_limit*100:.1f}%)")

            if hasattr(subscription, "voice_limit"):
                print(f"   语音配额: {subscription.voice_limit}")

    except Exception as e:
        print(f"⚠️ 获取账户信息失败: {e}")


def interactive_setup(client: ElevenLabs):
    """交互式设置向导"""
    print("\n🚀 ElevenLabs 语音设置向导")
    print("=" * 60)

    # 1. 显示账户信息
    get_account_info(client)

    # 2. 列出可用语音
    voices = list_voices(client)

    # 3. 检查是否有克隆语音
    cloned = [v for v in voices if v.category == "cloned"]

    print("\n" + "=" * 60)
    print("接下来你可以:")
    print("  1. 使用现有语音 - 运行: python setup_voice.py set <voice_id>")
    print("  2. 克隆新语音 - 运行: python setup_voice.py clone <name> <audio_file>")
    print("  3. 测试语音 - 运行: python setup_voice.py test <voice_id>")

    if cloned:
        print(f"\n💡 建议: 你已有 {len(cloned)} 个克隆语音，可以直接使用:")
        for v in cloned:
            print(f"   python setup_voice.py set {v.voice_id}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="ElevenLabs 语音设置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 交互式设置向导
  python setup_voice.py

  # 列出所有可用语音
  python setup_voice.py list
  python setup_voice.py list --all

  # 克隆语音（需要上传音频样本）
  python setup_voice.py clone "我的声音" sample1.mp3 sample2.mp3

  # 设置语音 ID
  python setup_voice.py set <voice_id>

  # 测试语音
  python setup_voice.py test <voice_id>
  python setup_voice.py test <voice_id> --text "自定义测试文本"

  # 查看账户信息
  python setup_voice.py account

语音克隆注意事项:
  - 音频文件最好是清晰的人声录音，无背景噪音
  - 建议使用 1-5 分钟的音频样本
  - 支持 MP3、WAV、M4A 等常见格式
  - 单个文件不超过 10MB
  - 多个音频样本效果更好
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出可用语音")
    list_parser.add_argument("--all", "-a", action="store_true", help="显示所有语音")

    # clone 命令
    clone_parser = subparsers.add_parser("clone", help="克隆语音")
    clone_parser.add_argument("name", help="语音名称")
    clone_parser.add_argument("files", nargs="+", help="音频文件路径")
    clone_parser.add_argument("--description", "-d", default="", help="语音描述")

    # set 命令
    set_parser = subparsers.add_parser("set", help="设置语音 ID")
    set_parser.add_argument("voice_id", help="语音 ID")

    # test 命令
    test_parser = subparsers.add_parser("test", help="测试语音")
    test_parser.add_argument("voice_id", help="语音 ID")
    test_parser.add_argument("--text", "-t", default=None, help="测试文本")

    # account 命令
    subparsers.add_parser("account", help="查看账户信息")

    args = parser.parse_args()

    # 获取客户端
    client = get_client()

    # 执行命令
    if args.command == "list":
        list_voices(client, show_all=args.all)

    elif args.command == "clone":
        voice = clone_voice(client, args.name, args.files, args.description)
        if voice:
            print("\n是否要将此语音设置为默认语音?")
            response = input("输入 y 确认: ").strip().lower()
            if response == "y":
                set_voice_id(voice.voice_id)

    elif args.command == "set":
        set_voice_id(args.voice_id)

    elif args.command == "test":
        test_voice(client, args.voice_id, args.text)

    elif args.command == "account":
        get_account_info(client)

    else:
        # 默认运行交互式向导
        interactive_setup(client)


if __name__ == "__main__":
    main()

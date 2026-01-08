# 漫画短剧生成 - 快速启动指南

使用 Nano Banana (图像生成) + ElevenLabs (配音) 生成AI漫画短剧。

---

## 🚀 快速开始（5分钟）

### 1. 安装依赖

```bash
cd apps/daily-podcast-ai

# 安装所有依赖
pip install -r requirements.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 API Keys

#### 2.1 复制配置模板
```bash
cp .env.example .env
```

#### 2.2 获取 API Keys

| API Key | 获取地址 | 用途 |
|---------|---------|------|
| `GOOGLE_API_KEY` | https://aistudio.google.com/apikey | Nano Banana 图像生成 |
| `ELEVENLABS_API_KEY` | https://elevenlabs.io/app/settings/api-keys | 角色配音 |
| `OPENAI_API_KEY` (可选) | https://platform.openai.com/api-keys | AI剧本生成 |

#### 2.3 填入 `.env` 文件
```bash
GOOGLE_API_KEY=AIzaSy...  # 你的 Google AI API Key
ELEVENLABS_API_KEY=sk_...  # 你的 ElevenLabs API Key
```

### 3. 配置语音ID

运行语音设置脚本，选择2个不同的角色声音：

```bash
python scripts/setup_voice.py
```

这会列出所有可用的语音，记录你选择的 `voice_id`。

### 4. 修改测试剧本

编辑 `scripts/generate_comic_drama.py`，将语音ID替换为你选择的：

```python
# 找到 create_test_script() 函数中的 voice_id 字段
"voice_id": "21m00Tcm4TlvDq8ikWAM",  # 替换为你的角色A语音ID
```

### 5. 运行生成

```bash
python scripts/generate_comic_drama.py
```

### 6. 查看结果

```bash
# 视频保存在:
open output/comic-drama/2026-01-08/AI助手的一天.mp4
```

---

## 📚 详细说明

### 项目结构

```
apps/daily-podcast-ai/
├── src/
│   └── generators/
│       ├── nano_banana_generator.py  # Nano Banana 图像生成
│       ├── tts_generator.py          # ElevenLabs 配音
│       ├── audio_mixer.py            # 音频混合
│       └── video_composer.py         # 视频合成
├── scripts/
│   ├── generate_comic_drama.py       # 主脚本 ← 从这里开始
│   └── setup_voice.py                # 语音配置工具
├── config/
│   ├── voice.yaml                    # 语音配置
│   └── comic.yaml                    # 漫画/视频配置
└── output/
    └── comic-drama/
        └── YYYY-MM-DD/
            ├── frames/               # 生成的图像帧
            ├── audio/                # 配音文件
            └── 短剧标题.mp4         # 最终视频
```

### 剧本格式

```python
script = {
    "title": "你的短剧标题",
    "scenes": [
        {
            "description": "场景描述（用于Nano Banana生成图像）",
            "character": "角色名",
            "dialogue": "对话内容（用于ElevenLabs配音）",
            "voice_id": "ElevenLabs语音ID",
            "duration": 5.0  # 该镜头持续时间（秒）
        },
        # ... 更多场景
    ]
}
```

### 配置文件说明

#### `config/comic.yaml`

```yaml
image_generation:
  model: "gemini-2.5-flash-image"  # 或 "gemini-3-pro-image-preview" (Pro版)
  aspect_ratio: "16:9"  # 或 "9:16" (竖屏), "1:1" (方形)
  style: "comic"  # comic/anime/realistic/manga

video:
  fps: 24  # 帧率
  resolution: "1920x1080"  # 分辨率
  subtitle:
    font_size: 48
    position: "bottom"  # bottom/top/middle
```

---

## 🎯 高级用法

### 自定义剧本

创建 `scripts/my_custom_drama.py`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_comic_drama import generate_comic_drama

# 你的自定义剧本
my_script = {
    "title": "我的第一个AI短剧",
    "scenes": [
        {
            "description": "一个阳光明媚的公园，小女孩在喂鸽子，水彩画风格",
            "character": "小女孩",
            "dialogue": "小鸽子们，快来吃饭啦！",
            "voice_id": "你的语音ID",
            "duration": 4.0
        },
        # 添加更多场景...
    ]
}

# 生成
generate_comic_drama(my_script, output_dir="output/my-drama")
```

### 角色一致性技巧

Nano Banana Pro 支持参考图像来保持角色一致性。代码已自动处理：
- 第一帧生成的角色会作为后续帧的参考
- 在场景描述中保持角色外观描述一致

示例：
```python
# 第一个场景
"description": "一个蓝色机器人，圆形眼睛，友善的笑容，动漫风格"

# 后续场景（保持关键特征描述）
"description": "同样的蓝色机器人在公园里，圆形眼睛，挥手致意，动漫风格"
```

### 批量生成

```python
# scripts/batch_generate.py

scripts = [
    create_script_episode_1(),
    create_script_episode_2(),
    create_script_episode_3(),
]

for i, script in enumerate(scripts):
    print(f"\n{'='*60}")
    print(f"生成第 {i+1}/{len(scripts)} 集")
    print(f"{'='*60}")

    generate_comic_drama(
        script,
        output_dir=f"output/series/episode-{i+1}"
    )
```

---

## 💰 成本估算

### 单集短剧成本（1分钟 = 12帧）

| 项目 | 工具 | 单价 | 数量 | 小计 |
|------|------|------|------|------|
| 图像生成 | Nano Banana | ¥0.008/张 | 12张 | ¥0.096 |
| 角色配音 | ElevenLabs | ¥2.5/分钟 | 1分钟 | ¥2.50 |
| **总计** | | | | **¥2.6/分钟** |

### 升级到 Nano Banana Pro

| 项目 | 普通版 | Pro版 | 差异 |
|------|--------|-------|------|
| 图像质量 | 1080p | 4K | 更高清 |
| 文字渲染 | 良好 | 完美 | 对话框更清晰 |
| 成本 | ¥0.008/张 | ¥0.04/张 | 5倍 |
| **总成本** | **¥2.6/分钟** | **¥3.0/分钟** | +¥0.4 |

**建议**：MVP阶段使用普通版，正式发布升级到Pro版。

---

## 🐛 常见问题

### Q1: 报错 "未设置 GOOGLE_API_KEY"
**解决**：
```bash
# 检查 .env 文件是否存在
ls -la .env

# 检查环境变量是否加载
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### Q2: 角色外观不一致
**解决**：
- 在 `config/comic.yaml` 中确保 `maintain_character: true`
- 在场景描述中保持角色关键特征一致
- 考虑升级到 Nano Banana Pro（角色一致性更好）

### Q3: 字幕显示乱码
**解决**：
```bash
# macOS 已内置中文字体，无需额外配置

# Linux 需要安装中文字体:
sudo apt-get install fonts-wqy-microhei

# Windows 会自动使用微软雅黑
```

### Q4: 视频导出很慢
**解决**：
- 降低分辨率：在 `config/comic.yaml` 中设置 `resolution: "1280x720"`
- 降低帧率：设置 `fps: 12`
- 降低比特率：设置 `bitrate: "2000k"`

### Q5: 想要竖屏视频（抖音/快手格式）
**解决**：
```yaml
# config/comic.yaml
image_generation:
  aspect_ratio: "9:16"  # 竖屏

video:
  resolution: "1080x1920"  # 竖屏分辨率
```

---

## 📈 下一步优化

完成 MVP 后，可以考虑：

1. **自动化剧本生成**
   - 使用 GPT-4 根据用户创意自动生成剧本
   - 参考: `apps/daily-podcast-ai/src/processors/script_writer.py`

2. **音效库集成**
   - 添加脚步声、开门声、背景音乐等
   - 参考: `src/generators/audio_mixer.py`

3. **批量化生产**
   - 一次生成10集连载短剧
   - 自动发布到视频平台

4. **成本优化**
   - 缓存常用角色图像
   - 复用相同场景的背景

---

## 📞 技术支持

遇到问题？
- 查看 `apps/daily-podcast-ai/README.md` 了解项目架构
- 参考 ElevenLabs 文档: https://elevenlabs.io/docs
- 参考 Gemini API 文档: https://ai.google.dev/gemini-api/docs/image-generation

---

**祝你创作愉快！🎉**

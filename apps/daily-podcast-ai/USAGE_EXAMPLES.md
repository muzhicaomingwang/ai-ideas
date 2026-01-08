# 漫画短剧生成 - 完整使用示例

所有功能的实际使用案例和命令参考。

---

## 📋 目录

1. [狼人杀复盘系列](#狼人杀复盘系列)
2. [通用题材系列](#通用题材系列)
3. [自定义剧本](#自定义剧本)
4. [批量生成](#批量生成)
5. [输出格式调整](#输出格式调整)

---

## 🐺 狼人杀复盘系列

### 示例1: 生成经典翻盘局

```bash
cd apps/daily-podcast-ai

# 方式1: 直接运行（使用默认剧本）
python scripts/generate_werewolf_drama.py

# 方式2: 指定剧本
python scripts/generate_werewolf_drama.py classic_win

# 输出位置
# output/werewolf-drama/classic_win/2026-01-08/狼人杀单局复盘-预女猎翻盘局.mp4
```

**预期输出**：
- 7个场景，75秒
- 展示预言家、女巫、猎人配合
- 成本约 ¥3.19

---

### 示例2: 生成狼队内讧局（搞笑向）

```bash
python scripts/generate_werewolf_drama.py wolf_betrayal

# 输出
# output/werewolf-drama/wolf_betrayal/2026-01-08/狼人杀复盘-狼队内讧惨案.mp4
```

**亮点**：
- 5号狼悍跳验队友
- 2号狼愤怒反击
- 名场面："你是不是脑子有问题？"

---

### 示例3: 批量生成所有狼人杀剧本

```bash
# 创建批量脚本
cat > scripts/batch_werewolf.sh << 'EOF'
#!/bin/bash
for script in classic_win wolf_betrayal epic_comeback perfect_wolf; do
    echo "========================================="
    echo "生成: $script"
    echo "========================================="
    python scripts/generate_werewolf_drama.py $script
    echo ""
done
EOF

chmod +x scripts/batch_werewolf.sh
./scripts/batch_werewolf.sh
```

**输出**：4个不同主题的复盘视频，可组成系列发布

---

## 🎨 通用题材系列

### 示例4: 生成AI助手故事

```bash
# 修改 generate_comic_drama.py
# 将 create_test_script() 替换为:

from example_scripts import get_ai_assistant_story

test_script = get_ai_assistant_story()
```

然后运行：
```bash
python scripts/generate_comic_drama.py
```

---

### 示例5: 生成咖啡店治愈系短剧

```python
# scripts/generate_coffee.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from example_scripts import get_coffee_shop_story
from generate_comic_drama import generate_comic_drama

script = get_coffee_shop_story()
generate_comic_drama(script, output_dir="output/coffee-shop")
```

运行：
```bash
python scripts/generate_coffee.py
```

---

## ✏️ 自定义剧本

### 示例6: 创建你的第一个自定义剧本

```python
# scripts/my_first_drama.py
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_comic_drama import generate_comic_drama

# 你的剧本
my_script = {
    "title": "我的第一个短剧",
    "scenes": [
        {
            "description": "阳光明媚的公园，小女孩在喂鸽子，水彩画风格，温暖色调",
            "character": "小女孩",
            "dialogue": "小鸽子们，快来吃饭啦！",
            "voice_id": "pNInz6obpgDQGcFmaJgB",  # 替换为你的语音ID
            "duration": 4.0
        },
        {
            "description": "鸽子们飞过来，围绕小女孩，她开心地笑着，漫画风格",
            "character": "小女孩",
            "dialogue": "你们真可爱！",
            "voice_id": "pNInz6obpgDQGcFmaJgB",
            "duration": 3.0
        },
        {
            "description": "远景，公园的长椅上，小女孩和鸽子们的剪影，夕阳余晖，治愈系画风",
            "character": "旁白",
            "dialogue": "简单的快乐，就是这么美好。",
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "duration": 4.0
        }
    ]
}

# 生成
result = generate_comic_drama(my_script, output_dir="output/my-drama")
if result:
    print(f"✅ 完成！视频位置: {result}")
```

运行：
```bash
chmod +x scripts/my_first_drama.py
python scripts/my_first_drama.py
```

---

## 🔄 批量生成

### 示例7: 生成一周的内容

```python
# scripts/weekly_batch.py
from datetime import datetime, timedelta
from werewolf_game_scripts import WEREWOLF_SCRIPTS
from generate_comic_drama import generate_comic_drama

# 每天发布一个不同的剧本
script_list = list(WEREWOLF_SCRIPTS.keys())

for i, script_name in enumerate(script_list):
    # 计算发布日期
    publish_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")

    script_func = WEREWOLF_SCRIPTS[script_name]
    script = script_func()

    print(f"\n生成第{i+1}天内容: {publish_date}")

    generate_comic_drama(
        script,
        output_dir=f"output/weekly/{script_name}",
        date=publish_date
    )
```

---

## 🎛️ 输出格式调整

### 示例8: 生成竖屏版本（抖音/快手）

修改 `config/comic.yaml`：

```yaml
image_generation:
  aspect_ratio: "9:16"  # 改为竖屏

video:
  resolution: "1080x1920"  # 竖屏分辨率
  subtitle:
    font_size: 56  # 竖屏字体可以稍大
    margin: 80
```

然后正常生成：
```bash
python scripts/generate_werewolf_drama.py
```

---

### 示例9: 生成方形视频（小红书/Instagram）

```yaml
image_generation:
  aspect_ratio: "1:1"  # 方形

video:
  resolution: "1080x1080"
```

---

### 示例10: 高清4K版本

```yaml
image_generation:
  model: "gemini-3-pro-image-preview"  # 升级到 Pro
  enable_4k: true

video:
  resolution: "3840x2160"  # 4K分辨率
  bitrate: "15000k"
```

**注意**：4K版本成本提升约5倍。

---

## 🎨 风格定制

### 示例11: 生成暗黑风格狼人杀

修改剧本中的场景描述：

```python
{
    "description": (
        "黑暗哥特风格的会议室，昏暗的烛光，"
        "12个座位被阴影笼罩，中央是血红色的月亮标志，"
        "暗黑漫画风格，恐怖氛围，浓重的黑色和深红色"
    ),
    # ...
}
```

---

### 示例12: 生成Q版可爱风格

```python
{
    "description": (
        "Q版卡通风格的圆桌，12个可爱的小人坐在圆形座位上，"
        "大眼睛，圆脸，卡哇伊风格，糖果色调，温馨可爱，"
        "chibi anime style"
    ),
    # ...
}
```

---

## 🔧 调试技巧

### 示例13: 只生成图像（不配音）

```python
# scripts/test_image_only.py
from src.generators.nano_banana_generator import NanoBananaGenerator

generator = NanoBananaGenerator()

test_scenes = [
    {"description": "场景1描述", "dialogue": "", "duration": 0},
    {"description": "场景2描述", "dialogue": "", "duration": 0},
]

frames = generator.generate_comic_sequence(
    script_scenes=test_scenes,
    output_dir="output/test-frames"
)

print(f"生成了 {len(frames)} 个图像帧")
```

---

### 示例14: 只生成配音（不生成图像）

```python
# scripts/test_voice_only.py
from src.generators.tts_generator import TTSGenerator

generator = TTSGenerator()

dialogues = [
    "这是第一段对话",
    "这是第二段对话",
    "这是第三段对话"
]

for i, text in enumerate(dialogues):
    generator.generate_audio(
        text=text,
        output_path=f"output/test-audio/test_{i}.mp3"
    )
```

---

## 📊 质量控制

### 示例15: 生成预览版（快速验证）

使用低质量配置快速生成预览：

```yaml
# config/comic_preview.yaml (复制并修改 comic.yaml)
video:
  fps: 12  # 降低帧率
  resolution: "960x540"  # 降低分辨率
  bitrate: "1500k"
```

生成时指定配置文件：
```python
# 修改生成器初始化
generator = NanoBananaGenerator(config_path="config/comic_preview.yaml")
```

预览版生成速度提升50%，成本降低30%。

---

## 🎯 实际案例

### 案例1: B站UP主"狼人杀小课堂"

**需求**：每周3集教学视频
**剧本**：classic_win, epic_comeback, perfect_wolf
**时长**：每集60-80秒
**成本**：¥9-10/周

**流程**：
```bash
# 周一生成3集
python scripts/generate_werewolf_drama.py classic_win
python scripts/generate_werewolf_drama.py epic_comeback
python scripts/generate_werewolf_drama.py perfect_wolf

# 手动添加片头片尾（5秒）
# 导出到B站
```

---

### 案例2: 抖音"狼人杀精彩瞬间"

**需求**：每天1条竖屏短视频
**剧本**：从 wolf_betrayal 中提取搞笑片段
**时长**：30-45秒
**成本**：¥1.5-2/条

**流程**：
```bash
# 1. 修改为竖屏配置
# 2. 只生成高光场景（场景3-5）
# 3. 添加BGM
# 4. 发布
```

---

### 案例3: 小红书"游戏教学"

**需求**：图文+视频混合
**格式**：方形1:1
**内容**：战术分析 + 案例展示

**流程**：
```bash
# 1. 生成方形视频
# 2. 导出关键帧作为图片
# 3. 编辑图文笔记
# 4. 视频作为补充素材
```

---

## 📈 效率优化

### 技巧1: 批量修改语音ID

```bash
# 一次性替换所有剧本的语音ID
cd scripts
sed -i '' 's/21m00Tcm4TlvDq8ikWAM/你的新语音ID/g' werewolf_game_scripts.py
```

### 技巧2: 预生成图像库

```python
# 提前生成常用场景
common_scenes = {
    "圆桌俯视": "俯视视角的12人圆桌，编号清晰...",
    "夜晚氛围": "夜晚场景，月光洒在桌面...",
    "白天投票": "白天场景，投票箭头...",
}

generator = NanoBananaGenerator()
for name, desc in common_scenes.items():
    generator.generate_frame(
        description=desc,
        output_path=f"cache/scenes/{name}.png"
    )
```

之后可以直接复用这些图像。

---

## 🎁 额外资源

### 背景音乐推荐

| 场景类型 | 推荐BGM | 来源 |
|---------|---------|------|
| 狼人杀复盘 | 悬疑推理BGM | YouTube Audio Library |
| 紧张PK | Epic Tension Music | Epidemic Sound |
| 胜利庆祝 | Victory Fanfare | FreeSounds |

### 音效推荐

- **狼嚎声**：夜晚场景
- **刀人音效**：表示玩家出局
- **验人音效**：预言家验人
- **投票音效**：白天投票

下载：https://freesound.org

---

## 🚀 生产级部署

### 自动化定时生成

```bash
# 添加到 crontab
# 每天早上9点生成一个狼人杀复盘

0 9 * * * cd /path/to/daily-podcast-ai && python scripts/generate_werewolf_drama.py >> logs/werewolf.log 2>&1
```

### CI/CD集成

```yaml
# .github/workflows/generate-werewolf.yml
name: Generate Werewolf Drama

on:
  schedule:
    - cron: '0 9 * * *'  # 每天早上9点
  workflow_dispatch:  # 手动触发

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/generate_werewolf_drama.py
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
      - uses: actions/upload-artifact@v3
        with:
          name: werewolf-video
          path: output/werewolf-drama/**/*.mp4
```

---

## 📱 社交媒体发布

### 抖音发布checklist

- [ ] 视频：9:16竖屏，时长15-60秒
- [ ] 封面：提取关键帧，添加文字
- [ ] 标题：【狼人杀复盘】XX局 | XX翻盘
- [ ] 话题：#狼人杀 #游戏复盘 #策略游戏
- [ ] 发布时间：晚上8-10点

### B站发布checklist

- [ ] 视频：16:9横屏，分P或合集
- [ ] 封面：设计专业封面（建议用Canva）
- [ ] 标题：狼人杀复盘【第X期】- 主题名
- [ ] 简介：包含场次信息、MVP、关键战术
- [ ] 标签：狼人杀、游戏、策略、复盘
- [ ] 分区：游戏 → 桌游棋牌

---

## 🎓 学习路径

### 新手（第1周）

1. ✅ 阅读 `QUICKSTART_WEREWOLF.md`
2. ✅ 运行 `test_comic_generation.py`
3. ✅ 生成第一个默认剧本
4. ✅ 修改语音ID生成第二个

### 进阶（第2周）

1. 📝 创建自己的剧本
2. 🎨 尝试不同风格
3. 🎵 添加BGM和音效
4. 📊 批量生成系列内容

### 高级（第3周）

1. 🤖 接入GPT-4自动生成剧本
2. 🎬 后期特效增强
3. 📈 数据分析和优化
4. 💰 商业化运营

---

## 📖 完整命令速查

```bash
# ========== 安装和配置 ==========
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_voice.py

# ========== 查看功能 ==========
python scripts/show_all_features.py
python scripts/werewolf_game_scripts.py
python scripts/example_scripts.py

# ========== 测试 ==========
python scripts/test_comic_generation.py

# ========== 生成视频 ==========
# 狼人杀系列
python scripts/generate_werewolf_drama.py
python scripts/generate_werewolf_drama.py wolf_betrayal

# 通用系列
python scripts/generate_comic_drama.py

# ========== 查看结果 ==========
ls -lh output/werewolf-drama/
open output/werewolf-drama/classic_win/2026-01-08/*.mp4
```

---

好了，现在开始创作你的狼人杀复盘短剧吧！🐺🎬

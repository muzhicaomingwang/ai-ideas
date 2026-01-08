# 狼人杀复盘短剧生成指南

使用 Nano Banana + ElevenLabs 自动生成狼人杀游戏复盘视频。

---

## 🎮 项目特色

- **自动图像生成**：使用 Nano Banana 生成12人圆桌、角色卡牌、投票场景
- **多角色配音**：解说员 + 玩家角色，真实还原游戏氛围
- **专业复盘**：包含战术分析、关键决策点标注
- **快速产出**：7个场景约70秒的短剧，10分钟内生成完成

---

## 🚀 快速开始

### 1. 一键生成（使用默认剧本）

```bash
cd apps/daily-podcast-ai

# 生成经典翻盘局
python scripts/generate_werewolf_drama.py

# 视频保存在:
# output/werewolf-drama/classic_win/2026-01-08/狼人杀单局复盘-预女猎翻盘局.mp4
```

### 2. 选择其他剧本

```bash
# 查看所有可用剧本
python scripts/werewolf_game_scripts.py

# 生成指定剧本
python scripts/generate_werewolf_drama.py wolf_betrayal    # 狼队内讧
python scripts/generate_werewolf_drama.py epic_comeback    # 史诗翻盘
python scripts/generate_werewolf_drama.py perfect_wolf     # 完美狼局
```

---

## 📚 内置剧本库

### classic_win - 预女猎翻盘局 ⭐ 推荐

**故事线**：预言家被刀但被救，验出狼人，猎人精准带人，好人完美配合获胜

**场景**：
1. 12人局角色介绍（3狼3民+6神）
2. 第1晚：狼刀预言家，女巫救人
3. 第2天：预言家报验人，投出7号狼
4. 第2晚：狼刀猎人
5. 第3天：猎人带走11号狼
6. PK环节：投出最后一狼
7. 复盘总结：MVP分析

**时长**：75秒
**主题**：团队配合、神职作用

---

### wolf_betrayal - 狼队内讧惨案

**故事线**：狼队因沟通不足，5号狼悍跳验2号队友，导致全队崩盘

**场景**：
1. 12人局介绍
2. 第1晚：狼刀预言家
3. 第2天：5号狼悍跳验2号队友
4. 2号狼愤怒反击
5. 2号狼被投出，队友懵圈
6. 狼队连续崩盘
7. 复盘：狼踩狼失败教训

**时长**：67秒
**主题**：团队沟通、狼队战术

---

### epic_comeback - 史诗翻盘局

**故事线**：好人3打2绝境翻盘，预言家冷静推理+猎人坚定支持

**场景**：
1. 危机开局（3好人vs2狼）
2. 夜晚狼队刀人
3. 预言家关键推理
4. 猎人表态支持
5. 投出一狼
6. 最后一夜
7. 复盘：绝境翻盘的关键

**时长**：68秒
**主题**：逻辑推理、绝境反击

---

### perfect_wolf - 狼队教科书级胜利

**故事线**：2号悍跳+6号冲锋+9号倒钩，狼队完美配合

**场景**：
1. 狼队战术介绍
2. 2号狼悍跳预言家
3. 6号狼冲锋配合
4. 投出真预言家
5. 狼队控场连胜
6. 狼队获胜
7. 复盘：狼队战术分析

**时长**：58秒
**主题**：狼队战术、悍跳技巧

---

## 🎨 自定义你的剧本

### 创建新剧本

编辑 `scripts/werewolf_game_scripts.py`，添加新函数：

```python
def get_your_custom_game():
    """你的自定义剧本"""
    return {
        "title": "狼人杀复盘-你的标题",
        "scenes": [
            {
                "description": "场景的视觉描述（用于生成图像）",
                "character": "角色名称",
                "dialogue": "对话或旁白内容",
                "voice_id": "ElevenLabs语音ID",
                "duration": 8.0  # 场景时长（秒）
            },
            # ... 更多场景
        ]
    }

# 添加到索引
WEREWOLF_SCRIPTS["your_key"] = get_your_custom_game
```

### 场景描述技巧

**好的描述**（Nano Banana 容易理解）：
```
"俯视视角的圆桌，12个座位呈圆形排列，编号1-12清晰可见，
中央是狼人杀月亮标志，漫画风格，温暖灯光"
```

**避免的描述**（过于抽象）：
```
"狼人杀游戏场景"  # ❌ 太抽象
"复杂的推理过程"  # ❌ 无法可视化
```

**关键要素**：
- 视角：俯视/平视/特写
- 元素：圆桌、座位编号、卡牌、投票箭头
- 风格：漫画风格/动漫风格/写实风格
- 光线：白天/夜晚/聚光灯
- 情绪：紧张/欢庆/神秘

---

## 🎙️ 角色语音配置

### 推荐语音分配

| 角色类型 | 语音特点 | 推荐Voice ID |
|---------|---------|-------------|
| **解说员** | 专业、沉稳、清晰 | EXAVITQu4vr4xnSDxMaL |
| **玩家A** | 年轻、热情、活泼 | 21m00Tcm4TlvDq8ikWAM |
| **玩家B** | 冷静、理性、稳重 | pNInz6obpgDQGcFmaJgB |

### 查看可用语音

```bash
python scripts/setup_voice.py
```

会列出所有 ElevenLabs 可用语音，选择3个不同风格的即可。

---

## 🎬 高级功能

### 1. 批量生成多集

```python
# scripts/batch_werewolf.py
from werewolf_game_scripts import WEREWOLF_SCRIPTS
from generate_comic_drama import generate_comic_drama

for script_name, script_func in WEREWOLF_SCRIPTS.items():
    script = script_func()
    generate_comic_drama(
        script,
        output_dir=f"output/werewolf-series/{script_name}"
    )
```

### 2. 竖屏版本（抖音/快手）

修改 `config/comic.yaml`：

```yaml
image_generation:
  aspect_ratio: "9:16"  # 改为竖屏

video:
  resolution: "1080x1920"  # 竖屏分辨率
```

### 3. 添加背景音乐

```python
# 在 generate_comic_drama.py 中修改
from src.generators.audio_mixer import AudioMixer

# 在视频合成前添加背景音乐
mixer = AudioMixer()
audio_with_bgm = mixer.add_background_music(
    voice_audio_path="合并后的配音.mp3",
    bgm_path="bgm/suspense.mp3",  # 悬疑音乐
    output_path="最终音频.mp3"
)
```

### 4. 导出分镜脚本（用于后期编辑）

```python
# scripts/export_storyboard.py
import json
from werewolf_game_scripts import get_werewolf_classic_game

script = get_werewolf_classic_game()

# 导出为 JSON
with open("output/storyboard.json", "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)

# 或导出为 Markdown
with open("output/storyboard.md", "w", encoding="utf-8") as f:
    f.write(f"# {script['title']}\n\n")
    for i, scene in enumerate(script['scenes']):
        f.write(f"## 场景 {i+1}: {scene['character']}\n\n")
        f.write(f"**描述**: {scene['description']}\n\n")
        f.write(f"**对白**: {scene['dialogue']}\n\n")
        f.write(f"**时长**: {scene['duration']}秒\n\n")
        f.write("---\n\n")
```

---

## 💰 成本分析

### 单集成本（以 classic_win 为例）

| 项目 | 计算 | 金额 |
|------|------|------|
| 图像生成 | 7帧 × ¥0.008/帧 | ¥0.056 |
| 配音 | 75秒 ≈ 1.25分钟 × ¥2.5/分钟 | ¥3.13 |
| **总计** | | **¥3.19/集** |

### 批量生产（10集）

- 总成本：¥31.9
- 总时长：约12分钟
- 单集均摊：¥3.19

### 成本优化建议

1. **复用背景图像**：圆桌场景可以复用，只修改卡牌状态
2. **使用 Nano Banana 普通版**：成本是 Pro 版的 1/5
3. **优化配音**：简化解说词，控制在60秒内

---

## 🎯 典型应用场景

### 1. 游戏复盘UP主
- 录制自己的狼人杀游戏
- 用AI快速生成复盘视频
- 发布到B站/抖音

### 2. 狼人杀教学
- 制作战术教学系列
- 展示经典案例分析
- 帮助新手理解游戏

### 3. 娱乐内容创作
- 创作搞笑狼人杀剧情
- 制作狼人杀表情包视频
- 短视频平台引流

---

## 🐛 常见问题

### Q1: 图像中的角色不一致怎么办？

**解决方案**：
1. 在场景描述中保持关键特征一致
   ```
   场景1: "蓝色机器人，圆形眼睛，友善笑容"
   场景2: "同样的蓝色机器人，圆形眼睛，挥手致意"  # 保持特征
   ```

2. 升级到 Nano Banana Pro
   ```yaml
   # config/comic.yaml
   image_generation:
     model: "gemini-3-pro-image-preview"  # Pro版角色一致性更好
   ```

### Q2: 如何添加座位编号和角色标识？

Nano Banana 擅长渲染文字，直接在描述中说明：

```python
"description": "圆桌上方显示编号1-12，1号位置有金色'预言家'文字标签，
3、7、11号位置有红色'狼人'标签，清晰可读的文字，漫画风格"
```

### Q3: 配音和画面时长不匹配

每个场景的 `duration` 应该基于配音文本长度估算：
- 中文：约 3-4 字/秒
- 例如："这是一个测试"（6字）→ 约2秒

```python
dialogue_text = "我是预言家，昨晚验出7号是狼！"  # 14字
duration = len(dialogue_text) / 3.5  # ≈ 4秒
```

### Q4: 想要更悬疑的风格

修改场景描述的风格词：

```python
# 原始
"description": "夜晚场景，漫画风格"

# 悬疑风格
"description": "夜晚场景，暗黑漫画风格，阴森的紫色月光，悬疑氛围，
浓重的阴影，神秘的光效"
```

---

## 📊 场景设计最佳实践

### 7场景结构模板

```python
{
    "scenes": [
        # 场景1: 全局介绍（8-10秒）
        # - 俯视圆桌 + 所有座位
        # - 角色配置说明
        # - 设定悬念

        # 场景2: 第1晚行动（10-12秒）
        # - 狼人刀人
        # - 神职行动
        # - 关键信息

        # 场景3: 第2天白天（15-18秒）
        # - 发言环节（1-2个关键发言）
        # - 投票出局

        # 场景4: 第2晚行动（8-10秒）
        # - 狼人再次刀人
        # - 神职应对

        # 场景5: 第3天关键推理（12-15秒）
        # - 高光时刻
        # - 关键玩家发言

        # 场景6: 决胜环节（10-12秒）
        # - PK或最后投票
        # - 结果揭晓

        # 场景7: 复盘总结（10-13秒）
        # - 身份揭晓
        # - MVP评选
        # - 战术分析
    ]
}
```

### 视觉元素清单

**必备元素**：
- ✅ 圆形桌子
- ✅ 12个座位编号
- ✅ 角色卡牌（狼人、预言家、女巫等）
- ✅ 投票箭头
- ✅ 白天/夜晚氛围

**增强元素**：
- 🌟 发光效果（神职技能）
- 🗨️ 对话气泡
- ➡️ 推理逻辑线
- ⚡ 戏剧性光效
- 📊 数据图表（投票结果）

---

## 🎨 风格调整

### 调整画风

在 `config/comic.yaml` 中修改：

```yaml
image_generation:
  style: "anime"  # 可选值:
  # - comic: 美式漫画
  # - anime: 日本动漫
  # - manga: 日式漫画（黑白）
  # - realistic: 写实风格
  # - watercolor: 水彩画
```

### 调整色调

在场景描述中添加色调关键词：

```python
# 温馨风格
"description": "..., 温暖色调，柔和光线，治愈系氛围"

# 悬疑风格
"description": "..., 冷色调，阴森氛围，神秘的蓝紫色"

# 激烈风格
"description": "..., 高对比度，强烈光影，戏剧性效果"
```

---

## 📈 内容运营建议

### 视频平台适配

| 平台 | 格式要求 | 配置调整 |
|------|---------|---------|
| **B站** | 16:9横屏 | 默认配置即可 |
| **抖音** | 9:16竖屏 | aspect_ratio: "9:16" |
| **快手** | 9:16竖屏 | 同抖音 |
| **小红书** | 3:4或1:1 | aspect_ratio: "3:4" |
| **YouTube** | 16:9横屏 | 默认配置 |

### 标题优化

```
格式: 【狼人杀复盘】<亮点> | <结果>

示例:
- 【狼人杀复盘】预言家被刀反杀3狼 | 好人完美配合
- 【狼人杀复盘】狼队内讧名场面 | 队友互卖笑死我了
- 【狼人杀复盘】3打2绝境翻盘 | 预言家神级推理
```

### 封面设计

使用第1个或第7个场景作为封面：
- 第1场景：完整圆桌，信息量大
- 第7场景：总结画面，有吸引力

```bash
# 提取视频第1帧作为封面
ffmpeg -i output/video.mp4 -vframes 1 -f image2 cover.jpg
```

---

## 🔧 调试技巧

### 单独测试图像生成

```bash
cd apps/daily-podcast-ai
python src/generators/nano_banana_generator.py
```

### 单独测试配音

```bash
python src/generators/tts_generator.py
```

### 完整测试

```bash
python scripts/test_comic_generation.py
```

---

## 📞 获取帮助

- **项目主文档**：`README.md`
- **通用指南**：`docs/COMIC_DRAMA_QUICKSTART.md`
- **配置说明**：`config/comic.yaml`（有详细注释）

祝你创作愉快！🎉🐺

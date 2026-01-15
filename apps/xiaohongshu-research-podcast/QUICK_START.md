# 快速开始指南

## 5分钟快速体验

### 1. 安装依赖

```bash
# 确保已安装Poetry
poetry --version

# 如未安装
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install

# 安装Playwright浏览器
poetry run playwright install chromium
```

### 2. 配置API密钥

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置（填入你的API密钥）
nano .env
```

需要配置两个API密钥：
- **Google Gemini API**: https://ai.google.dev/
- **ElevenLabs API**: https://elevenlabs.io/

### 3. 运行第一次生成

```bash
# 仅生成报告和封面（不需要音频）
poetry run python scripts/daily_generate.py --skip-audio

# 查看输出
ls output/$(date +%Y-%m-%d)/
```

你会看到：
```
script-2026-01-15.json    # 播客脚本（JSON）
script-2026-01-15.md      # 播客脚本（Markdown）
report-2026-01-15.md      # 研究报告
cover-2026-01-15.png      # 播客封面
```

### 4. 查看生成结果

```bash
# 查看研究报告
cat output/$(date +%Y-%m-%d)/report-*.md

# 查看播客脚本
cat output/$(date +%Y-%m-%d)/script-*.md

# 查看封面（macOS）
open output/$(date +%Y-%m-%d)/cover-*.png
```

---

## 完整功能体验（包含音频）

### 前提条件

1. ✅ 已配置 `GOOGLE_API_KEY`
2. ✅ 已配置 `ELEVENLABS_API_KEY`
3. ✅ 已安装所有依赖

### 运行完整流程

```bash
# 生成完整播客（包含音频）
poetry run python scripts/daily_generate.py

# 等待约2-3分钟...
```

### 输出文件

```
output/2026-01-15/
├── script-2026-01-15.json       # 对话脚本（JSON）
├── script-2026-01-15.md         # 对话脚本（Markdown）
├── podcast-2026-01-15.mp3       # 播客音频（约9分钟）
├── report-2026-01-15.md         # 研究报告
├── cover-2026-01-15.png         # 播客封面（1400x1400）
└── audio_segments/              # 音频片段（调试用）
    ├── segment_0_xiaoya.mp3
    ├── segment_1_zhimeng.mp3
    └── ...
```

### 播放音频

```bash
# macOS
open output/$(date +%Y-%m-%d)/podcast-*.mp3

# Linux
vlc output/$(date +%Y-%m-%d)/podcast-*.mp3
```

---

## 命令行选项

```bash
# 查看所有选项
poetry run python scripts/daily_generate.py --help

# 常用选项
--date 2026-01-14          # 生成指定日期
--skip-audio               # 跳过音频生成
--skip-report              # 跳过报告生成
--skip-cover               # 跳过封面生成
--skip-scrape              # 使用缓存数据（不重新抓取）
--output ./custom-output   # 自定义输出目录
--verbose                  # 显示详细日志
--dry-run                  # 演示模式（不生成文件）
```

### 实用组合

```bash
# 仅生成报告（最快，不消耗TTS配额）
poetry run python scripts/daily_generate.py --skip-audio

# 使用缓存数据快速重新生成
poetry run python scripts/daily_generate.py --skip-scrape

# 生成历史日期的播客
poetry run python scripts/daily_generate.py --date 2026-01-10
```

---

## 查看示例

项目已包含示例输出：

```bash
# 查看示例报告
cat output/example-report-2026-01-15.md

# 运行示例生成器
poetry run python examples/generate_complete_report.py
```

---

## 配置自动化（可选）

### macOS定时任务

```bash
# 1. 测试运行脚本
./scripts/run_daily.sh

# 2. 配置launchd
cp scripts/com.xiaohongshu-research-podcast.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist

# 3. 查看状态
launchctl list | grep xiaohongshu
```

详细说明见: `docs/DEPLOYMENT.md`

---

## 成本估算

### 每日成本
- **AI分析**: ~$0.06 (Gemini输入tokens)
- **脚本生成**: ~$0.16 (Gemini输出tokens)
- **TTS合成**: ~$0.09 (ElevenLabs, ~3000字符)
- **合计**: ~$0.31/天

### 月度成本
- **每天运行**: ~$9.3/月
- **工作日运行**: ~$6.5/月

### 优化技巧
1. 使用 `--skip-audio` 在测试时跳过TTS
2. 启用缓存避免重复API调用
3. 批量处理多天数据

---

## 常见问题

### Q1: 报告生成很慢？
A: 主要时间在数据抓取（~30秒）和AI生成（~20秒）。可以使用 `--skip-scrape` 使用缓存数据。

### Q2: 音频质量如何调整？
A: 编辑 `config/voice.yaml`，调整 `voice_settings` 参数。

### Q3: 如何修改播客时长？
A: 修改 `scripts/daily_generate.py` 中的 `target_duration` 参数（默认540秒=9分钟）。

### Q4: 能生成历史日期的播客吗？
A: 可以，但需要有对应日期的缓存数据。使用 `--date 2026-01-10`。

### Q5: 如何修改主持人语音？
A: 编辑 `config/voice.yaml`，更新 `voice_id` 为你喜欢的ElevenLabs语音ID。

---

## 下一步

- **查看详细文档**: `docs/` 目录
- **查看示例代码**: `examples/` 目录
- **配置自动化**: `docs/DEPLOYMENT.md`
- **自定义配置**: 编辑 `config/voice.yaml`

---

**需要帮助？**
- 查看日志: `logs/daily-*.log`
- 查看源码: `src/` 目录
- 提issue: (GitHub仓库地址)

# Daily Podcast AI

> 将每日早新闻自动生成为播客，使用你自己的声音作为播报员

## 项目背景

这是一个自动化播客生成工具，核心功能是：
1. 从多个新闻源获取每日早新闻
2. 使用 AI 进行内容整理和脚本生成
3. 通过 ElevenLabs 的语音克隆技术，用你自己的声音朗读新闻
4. 输出为标准播客格式（MP3）

## 技术栈

- **语音合成**: ElevenLabs API（通过 MCP Server）
- **新闻获取**: RSS/API 聚合
- **内容处理**: Claude AI（摘要、脚本生成）
- **音频处理**: Python + pydub

---

## ElevenLabs MCP 调研结果

### 官方 MCP Server

ElevenLabs 提供官方 MCP（Model Context Protocol）服务器，于 2025年4月7日发布。

- **GitHub**: https://github.com/elevenlabs/elevenlabs-mcp
- **文档**: https://elevenlabs.io/docs/agents-platform/customization/tools/mcp

### 核心功能

| 功能 | 说明 |
|------|------|
| Text-to-Speech | 文本转语音，支持多种声音 |
| Voice Cloning | 语音克隆（即时/专业两种模式） |
| Audio Transcription | 音频转文字 |
| Voice Design | 自定义声音设计 |
| Audio Isolation | 音频隔离/降噪 |
| Multi-speaker ID | 多说话人识别 |

### 语音克隆要求

| 模式 | 音频时长 | 效果 |
|------|---------|------|
| 即时克隆 (Instant) | 1-2 分钟清晰音频 | 快速生成，质量中等 |
| 专业克隆 (Professional) | 30+ 分钟（推荐 2+ 小时） | 高质量，需审核 |

### 免费额度

- **每月免费**: 10,000 credits
- **换算**: 约 10 分钟标准音频输出
- **评估**: 对于每日简短播客（3-5分钟），免费额度基本够用

### 配置方式

#### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ElevenLabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

#### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ELEVENLABS_API_KEY` | API 密钥（必须） | - |
| `ELEVENLABS_MCP_BASE_PATH` | 文件输出基础路径 | `~/Desktop` |
| `ELEVENLABS_MCP_OUTPUT_MODE` | 输出模式 | `files` |
| `ELEVENLABS_API_RESIDENCY` | 数据驻留地区 | `us` |

### MCP 工具列表

安装后可用的 MCP 工具：

- `text_to_speech` - 文本转语音
- `get_voices` - 获取可用声音列表
- `clone_voice` - 克隆声音
- `transcribe_audio` - 音频转文字
- `isolate_audio` - 音频隔离
- `get_voice_settings` - 获取声音设置
- `update_voice_settings` - 更新声音设置

---

## 项目结构

```
daily-podcast-ai/
├── README.md                 # 项目文档（本文件）
├── config/
│   ├── sources.yaml          # 新闻源配置
│   └── voice.yaml            # 语音配置（ElevenLabs voice_id: SKlxpKXGwoM0E8XpnxNs）
├── src/
│   ├── news_sources/         # 新闻获取模块
│   │   ├── rss_fetcher.py
│   │   └── api_fetcher.py
│   ├── processors/           # 内容处理模块
│   │   ├── summarizer.py     # 新闻摘要
│   │   ├── script_writer.py  # 播客脚本生成
│   │   └── news_ranker.py    # AI新闻优选（GPT-4o-mini）
│   └── generators/           # 音频生成模块
│       ├── tts_generator.py  # TTS 生成
│       └── audio_mixer.py    # 音频合成
├── scripts/
│   ├── setup_voice.py        # 声音克隆设置
│   ├── daily_generate.py     # 每日生成脚本（支持 --from-cache 优选）
│   ├── hourly_collect.py     # 每小时新闻收集脚本
│   ├── generate_cover.py     # 封面图片生成（PIL，1400x1400px）
│   ├── run_daily.sh          # 定时任务执行脚本（venv + .env）
│   ├── com.daily-podcast-ai.plist        # launchd: 每天7点生成播客
│   └── com.daily-podcast-ai-hourly.plist # launchd: 每小时收集新闻
├── logo/
│   └── 王植萌漫画形象.png     # 播客封面 logo（350px）
├── cache/                    # 新闻缓存目录
│   └── YYYY-MM-DD-news.json  # 每小时收集的新闻缓存
├── docs/
│   └── workflow.md           # 工作流文档
├── output/                   # 生成的播客文件
│   └── YYYY-MM-DD/           # 按日期组织
│       ├── script-YYYY-MM-DD.md      # 播客讲稿
│       ├── cover-YYYY-MM-DD.png      # 封面图片
│       └── daily-podcast-YYYY-MM-DD.mp3  # 音频文件
├── logs/                     # 日志目录
│   ├── daily-YYYY-MM-DD.log  # 每日生成日志
│   ├── hourly-stdout.log     # 每小时收集日志
│   └── launchd-*.log         # launchd 系统日志
└── venv/                     # Python 虚拟环境
```

---

## 工作流设计

### 两级自动化流程

```
┌─────────────────────────────────────────────────────────────┐
│                   阶段1: 每小时收集（0:00-6:00）              │
└─────────────────────────────────────────────────────────────┘
         │
         │  每小时执行一次
         ▼
┌─────────────────┐
│  RSS 源获取      │  从配置的新闻源获取最新文章
└────────┬────────┘
         ▼
┌─────────────────┐
│  去重 & 追加     │  自动去重，追加到缓存文件
└────────┬────────┘
         ▼
┌─────────────────┐
│  缓存存储        │  cache/YYYY-MM-DD-news.json
└─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   阶段2: 早上7点优选生成                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  读取缓存        │  加载全天收集的新闻（可能几十篇）
└────────┬────────┘
         ▼
┌─────────────────┐
│  AI 优选         │  GPT-4o-mini 评估质量，选出 Top 10
└────────┬────────┘
         ▼
┌─────────────────┐
│  AI 摘要         │  Claude 生成简明摘要
└────────┬────────┘
         ▼
┌─────────────────┐
│  脚本生成        │  生成播客脚本（含过渡语）
└────────┬────────┘
         ▼
┌─────────────────┐
│  语音合成        │  ElevenLabs TTS（你的声音）
└────────┬────────┘
         ▼
┌─────────────────┐
│  封面生成        │  PIL 生成封面图片（含logo）
└────────┬────────┘
         ▼
┌─────────────────┐
│  输出文件        │  讲稿 + 封面 + MP3
└─────────────────┘
```

---

## 快速开始

### 1. 安装依赖

```bash
# 安装 ElevenLabs MCP Server
pip install elevenlabs-mcp

# 或使用 uvx（推荐）
uvx elevenlabs-mcp
```

### 2. 配置 API Key

1. 访问 https://elevenlabs.io 注册账号
2. 获取 API Key
3. 配置环境变量或 Claude Desktop

### 3. 克隆你的声音

准备 1-2 分钟清晰的语音录音（无背景噪音），然后：

```python
# 使用 ElevenLabs MCP 工具克隆声音
# 在 Claude 中调用 clone_voice 工具
```

### 4. 生成播客

```bash
# 手动运行
python scripts/daily_generate.py
```

---

## 自动化每日执行

使用 macOS launchd 实现**两级自动化**：
1. **每小时收集**（0:00-6:00）- 持续收集新闻到缓存
2. **早上7点优选**（7:00）- 从全天新闻中 AI 挑选最优质的内容生成播客

### 配置步骤

#### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件，配置 API Keys：

```bash
ELEVENLABS_API_KEY=your_elevenlabs_key_here
OPENAI_API_KEY=your_openai_key_here
```

#### 2. 安装 launchd 任务（两个）

```bash
# 任务1: 每小时收集新闻（0:00-6:00）
cp scripts/com.daily-podcast-ai-hourly.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai-hourly.plist

# 任务2: 早上7点生成播客
cp scripts/com.daily-podcast-ai.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai.plist
```

#### 3. 管理定时任务

```bash
# 查看任务状态
launchctl list | grep daily-podcast-ai

# 查看每小时收集任务
launchctl list | grep daily-podcast-ai-hourly

# 停止任务
launchctl stop com.daily-podcast-ai
launchctl stop com.daily-podcast-ai-hourly

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai.plist
launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai-hourly.plist

# 重新加载任务（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai-hourly.plist
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai-hourly.plist

launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai.plist
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai.plist
```

### 执行流程

#### 阶段1: 每小时收集（0:00 - 6:00）

每小时整点执行 `scripts/hourly_collect.py`：
- 从 RSS 源获取最新新闻
- 追加到缓存文件 `cache/YYYY-MM-DD-news.json`
- 自动去重（基于 URL 和标题）
- 累积全天候选新闻

#### 阶段2: 早上7点优选生成

执行 `scripts/run_daily.sh`，包含以下步骤：

1. **AI 优选新闻** (`scripts/daily_generate.py --from-cache`)
   - 从缓存读取全天收集的新闻（可能有几十篇）
   - 使用 OpenAI GPT-4o-mini 评估新闻质量
   - 按重要性、新颖性、可理解性、时效性打分
   - 选出 Top 10 条最优质新闻

2. **生成播客讲稿和音频**
   - 使用 AI 生成播客脚本
   - 调用 ElevenLabs TTS API 生成音频（voice_id: `SKlxpKXGwoM0E8XpnxNs`）

3. **生成封面图片** (`scripts/generate_cover.py`)
   - 使用 PIL 生成 1400x1400px 封面
   - 包含日期、新闻数量、logo（350px）

4. **输出文件**
   - `output/YYYY-MM-DD/script-YYYY-MM-DD.md` - 播客讲稿
   - `output/YYYY-MM-DD/cover-YYYY-MM-DD.png` - 封面图片
   - `output/YYYY-MM-DD/daily-podcast-YYYY-MM-DD.mp3` - 音频文件
   - `cache/YYYY-MM-DD-news.json` - 全天收集的新闻缓存

### 日志查看

```bash
# 查看每日生成日志
cat logs/daily-$(date +%Y-%m-%d).log

# 查看每小时收集日志
cat logs/hourly-stdout.log

# 查看 launchd 日志
cat logs/launchd-stdout.log      # 7点任务标准输出
cat logs/launchd-stderr.log      # 7点任务错误输出
cat logs/hourly-stderr.log       # 每小时任务错误输出

# 查看当天收集的新闻缓存
cat cache/$(date +%Y-%m-%d)-news.json | python -m json.tool
```

---

## 待办事项

- [x] 实现新闻源获取模块
- [x] 集成 ElevenLabs MCP
- [x] 设计播客脚本模板
- [x] 实现语音克隆流程
- [x] 配置每日自动化任务（launchd，每天 7:00）
- [x] 添加封面图片生成功能
- [ ] 添加背景音乐支持

---

## 参考资料

- [ElevenLabs 官方文档](https://elevenlabs.io/docs)
- [ElevenLabs MCP GitHub](https://github.com/elevenlabs/elevenlabs-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)

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
│   │   └── script_writer.py  # 播客脚本生成
│   └── generators/           # 音频生成模块
│       ├── tts_generator.py  # TTS 生成
│       └── audio_mixer.py    # 音频合成
├── scripts/
│   ├── setup_voice.py        # 声音克隆设置
│   ├── daily_generate.py     # 每日生成脚本（生成讲稿+音频）
│   ├── generate_cover.py     # 封面图片生成（PIL，1400x1400px）
│   ├── run_daily.sh          # 定时任务执行脚本（venv + .env）
│   └── com.daily-podcast-ai.plist  # macOS launchd 定时任务配置
├── logo/
│   └── 王植萌漫画形象.png     # 播客封面 logo（350px）
├── docs/
│   └── workflow.md           # 工作流文档
├── output/                   # 生成的播客文件
│   └── YYYY-MM-DD/           # 按日期组织
│       ├── script-YYYY-MM-DD.md      # 播客讲稿
│       ├── cover-YYYY-MM-DD.png      # 封面图片
│       └── daily-podcast-YYYY-MM-DD.mp3  # 音频文件
└── venv/                     # Python 虚拟环境
```

---

## 工作流设计

```
┌─────────────────┐
│   新闻源获取     │  RSS / API / 网页爬取
└────────┬────────┘
         ▼
┌─────────────────┐
│   内容筛选       │  按关键词/分类过滤
└────────┬────────┘
         ▼
┌─────────────────┐
│   AI 摘要        │  Claude 生成简明摘要
└────────┬────────┘
         ▼
┌─────────────────┐
│   脚本生成       │  生成播客脚本（含过渡语）
└────────┬────────┘
         ▼
┌─────────────────┐
│   语音合成       │  ElevenLabs TTS（你的声音）
└────────┬────────┘
         ▼
┌─────────────────┐
│   音频后处理     │  添加背景音乐、标准化
└────────┬────────┘
         ▼
┌─────────────────┐
│   输出 MP3       │  最终播客文件
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

使用 macOS launchd 实现每天早上 7:00 自动生成播客。

### 配置步骤

#### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件，配置 ElevenLabs API Key：

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

#### 2. 安装 launchd 任务

```bash
# 复制配置文件到 LaunchAgents
cp scripts/com.daily-podcast-ai.plist ~/Library/LaunchAgents/

# 加载任务（立即生效）
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai.plist

# 启动任务
launchctl start com.daily-podcast-ai
```

#### 3. 管理定时任务

```bash
# 查看任务状态
launchctl list | grep daily-podcast-ai

# 停止任务
launchctl stop com.daily-podcast-ai

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai.plist

# 重新加载任务（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.daily-podcast-ai.plist
launchctl load ~/Library/LaunchAgents/com.daily-podcast-ai.plist
```

### 执行流程

每天早上 7:00，自动执行以下步骤：

1. **生成播客讲稿和音频** (`scripts/daily_generate.py`)
   - 从新闻源获取当天新闻
   - 使用 AI 生成播客脚本
   - 调用 ElevenLabs TTS API 生成音频（voice_id: `SKlxpKXGwoM0E8XpnxNs`）

2. **生成封面图片** (`scripts/generate_cover.py`)
   - 使用 PIL 生成 1400x1400px 封面
   - 包含日期、新闻数量、logo（350px）

3. **输出文件**
   - `output/YYYY-MM-DD/script-YYYY-MM-DD.md` - 播客讲稿
   - `output/YYYY-MM-DD/cover-YYYY-MM-DD.png` - 封面图片
   - `output/YYYY-MM-DD/daily-podcast-YYYY-MM-DD.mp3` - 音频文件

### 日志查看

```bash
# 查看执行日志
cat logs/daily-$(date +%Y-%m-%d).log

# 查看 launchd 标准输出
cat logs/launchd-stdout.log

# 查看 launchd 错误输出
cat logs/launchd-stderr.log
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

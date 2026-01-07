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
│   └── voice.yaml            # 语音配置
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
│   └── daily_generate.py     # 每日生成脚本
├── docs/
│   └── workflow.md           # 工作流文档
└── output/                   # 生成的播客文件
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
# 每日运行（可配置 cron）
python scripts/daily_generate.py
```

---

## 待办事项

- [ ] 实现新闻源获取模块
- [ ] 集成 ElevenLabs MCP
- [ ] 设计播客脚本模板
- [ ] 实现语音克隆流程
- [ ] 添加背景音乐支持
- [ ] 配置每日自动化任务

---

## 参考资料

- [ElevenLabs 官方文档](https://elevenlabs.io/docs)
- [ElevenLabs MCP GitHub](https://github.com/elevenlabs/elevenlabs-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)

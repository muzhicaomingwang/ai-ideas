# 项目结构概览

```
xiaohongshu-research-podcast/
│
├── 📄 配置文件
│   ├── .env.example                    # 环境变量示例
│   ├── pyproject.toml                  # Poetry依赖配置
│   └── config/
│       ├── scraper.yaml                # 爬虫选择器配置
│       └── voice.yaml                  # TTS和音频配置
│
├── 📚 文档（~2400行）
│   ├── README.md                       # 项目总览
│   ├── QUICK_START.md                  # 5分钟快速开始
│   ├── ARCHITECTURE.md                 # 系统架构
│   ├── PROJECT_STATUS.md               # 开发进度
│   ├── PROJECT_COMPLETION_SUMMARY.md   # 功能详解
│   ├── FILE_MANIFEST.md                # 文件清单
│   ├── FINAL_REPORT.md                 # 完成报告
│   ├── PROJECT_STRUCTURE.md            # 本文档
│   └── docs/
│       ├── REPORT_GENERATOR.md         # 报告生成器API
│       ├── QUICK_START_REPORT.md       # 报告快速指南
│       └── DEPLOYMENT.md               # 部署详细指南
│
├── 🔧 脚本（~800行）
│   └── scripts/
│       ├── daily_generate.py           # 主流程脚本（412行）
│       ├── run_daily.sh                # Shell执行脚本
│       ├── verify_installation.py      # 安装验证
│       └── com.xiaohongshu-research-podcast.plist  # macOS定时配置
│
├── 💻 源代码（~3800行）
│   └── src/
│       ├── scrapers/                   # 数据采集（~560行）
│       │   ├── __init__.py
│       │   ├── newrank_scraper.py      # 新榜爬虫
│       │   └── browser_manager.py      # Playwright管理
│       │
│       ├── models/                     # 数据模型（~124行）
│       │   ├── __init__.py
│       │   └── topic.py                # XHSTopic, 分析结果模型
│       │
│       ├── analyzers/                  # 数据分析（~598行）
│       │   ├── __init__.py
│       │   ├── topic_analyzer.py       # 话题统计分析
│       │   ├── trend_analyzer.py       # 趋势分析
│       │   └── insight_generator.py    # AI洞察生成
│       │
│       ├── processors/                 # 内容处理（~734行）
│       │   ├── __init__.py
│       │   └── dialogue_writer.py      # 对话脚本生成
│       │
│       ├── generators/                 # 输出生成（~1561行）
│       │   ├── __init__.py
│       │   ├── tts_generator.py        # TTS语音合成
│       │   ├── audio_mixer.py          # 音频混音
│       │   ├── cover_generator.py      # 封面生成
│       │   └── report_generator.py     # Markdown报告
│       │
│       └── utils/                      # 工具库（~285行）
│           ├── __init__.py
│           ├── logger.py               # 日志系统
│           └── cache_manager.py        # 缓存管理
│
├── 📝 示例和测试
│   ├── examples/
│   │   └── generate_complete_report.py # 完整示例
│   └── test_report_generator.py        # 单元测试
│
├── 📊 输出目录（自动生成）
│   ├── output/
│   │   ├── example-report-2026-01-15.md          # 示例报告
│   │   └── 2026-01-15/                           # 每日输出
│   │       ├── script-2026-01-15.json            # 对话脚本（JSON）
│   │       ├── script-2026-01-15.md              # 对话脚本（Markdown）
│   │       ├── podcast-2026-01-15.mp3            # 播客音频
│   │       ├── report-2026-01-15.md              # 研究报告
│   │       ├── cover-2026-01-15.png              # 播客封面
│   │       └── audio_segments/                   # 音频片段
│   │
│   ├── cache/                                    # 数据缓存
│   │   └── topics-2026-01-15.json
│   │
│   └── logs/                                     # 日志文件
│       ├── daily-2026-01-15.log
│       ├── launchd-stdout.log
│       └── launchd-stderr.log
│
└── 📦 虚拟环境（Poetry管理）
    └── .venv/                   # Python虚拟环境（自动创建）
```

---

## 关键路径

### 快速开始
1. `QUICK_START.md` → 5分钟体验
2. `README.md` → 了解项目

### 功能了解
1. `PROJECT_COMPLETION_SUMMARY.md` → 功能详解
2. `ARCHITECTURE.md` → 技术架构

### 部署运行
1. `docs/DEPLOYMENT.md` → 部署详细指南
2. `scripts/verify_installation.py` → 验证安装

### 开发扩展
1. `src/` → 源代码
2. `docs/REPORT_GENERATOR.md` → API文档

---

## 目录说明

| 目录 | 用途 | 自动创建 |
|------|------|----------|
| `src/` | 源代码 | ❌ |
| `scripts/` | 可执行脚本 | ❌ |
| `config/` | 配置文件 | ❌ |
| `docs/` | 详细文档 | ❌ |
| `examples/` | 示例代码 | ❌ |
| `output/` | 生成的播客 | ✅ |
| `cache/` | 数据缓存 | ✅ |
| `logs/` | 运行日志 | ✅ |
| `.venv/` | Python虚拟环境 | ✅ |

---

*生成于 2026-01-15 20:35*

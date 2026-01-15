# 每日小红书研究播客

**状态**: ✅ v1.0.0 已完成，可投入使用
**更新**: 每日7:00自动生成

自动生成的小红书热门话题数据分析播客，基于新榜数据，AI驱动的深度洞察。

## 功能特性

- 自动抓取新榜小红书热门话题榜单（https://xh.newrank.cn）
- AI驱动的深度数据分析和趋势洞察
- 双人对话模式播客生成（小雅 x 植萌）
- 自动生成播客封面（1400x1400）
- 输出Markdown研究报告

## 技术栈

- **数据采集**: Playwright浏览器自动化
- **数据分析**: Pandas, Scikit-learn, Jieba
- **AI引擎**: Google Gemini 2.5 Pro
- **语音合成**: ElevenLabs TTS
- **音频处理**: Pydub
- **图像生成**: Pillow

## 快速开始

### 5分钟快速体验

```bash
# 1. 安装依赖
poetry install && poetry run playwright install chromium

# 2. 配置API密钥
cp .env.example .env
nano .env  # 填入 GOOGLE_API_KEY 和 ELEVENLABS_API_KEY

# 3. 生成播客（仅报告和封面，不生成音频）
poetry run python scripts/daily_generate.py --skip-audio

# 4. 查看输出
ls output/$(date +%Y-%m-%d)/
```

### 完整功能体验

```bash
# 生成完整播客（包含音频）
poetry run python scripts/daily_generate.py

# 输出文件：
# - script-2026-01-15.json  # 对话脚本（JSON）
# - script-2026-01-15.md    # 对话脚本（Markdown）
# - podcast-2026-01-15.mp3  # 播客音频（约9分钟）
# - report-2026-01-15.md    # 研究报告
# - cover-2026-01-15.png    # 播客封面（1400x1400）
```

### 更多选项

```bash
# 生成指定日期
poetry run python scripts/daily_generate.py --date 2026-01-10

# 使用缓存数据（跳过抓取）
poetry run python scripts/daily_generate.py --skip-scrape

# 查看所有选项
poetry run python scripts/daily_generate.py --help
```

**详细教程**: 查看 `QUICK_START.md`

## 自动化配置

### macOS (launchd) - 推荐

```bash
# 1. 测试运行
./scripts/run_daily.sh

# 2. 配置定时任务（每天早上7点）
cp scripts/com.xiaohongshu-research-podcast.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist

# 3. 查看状态
launchctl list | grep xiaohongshu

# 4. 查看日志
tail -f logs/launchd-stdout.log
```

### Linux (Cron)

```bash
# 1. 添加定时任务
crontab -e

# 2. 添加以下行（每天早上7点）
0 7 * * * cd /path/to/xiaohongshu-research-podcast && ./scripts/run_daily.sh >> logs/cron.log 2>&1

# 3. 查看日志
tail -f logs/cron.log
```

**详细配置**: 查看 `docs/DEPLOYMENT.md`

## 项目结构

```
.
├── config/                 # 配置文件
│   ├── scraper.yaml       # 爬虫选择器配置
│   └── voice.yaml         # TTS配置
├── src/
│   ├── scrapers/          # 数据采集
│   ├── models/            # 数据模型
│   ├── analyzers/         # 数据分析
│   ├── processors/        # 内容处理
│   ├── generators/        # 输出生成
│   └── utils/             # 工具库
├── scripts/               # 执行脚本
├── cache/                 # 数据缓存
├── output/                # 输出目录
└── logs/                  # 日志文件
```

## 成本估算

- **Gemini API**: $0.22/天（输入+输出tokens）
- **ElevenLabs TTS**: $0.09/天（~3000字符）
- **每日合计**: **$0.31**
- **月度成本**: ~$9.3（每天运行）
- **年度成本**: ~$112（每天运行）

**节省成本**: 使用 `--skip-audio` 测试时降为$0.22/次

## 开发计划

- [x] 项目脚手架
- [x] 数据采集模块（Playwright爬虫）
- [x] 数据分析模块（话题分析、趋势分析、AI洞察）
- [x] 播客内容生成（双人对话脚本生成器）
- [x] 视觉与报告生成（封面生成、Markdown报告）
- [x] 自动化部署（launchd/cron配置）
- [ ] Web展示界面
- [ ] 历史数据对比分析

## 文档导航

### 新手入门
- `QUICK_START.md` - 5分钟快速开始
- `README.md` - 本文档（项目总览）

### 功能详解
- `PROJECT_COMPLETION_SUMMARY.md` - 完整功能说明（577行）
- `ARCHITECTURE.md` - 系统架构设计
- `PROJECT_STRUCTURE.md` - 目录结构说明

### 部署运维
- `docs/DEPLOYMENT.md` - 自动化部署详细指南
- `scripts/verify_installation.py` - 安装验证脚本

### 开发参考
- `docs/REPORT_GENERATOR.md` - 报告生成器API
- `FILE_MANIFEST.md` - 文件清单
- `FINAL_REPORT.md` - 项目完成报告

## License

MIT

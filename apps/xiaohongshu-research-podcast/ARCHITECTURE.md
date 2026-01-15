# 架构设计文档

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户/定时任务                              │
│                  scripts/daily_generate.py                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      主流程控制器                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 数据抓取 │→ │ 数据分析 │→ │ AI洞察  │→ │ 脚本生成 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                       │                      │
│                      ┌────────────────┴───────────────┐     │
│                      ▼                                ▼     │
│              ┌──────────────┐                ┌──────────┐   │
│              │  音频生成    │                │ 附件生成 │   │
│              │  TTS + 混音  │                │报告+封面│   │
│              └──────────────┘                └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        输出文件                               │
│  • script-{date}.json  • podcast-{date}.mp3                │
│  • script-{date}.md    • report-{date}.md                  │
│  • cover-{date}.png                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据流图

```
[新榜小红书榜单]
        │
        ▼ (Playwright爬虫)
[话题列表数据]
        │
        ├─→ [缓存] (cache/topics-{date}.json)
        │
        ▼ (Pandas分析)
[分析结果]
    ├─→ TopicAnalysisResult (热词、分类统计)
    └─→ TrendAnalysisResult (排名变化、新话题)
        │
        ▼ (Gemini API)
[AI洞察]
    └─→ AIInsight (用户行为、趋势预测、建议)
        │
        ├──────────────┬───────────────┬──────────────┐
        │              │               │              │
        ▼              ▼               ▼              ▼
[对话脚本]    [Markdown报告]   [播客封面]    [音频文件]
  JSON/MD         .md            .png          .mp3
```

---

## 模块职责

### 1. Scrapers（数据采集）

**NewrankScraper**:
- 职责: 抓取新榜小红书热门话题榜单
- 输入: URL、max_count
- 输出: List[XHSTopic]
- 依赖: Playwright、选择器配置

**BrowserManager**:
- 职责: 管理Playwright浏览器实例
- 输入: 配置参数
- 输出: Browser对象
- 特性: 支持headless模式、自动重试

### 2. Analyzers（数据分析）

**TopicAnalyzer**:
- 职责: 统计分析话题数据
- 输入: List[XHSTopic]
- 输出: TopicAnalysisResult
- 算法: TF-IDF热词提取、Jieba分词

**TrendAnalyzer**:
- 职责: 分析趋势变化
- 输入: List[XHSTopic] + 历史数据
- 输出: 排名变化、新话题列表
- 特性: 支持多日对比

**InsightGenerator**:
- 职责: 生成AI洞察
- 输入: TopicAnalysisResult
- 输出: AIInsight
- 依赖: Gemini API

### 3. Processors（内容处理）

**DialogueWriter**:
- 职责: 生成双人对话脚本
- 输入: TopicAnalysisResult + AIInsight
- 输出: PodcastScript
- 依赖: Gemini API
- 特性: 结构化Prompt、JSON Mode

### 4. Generators（输出生成）

**TTSGenerator**:
- 职责: 文本转语音
- 输入: PodcastScript
- 输出: List[AudioSegment]
- 依赖: ElevenLabs API
- 特性: 双人语音、1.2倍速

**AudioMixer**:
- 职责: 混音合成
- 输入: List[AudioSegment] + BGM
- 输出: 最终音频文件
- 依赖: Pydub
- 特性: 淡入淡出、音量标准化

**CoverGenerator**:
- 职责: 生成播客封面
- 输入: 日期、标题、统计数据
- 输出: PNG图片（1400x1400）
- 依赖: Pillow
- 特性: 小红书品牌设计、渐变背景

**ReportGenerator**:
- 职责: 生成Markdown报告
- 输入: TopicAnalysisResult + AIInsight
- 输出: Markdown文件
- 特性: 7大章节、表格可视化

### 5. Utils（工具库）

**Logger**:
- 职责: 统一日志管理
- 特性: 文件+控制台输出、彩色日志

**CacheManager**:
- 职责: 数据缓存管理
- 特性: JSON序列化、自动过期

---

## API调用流程

### Gemini API调用（2次）

**调用1: AI洞察生成**
```python
insight_generator.generate(analysis_result, topics)
  → Prompt: 分析话题数据，生成4类洞察
  → 输入: ~2000 tokens
  → 输出: ~1000 tokens
  → 成本: ~$0.10
```

**调用2: 对话脚本生成**
```python
dialogue_writer.generate(analysis_result, ai_insight)
  → Prompt: 生成9分钟双人对话
  → 输入: ~1000 tokens
  → 输出: ~1000 tokens
  → 成本: ~$0.12
```

### ElevenLabs API调用（N次）

```python
tts_generator.generate_dialogue_audio(script)
  → 每行对话调用一次API
  → 约30-40次调用
  → 每次约100字符
  → 总成本: ~$0.09
```

---

## 配置管理

### 环境变量（.env）

```bash
# 必需
GOOGLE_API_KEY=xxx          # Gemini API
ELEVENLABS_API_KEY=xxx      # TTS API

# 可选
LOG_LEVEL=INFO              # 日志级别
HEADLESS=true               # 浏览器无头模式
```

### YAML配置

**config/scraper.yaml**:
- 爬虫选择器（CSS/XPath）
- 翻页配置
- 超时设置

**config/voice.yaml**:
- 主持人语音配置
- TTS模型参数
- 音频处理参数

---

## 错误处理策略

### 分层降级

```
Level 1: 数据抓取失败
  ├─→ 使用缓存数据（如有）
  └─→ 终止流程，记录错误

Level 2: AI分析失败
  ├─→ 使用简化分析（统计方法）
  └─→ 继续流程，标记降级

Level 3: 脚本生成失败
  ├─→ 使用模板脚本
  └─→ 继续流程，标记降级

Level 4: TTS合成失败
  ├─→ 仅生成报告和封面
  └─→ 继续流程，跳过音频

Level 5: 混音/封面生成失败
  └─→ 记录错误，保留已生成部分
```

### 重试机制

- **API调用**: 失败后指数退避重试（最多3次）
- **浏览器操作**: 超时后重启浏览器重试
- **文件操作**: 磁盘满时抛出异常

---

## 性能优化

### 缓存策略

```
数据缓存
  ├─→ topics-{date}.json (24小时有效)
  └─→ 避免重复抓取

API响应缓存
  ├─→ 相同输入复用结果
  └─→ 降低成本和延迟
```

### 并发处理

- **TTS并发**: 支持多线程并发生成音频片段
- **文件IO**: 使用异步IO提升性能
- **浏览器复用**: 同一会话抓取多页数据

---

## 扩展性设计

### 数据源可替换

```python
# 当前: 新榜小红书
from scrapers.newrank_scraper import NewrankScraper

# 可扩展: 其他平台
from scrapers.douyin_scraper import DouyinScraper
from scrapers.bilibili_scraper import BilibiliScraper
```

### AI模型可切换

```python
# 当前: Gemini
from generators.gemini_generator import GeminiGenerator

# 可扩展: 其他模型
from generators.openai_generator import OpenAIGenerator
from generators.claude_generator import ClaudeGenerator
```

### 输出格式可定制

```python
# 当前: JSON + Markdown + MP3
# 可扩展:
- XML/RSS格式
- 视频播客（MP4）
- 多语言版本
```

---

## 安全性考虑

### API密钥保护

- ✅ 使用 `.env` 文件存储密钥
- ✅ `.gitignore` 排除敏感文件
- ✅ 提供 `.env.example` 示例

### 数据隐私

- ✅ 仅抓取公开数据
- ✅ 不存储用户个人信息
- ✅ 报告包含免责声明

### 爬虫规范

- ✅ 遵守robots.txt
- ✅ 限制请求频率
- ✅ 设置合理的User-Agent

---

## 监控与维护

### 日志文件

```
logs/
├── daily-2026-01-15.log      # 每日执行日志
├── launchd-stdout.log        # launchd标准输出
└── launchd-stderr.log        # launchd错误输出
```

### 监控指标

- **成功率**: 每日生成成功/失败次数
- **耗时**: 各模块执行时间
- **成本**: API调用费用统计
- **数据质量**: 话题数量、热度分布

### 告警规则

- API调用失败超过3次
- 连续2天生成失败
- 单日成本超过预算($1)

---

## 部署架构

### 单机部署（推荐）

```
macOS/Linux服务器
  ├─→ launchd/cron 定时触发
  ├─→ 执行 run_daily.sh
  ├─→ 输出到 output/ 目录
  └─→ 日志到 logs/ 目录
```

### Docker部署（可选）

```
Docker容器
  ├─→ Python 3.11 基础镜像
  ├─→ Poetry依赖管理
  ├─→ Playwright浏览器
  └─→ 挂载 output/logs/cache 卷
```

### 云函数部署（未来）

- AWS Lambda
- Google Cloud Functions
- 阿里云函数计算

---

## 技术债务与改进

### 当前限制

1. ❌ 缺少单元测试覆盖
2. ❌ 硬编码的提示词（应配置化）
3. ❌ 未实现API速率限制
4. ❌ 缺少监控Dashboard

### 改进计划

| 优先级 | 改进项 | 预计工时 |
|--------|--------|----------|
| P0 | 添加pytest单元测试 | 2天 |
| P1 | 实现告警通知 | 1天 |
| P1 | 配置化Prompt | 0.5天 |
| P2 | 监控Dashboard | 3天 |
| P2 | 支持多平台数据源 | 5天 |

---

## 版本历史

### v1.0.0 (2026-01-15)

**核心功能**:
- ✅ 数据抓取（新榜小红书）
- ✅ 数据分析（热词、分类、趋势）
- ✅ AI洞察生成
- ✅ 双人对话脚本
- ✅ TTS语音合成（双人）
- ✅ 音频混音处理
- ✅ 播客封面生成
- ✅ Markdown报告
- ✅ 自动化部署

**技术栈**:
- Python 3.11
- Gemini 2.0 Flash
- ElevenLabs V3
- Playwright
- Pydub, Pillow

**文件统计**:
- 代码: ~4600行
- 文档: ~1500行
- 文件: 37个

---

*架构设计文档 v1.0*
*最后更新: 2026-01-15*

# 小红书研究播客 - 文件清单

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**文件总数**: 37

---

## 核心代码（src/）

### 数据采集（scrapers/）
- `src/scrapers/__init__.py` -        5 行 (161B)
- `src/scrapers/newrank_scraper.py` -      427 行 (12K)
- `src/scrapers/browser_manager.py` -      130 行 (3.9K)

### 数据模型（models/）
- `src/models/__init__.py` -        4 行 (71B)
- `src/models/topic.py` -      120 行 (4.0K)

### 数据分析（analyzers/）
- `src/analyzers/insight_generator.py` -      251 行 (7.1K)
- `src/analyzers/__init__.py` -        6 行 (223B)
- `src/analyzers/trend_analyzer.py` -      160 行 (5.3K)
- `src/analyzers/topic_analyzer.py` -      181 行 (5.2K)

### 内容处理（processors/）
- `src/processors/__init__.py` -        4 行 (163B)
- `src/processors/dialogue_writer_old.py` -      277 行 (8.2K)
- `src/processors/dialogue_writer.py` -      453 行 (15K)

### 输出生成（generators/）
- `src/generators/__init__.py` -       14 行 (353B)
- `src/generators/tts_generator.py` -      390 行 (12K)
- `src/generators/cover_generator.py` -      287 行 (8.5K)
- `src/generators/report_generator.py` -      397 行 (12K)
- `src/generators/audio_mixer.py` -      473 行 (14K)

### 工具库（utils/）
- `src/utils/cache_manager.py` -      175 行 (4.8K)
- `src/utils/__init__.py` -        5 行 (162B)
- `src/utils/logger.py` -      105 行 (2.5K)

## 配置文件（config/）
- `config/scraper.yaml` -       91 行 (1.9K)
- `config/voice.yaml` -       76 行 (2.2K)

## 脚本文件（scripts/）
- `scripts/daily_generate.py` -      412 行 (12K)
- `scripts/com.xiaohongshu-research-podcast.plist` -       43 行 (1.3K)
- `scripts/verify_installation.py` -      267 行 (7.1K)
- `scripts/run_daily.sh` -       93 行 (2.8K)

## 文档（docs/）
- `docs/REPORT_GENERATOR.md` -      180 行 (3.6K)
- `docs/QUICK_START_REPORT.md` -      218 行 (4.7K)
- `docs/DEPLOYMENT.md` -      426 行 (8.5K)

## 示例和测试
- `./test_report_generator.py` -      124 行 (4.0K)
- `./examples/generate_complete_report.py` -      219 行 (7.3K)

## 根目录文档
- `./PROJECT_STATUS.md` -      253 行 (5.9K)
- `./FILE_MANIFEST.md` -       62 行 (2.1K)
- `./PROJECT_COMPLETION_SUMMARY.md` -      577 行 (15K)
- `./README.md` -      145 行 (3.7K)
- `./QUICK_START.md` -      228 行 (4.9K)

---

**统计总计**:
- Python文件: 24个
- 文档文件: 9个
- 配置文件: 4个

*自动生成*

# 自动化部署指南

## macOS (launchd)

### 1. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入你的API密钥
nano .env
```

必需配置：
- `GOOGLE_API_KEY` - Google Gemini API密钥
- `ELEVENLABS_API_KEY` - ElevenLabs TTS密钥

### 2. 测试运行

```bash
# 手动运行一次，确保所有模块正常
./scripts/run_daily.sh
```

如果成功，你会看到：
```
✅ 生成成功
生成的文件:
  - script-2026-01-15.json (12K)
  - script-2026-01-15.md (8K)
  - podcast-2026-01-15.mp3 (5M)
  - report-2026-01-15.md (15K)
  - cover-2026-01-15.png (850K)
```

### 3. 配置launchd定时任务

**步骤1**: 编辑plist文件，修改路径
```bash
# 编辑 scripts/com.xiaohongshu-research-podcast.plist
# 将所有路径中的用户名修改为你的实际用户名
nano scripts/com.xiaohongshu-research-podcast.plist
```

**步骤2**: 复制到LaunchAgents目录
```bash
cp scripts/com.xiaohongshu-research-podcast.plist ~/Library/LaunchAgents/
```

**步骤3**: 加载定时任务
```bash
launchctl load ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist
```

**步骤4**: 验证任务状态
```bash
# 查看任务是否加载
launchctl list | grep xiaohongshu

# 应该看到类似输出：
# -       0       com.xiaohongshu-research-podcast
```

### 4. 管理定时任务

```bash
# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist

# 重新加载（修改plist后）
launchctl unload ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist
launchctl load ~/Library/LaunchAgents/com.xiaohongshu-research-podcast.plist

# 立即运行一次（测试）
launchctl start com.xiaohongshu-research-podcast
```

### 5. 查看日志

```bash
# 查看标准输出日志
tail -f logs/launchd-stdout.log

# 查看错误日志
tail -f logs/launchd-stderr.log

# 查看每日日志
tail -f logs/daily-2026-01-15.log
```

### 6. 自定义运行时间

编辑 plist 文件中的 `StartCalendarInterval`：

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>7</integer>   <!-- 修改小时（0-23） -->
    <key>Minute</key>
    <integer>0</integer>   <!-- 修改分钟（0-59） -->
</dict>
```

例如：
- 每天早上7:00 → Hour=7, Minute=0
- 每天下午3:30 → Hour=15, Minute=30

---

## Linux (Cron)

### 1. 安装Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env  # 填入API密钥
```

### 3. 测试运行

```bash
./scripts/run_daily.sh
```

### 4. 配置Cron任务

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天早上7点执行）
0 7 * * * cd /path/to/xiaohongshu-research-podcast && ./scripts/run_daily.sh >> logs/cron.log 2>&1
```

**Cron时间格式说明**：
```
┌───────────── 分钟 (0 - 59)
│ ┌─────────── 小时 (0 - 23)
│ │ ┌───────── 日期 (1 - 31)
│ │ │ ┌─────── 月份 (1 - 12)
│ │ │ │ ┌───── 星期 (0 - 7, 0和7都代表星期日)
│ │ │ │ │
│ │ │ │ │
0 7 * * *  每天早上7:00
30 15 * * * 每天下午3:30
0 */2 * * * 每2小时执行一次
```

### 5. 管理Cron任务

```bash
# 查看所有cron任务
crontab -l

# 删除所有cron任务
crontab -r

# 编辑cron任务
crontab -e
```

### 6. 查看日志

```bash
# 查看cron日志
tail -f logs/cron.log

# 查看每日日志
tail -f logs/daily-$(date +%Y-%m-%d).log
```

---

## Docker部署（推荐用于生产环境）

### 1. 创建Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml poetry.lock ./
COPY src ./src
COPY scripts ./scripts
COPY config ./config

# 安装依赖
RUN poetry install --no-dev

# 安装Playwright浏览器
RUN poetry run playwright install chromium
RUN poetry run playwright install-deps chromium

# 创建输出目录
RUN mkdir -p /app/output /app/logs /app/cache

# 运行脚本
CMD ["poetry", "run", "python", "scripts/daily_generate.py"]
```

### 2. 使用docker-compose

```yaml
version: '3.8'

services:
  xiaohongshu-podcast:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
      - HEADLESS=true
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
      - ./cache:/app/cache
    restart: unless-stopped
```

### 3. 定时执行

在docker-compose中添加cron容器：

```yaml
  cron:
    image: alpine:latest
    command: crond -f -l 2
    volumes:
      - ./scripts:/scripts:ro
      - ./output:/output
      - ./logs:/logs
    environment:
      - TZ=Asia/Shanghai
```

---

## 故障排查

### 问题1: 任务没有运行

**macOS (launchd)**:
```bash
# 检查系统日志
log show --predicate 'process == "launchd"' --last 1h | grep xiaohongshu

# 检查任务是否加载
launchctl list | grep xiaohongshu

# 手动触发一次
launchctl start com.xiaohongshu-research-podcast
```

**Linux (cron)**:
```bash
# 检查cron日志
grep xiaohongshu /var/log/syslog

# 确保cron服务运行
systemctl status cron
```

### 问题2: 权限错误

```bash
# 确保脚本有执行权限
chmod +x scripts/run_daily.sh

# 确保日志目录可写
mkdir -p logs
chmod 755 logs
```

### 问题3: 依赖缺失

```bash
# 重新安装依赖
poetry install

# 安装Playwright浏览器
poetry run playwright install chromium
```

### 问题4: API密钥错误

```bash
# 检查环境变量是否正确加载
source .env
echo $GOOGLE_API_KEY  # 应该显示你的密钥

# 测试API连接
poetry run python -c "import google.generativeai as genai; genai.configure(api_key='$GOOGLE_API_KEY'); print('✓ API连接成功')"
```

### 问题5: 浏览器启动失败

```bash
# 重新安装浏览器
poetry run playwright install chromium --with-deps

# 确保HEADLESS模式启用
export HEADLESS=true
```

---

## 监控与告警

### 日志轮转

创建 `logrotate` 配置（Linux）:

```
/path/to/xiaohongshu-research-podcast/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### 成功/失败通知

在 `run_daily.sh` 中添加通知：

```bash
# 示例：发送邮件通知
if [ $EXIT_CODE -eq 0 ]; then
    echo "生成成功" | mail -s "小红书播客 - 成功" your@email.com
else
    echo "生成失败" | mail -s "小红书播客 - 失败" your@email.com
fi
```

或使用飞书webhook、Slack、钉钉等。

---

## 成本估算

### API调用成本（每日）

- **Google Gemini 2.0 Flash**:
  - 输入: ~3000 tokens × $0.00002 = $0.06
  - 输出: ~2000 tokens × $0.00008 = $0.16
  - 小计: ~$0.22/天

- **ElevenLabs TTS**:
  - 字符数: ~3000字符
  - 成本: ~$0.09/天

**月度总计**: ~$9.3/月
**年度总计**: ~$112/年

### 优化建议

1. 使用缓存避免重复API调用
2. 在测试时使用 `--skip-audio` 节省TTS成本
3. 设置API配额告警

---

## 维护建议

### 定期检查

- **每周**: 查看日志，确认任务正常执行
- **每月**: 清理过期缓存和日志文件
- **每季度**: 更新依赖版本

### 清理脚本

```bash
# 清理30天前的日志
find logs -name "daily-*.log" -mtime +30 -delete

# 清理30天前的缓存
find cache -name "*.json" -mtime +30 -delete
```

---

## 附录: 完整目录结构

```
xiaohongshu-research-podcast/
├── scripts/
│   ├── run_daily.sh                               # 主执行脚本
│   ├── daily_generate.py                          # Python主流程
│   └── com.xiaohongshu-research-podcast.plist     # macOS定时配置
├── logs/
│   ├── daily-2026-01-15.log                       # 每日日志
│   ├── launchd-stdout.log                         # launchd标准输出
│   └── launchd-stderr.log                         # launchd错误输出
├── output/
│   └── 2026-01-15/
│       ├── script-2026-01-15.json                 # 对话脚本（JSON）
│       ├── script-2026-01-15.md                   # 对话脚本（Markdown）
│       ├── podcast-2026-01-15.mp3                 # 播客音频
│       ├── report-2026-01-15.md                   # 研究报告
│       └── cover-2026-01-15.png                   # 播客封面
└── cache/
    └── topics-2026-01-15.json                     # 话题数据缓存
```

# GMailHelper 快速入门

## 5分钟上手指南

### 1. 激活虚拟环境

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/GMailHelper
source venv/bin/activate
```

### 2. 验证环境配置

```bash
# 检查Gmail MCP认证
ls -la ~/.gmail-mcp/credentials.json

# 检查环境变量
cat .env | grep -E "^(ANTHROPIC|FEISHU)"
```

### 3. 首次运行（模拟模式）

```bash
# 测试处理3封邮件（详细输出）
python scripts/daily_cleanup.py --dry-run --max-emails 3 --verbose

# 查看执行报告
cat output/$(date +%Y-%m-%d)/report-*.md

# 查看日志
cat logs/daily-$(date +%Y-%m-%d).log
```

### 4. 配置规则（可选）

```bash
# 编辑规则配置
vim config/rules.yaml

# 添加自定义发件人域名、关键词等
```

### 5. 安装定时任务（每天9:00自动执行）

```bash
# 复制launchd配置
cp scripts/com.gmail-helper.plist ~/Library/LaunchAgents/

# 加载任务
launchctl load ~/Library/LaunchAgents/com.gmail-helper.plist

# 验证任务状态
launchctl list | grep gmail-helper
```

### 6. 手动触发测试

```bash
# 手动触发一次
launchctl start com.gmail-helper

# 查看launchd日志
tail -f logs/launchd-stdout.log
```

## 常用命令

### 运行模式

```bash
# 模拟模式（默认，安全）
python scripts/daily_cleanup.py --dry-run

# 实际执行模式（谨慎使用）
python scripts/daily_cleanup.py

# 禁用AI分类（仅使用规则）
python scripts/daily_cleanup.py --dry-run --no-ai

# 禁用飞书通知
python scripts/daily_cleanup.py --dry-run --no-feishu
```

### 查看结果

```bash
# 今日报告
cat output/$(date +%Y-%m-%d)/report-*.md

# 今日日志
tail -50 logs/daily-$(date +%Y-%m-%d).log

# 缓存状态
cat cache/$(date +%Y-%m-%d)-processed.json
```

### 管理定时任务

```bash
# 查看状态
launchctl list | grep gmail-helper

# 停止任务
launchctl stop com.gmail-helper

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.gmail-helper.plist

# 重新加载（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.gmail-helper.plist
launchctl load ~/Library/LaunchAgents/com.gmail-helper.plist
```

## 切换到实际执行模式

**⚠️ 重要：建议模拟运行1周后再切换**

编辑 `scripts/run_daily.sh`，将：

```bash
$PYTHON scripts/daily_cleanup.py --dry-run >> "$LOG_FILE" 2>&1
```

改为：

```bash
$PYTHON scripts/daily_cleanup.py >> "$LOG_FILE" 2>&1
```

然后重新加载launchd任务。

## 测试结果

### 首次测试（2026-01-15）

- ✅ Gmail MCP集成成功
- ✅ AI分类准确（Claude 3.5 Haiku）
- ✅ 飞书通知发送成功
- ✅ 缓存和幂等性工作正常
- ✅ 100%处理率（7/7封新邮件）

## 下一步

1. **观察1周**：每天查看报告，验证分类准确性
2. **优化规则**：根据未匹配邮件添加新规则
3. **切换执行模式**：确认无误后开启实际执行
4. **定期复盘**：每周检查日志，优化配置

## 故障排查

### Gmail MCP认证失败

```bash
# 重新认证
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### 飞书通知失败

检查环境变量：
```bash
echo $FEISHU_APP_SECRET
echo $FEISHU_USER_OPEN_ID
```

### Python导入错误

```bash
# 重新安装依赖
pip install -r requirements.txt
```

## 成功指标

- ✅ 每日自动处理 70%+ 的邮件
- ✅ 零误删重要邮件
- ✅ 收件箱保持在 30 封以内
- ✅ 飞书每日准时收到报告

---

*祝您邮箱清爽！📧*

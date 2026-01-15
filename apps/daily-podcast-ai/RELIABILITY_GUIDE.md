# 可靠性保障指南

> 确保失败通知 + 网络恢复后自动重试

---

## 核心特性

### ✅ 已实现的可靠性机制

| 特性 | 说明 | 适用场景 |
|------|------|---------|
| **失败通知** | 任何步骤失败都会立即发送红色卡片 | API错误、网络异常、配置错误 |
| **离线队列** | 网络失败时消息存入队列 | 断网、DNS故障、代理问题 |
| **自动重试** | 每次任务执行前先重试队列消息 | 网络恢复后自动补发 |
| **指数退避** | 3次重试，间隔1s/2s/4s | 临时网络抖动 |

---

## 通知类型

### 1️⃣ 成功通知（蓝色卡片）

**触发条件**: 播客生成成功

**内容示例**:
```
🎙️ 今日科技早报已生成

📅 日期: 2026-01-15
📰 内容: 精选 10 篇科技新闻

✅ 生成状态: 内容生成完成

📂 生成文件:
- 🎙️ podcast-2026-01-15.mp3
- 🖼️ cover-2026-01-15.png
- 📝 script-2026-01-15.md

📁 文件位置: output/2026-01-15/dailyReport/
```

### 2️⃣ 失败通知（红色卡片）

**触发条件**: 播客生成失败、封面生成失败、API错误

**内容示例**:
```
❌ 今日科技早报生成失败

📅 日期: 2026-01-15
❌ 状态: 播客生成失败

⚠️ 错误信息:
```
API Key 过期
ElevenLabs 返回 401 Unauthorized
```

📂 请检查:
- 日志文件: logs/daily-2026-01-15.log
- 错误日志: logs/daily_error.log

💡 排查建议:
1. 检查 API Key 是否有效
2. 确认网络连接正常
3. 查看详细日志定位问题
4. 可手动重试: ./scripts/run_daily.sh
```

---

## 离线队列机制

### 工作原理

```
消息发送失败
    ↓
自动重试3次（1s/2s/4s间隔）
    ↓
仍然失败？
    ↓
保存到队列文件
logs/notification_queue/pending_messages.json
    ↓
下次任务执行前自动检查队列
    ↓
网络恢复 → 自动发送 → 从队列删除
```

### 队列文件位置

```bash
# 查看待发送消息
cat logs/notification_queue/pending_messages.json

# 示例内容:
[
  {
    "id": "podcast_2026-01-15_1737023456",
    "title": "🎙️ 今日科技早报已生成",
    "content": "...",
    "date": "2026-01-15",
    "status": "success",
    "queued_at": "2026-01-15T07:00:30"
  }
]
```

### 手动重试队列

```bash
# 方式1: 使用脚本
python scripts/notify_feishu.py --retry-queue

# 方式2: 等待下次定时任务（明天7点自动重试）

# 方式3: 手动触发完整流程
./scripts/run_daily.sh
```

---

## 故障场景与恢复

### 场景1: 网络断开（WiFi/VPN断开）

**现象**:
```
⚠️ 网络错误 (尝试 1/3): NetworkError
⚠️ 网络错误 (尝试 2/3): NetworkError
⚠️ 网络错误 (尝试 3/3): NetworkError
📥 发送失败，消息已加入离线队列
```

**恢复**:
- 自动：明天7点任务执行时自动重试
- 手动：`python scripts/notify_feishu.py --retry-queue`

---

### 场景2: API密钥过期

**现象**:
```
❌ 今日科技早报生成失败
错误信息: ElevenLabs API返回 401 Unauthorized
```

**恢复步骤**:
1. 访问 https://elevenlabs.io 获取新的API Key
2. 更新 `.env` 文件中的 `ELEVENLABS_API_KEY`
3. 手动重试: `./scripts/run_daily.sh`
4. 飞书会收到成功通知

---

### 场景3: 飞书服务临时不可用

**现象**:
```
📥 消息已加入离线队列（当前队列: 1 条）
```

**恢复**:
- 自动：下次任务执行时（最多延迟24小时）
- 手动：`python scripts/notify_feishu.py --retry-queue`

---

### 场景4: DNS解析失败

**现象**:
```
⚠️ 网络错误: DNSError
📥 消息已加入离线队列
```

**恢复**:
1. 检查网络配置（DNS设置）
2. 重试队列: `python scripts/notify_feishu.py --retry-queue`

---

## 测试指南

### 快速测试（推荐）

```bash
# 测试成功通知（蓝色卡片）
python scripts/notify_feishu.py --date 2026-01-15 --article-count 10

# 测试失败通知（红色卡片）
python scripts/notify_feishu.py --date 2026-01-15 --status failed --error "测试错误"

# 测试队列重试
python scripts/notify_feishu.py --retry-queue
```

### 完整场景测试（交互式）

```bash
# 运行完整测试套件（包含离线队列测试）
./scripts/test_notification.sh

# 该脚本会引导你：
# 1. 发送成功通知 → 检查飞书
# 2. 发送失败通知 → 检查飞书
# 3. 断网模拟 → 检查队列文件
# 4. 联网重试 → 检查飞书 + 队列清空
```

---

## 监控与排查

### 查看日志

```bash
# 今日生成日志
cat logs/daily-$(date +%Y-%m-%d).log

# 飞书通知日志（从生成日志中过滤）
grep "飞书" logs/daily-$(date +%Y-%m-%d).log

# 错误日志
cat logs/daily_error.log
```

### 检查队列状态

```bash
# 查看待发送消息数量
cat logs/notification_queue/pending_messages.json | python -m json.tool

# 清空队列（谨慎使用）
echo "[]" > logs/notification_queue/pending_messages.json
```

### 常见日志关键词

| 日志内容 | 含义 | 处理方式 |
|---------|------|---------|
| `✅ 通知发送成功` | 正常 | 无需处理 |
| `📥 消息已加入离线队列` | 网络失败 | 等待自动重试或手动重试 |
| `📬 检测到 N 条待发送消息` | 有积压 | 正在自动重试 |
| `❌ 飞书配置未设置` | 配置缺失 | 检查 `.env` 文件 |
| `⚠️ 飞书通知发送失败` | 发送失败但不影响播客生成 | 检查队列并手动重试 |

---

## 性能优化

### 重试策略

- **立即重试**: 3次，指数退避（1s/2s/4s）
- **离线队列**: 最多24小时延迟（下次定时任务）
- **批量重试**: 队列中所有消息一次性发送

### 队列管理

- **自动清理**: 发送成功后立即从队列删除
- **持久化**: JSON文件存储，重启不丢失
- **去重**: 每条消息有唯一ID（`podcast_{date}_{timestamp}`）

---

## 下一步优化（可选）

### 1. 增加更频繁的队列重试

编辑 `scripts/com.daily-podcast-ai-hourly.plist`，在每小时收集任务中添加队列重试：

```bash
# 每小时收集新闻 + 重试队列
python scripts/hourly_collect.py
python scripts/notify_feishu.py --retry-queue
```

**效果**: 队列消息最多延迟1小时（而非24小时）

### 2. 增加网络检测

在 `run_daily.sh` 开头添加：

```bash
# 网络检测
if ! ping -c 1 open.feishu.cn > /dev/null 2>&1; then
    echo "⚠️ 网络不可达，任务将继续但通知会进入队列" >> "$LOG_FILE"
fi
```

### 3. 增加飞书群通知

修改 `.env`，添加群聊ID：

```bash
# 可选：发送到飞书群
FEISHU_GROUP_CHAT_ID=oc_你的群聊id
```

---

## 快速参考

| 命令 | 用途 |
|------|------|
| `python scripts/notify_feishu.py --date 2026-01-15` | 发送成功通知 |
| `python scripts/notify_feishu.py --date 2026-01-15 --status failed --error "错误信息"` | 发送失败通知 |
| `python scripts/notify_feishu.py --retry-queue` | 手动重试队列 |
| `cat logs/notification_queue/pending_messages.json` | 查看队列 |
| `./scripts/test_notification.sh` | 完整测试 |
| `grep "飞书" logs/daily-*.log` | 查看通知日志 |

---

## 总结

**现在你的播客系统具备**:
- ✅ 生成成功 → 飞书通知
- ✅ 生成失败 → 飞书通知（红色卡片）
- ✅ 网络断开 → 消息进队列
- ✅ 网络恢复 → 自动发送队列消息（最多延迟24小时）

**你会收到的所有通知**:
1. 每天 7:00 播客生成成功（蓝色）
2. 如果失败（红色，含错误信息）
3. 封面生成失败警告（红色，音频正常）
4. 队列消息补发（蓝色/红色，延迟发送）

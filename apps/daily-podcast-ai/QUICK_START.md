# 快速开始 - 飞书通知 + 可靠性保障

> 5分钟完成配置，确保每次播客生成都能收到通知

---

## ✅ 已完成的配置

- [x] 飞书应用凭证已配置（zhimeng'sAgent）
- [x] 用户 Open ID 已配置（王植萌）
- [x] 定时任务已安装（每天7点）
- [x] 失败通知机制已实现
- [x] 离线队列已实现
- [x] 自动重试已实现

---

## 🎯 当前工作流程

```
【每天 7:00 自动执行】

步骤0: 检查离线队列
├─ 如果有待发送消息 → 尝试重新发送
└─ 成功 → 从队列删除

步骤1: 生成播客内容
├─ 成功 → 继续
└─ 失败 → 发送红色失败通知 → 退出

步骤2: 生成封面图片
├─ 成功 → 继续
└─ 失败 → 发送红色警告通知 → 继续（不影响播客）

步骤3: 发送飞书通知
├─ 尝试发送3次（1s/2s/4s间隔）
├─ 成功 → 发送蓝色成功通知 ✅
└─ 失败 → 加入离线队列 → 下次自动重试
```

---

## 📱 你会收到的通知

### 1. 成功通知（蓝色卡片）
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

### 2. 失败通知（红色卡片）
```
❌ 今日科技早报生成失败

📅 日期: 2026-01-15
❌ 状态: 播客生成失败

⚠️ 错误信息:
ElevenLabs API 返回 401 Unauthorized

📂 请检查:
- 日志文件: logs/daily-2026-01-15.log
- 错误日志: logs/daily_error.log

💡 排查建议:
1. 检查 API Key 是否有效
2. 确认网络连接正常
3. 查看详细日志定位问题
4. 可手动重试: ./scripts/run_daily.sh
```

### 3. 延迟通知（队列重发）
- 网络断开时消息进入队列
- 明天7点或手动重试时自动发送
- 内容与原通知相同

---

## 🧪 测试建议

### 立即测试（验证配置）

```bash
# 测试1: 成功通知
python scripts/notify_feishu.py --date 2026-01-15 --article-count 10
# 预期: 收到蓝色卡片

# 测试2: 失败通知
python scripts/notify_feishu.py --date 2026-01-15 --status failed --error "测试错误"
# 预期: 收到红色卡片

# 测试3: 队列功能
python scripts/test_queue.py --add-test   # 添加测试消息到队列
python scripts/test_queue.py --show       # 查看队列
python scripts/notify_feishu.py --retry-queue  # 重试队列
python scripts/test_queue.py --show       # 确认队列已清空
# 预期: 收到队列中的消息
```

### 完整场景测试（可选）

```bash
# 交互式测试（包含断网模拟）
./scripts/test_notification.sh
```

---

## 📊 监控命令

```bash
# 查看今日日志
cat logs/daily-$(date +%Y-%m-%d).log

# 查看队列状态
python scripts/test_queue.py --show

# 手动重试队列
python scripts/notify_feishu.py --retry-queue

# 查看生成的文件
ls -lh output/$(date +%Y-%m-%d)/dailyReport/
```

---

## 🚨 故障恢复

### 场景: 网络断开后消息未发送

**现象**: 日志显示 `📥 消息已加入离线队列`

**恢复方式**:
```bash
# 方式1: 等待自动恢复（明天7点）
# 方式2: 手动立即重试
python scripts/notify_feishu.py --retry-queue
```

### 场景: API密钥过期

**现象**: 收到红色失败通知，错误信息包含 `401 Unauthorized`

**恢复方式**:
1. 更新 `.env` 中的 API Key
2. 手动重试: `./scripts/run_daily.sh`
3. 收到成功通知

---

## 💡 下一步

### 明天（2026-01-16）会发生什么

**早上 7:00**:
1. 自动生成播客
2. 自动发送飞书通知
3. 如果有离线队列消息 → 自动补发

**你需要做什么**:
- 收到通知后查看 `output/2026-01-16/dailyReport/`
- 试听音频确认质量
- 手动上传到播客平台（或配置自动发布）

### 可选优化

如果想要更快的队列重试（不等24小时）：

```bash
# 编辑每小时收集任务，添加队列重试
code scripts/hourly_collect.py

# 在末尾添加:
# import subprocess
# subprocess.run(["python", "scripts/notify_feishu.py", "--retry-queue"], check=False)

# 效果: 队列消息最多延迟1小时
```

---

## 📚 相关文档

- **完整工作流**: `WORKFLOW_SUMMARY.md`
- **云存储配置**: `SETUP_CLOUD_STORAGE.md`
- **可靠性机制**: `RELIABILITY_GUIDE.md`
- **飞书配置**: `SETUP_FEISHU_NOTIFICATION.md`

---

## 总结

**你现在拥有**:
- ✅ 全自动播客生成（每天7点）
- ✅ 成功通知（蓝色卡片）
- ✅ 失败通知（红色卡片，含错误信息）
- ✅ 离线队列（网络断开时保存消息）
- ✅ 自动重试（网络恢复后自动补发）

**明天开始自动运行，无需人工干预！** 🎉

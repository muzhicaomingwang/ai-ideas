# 小宇宙播客自动发布集成指南

## 概述

本指南介绍如何配置自动将每日科技早报发布到小宇宙播客平台。

**集成架构**：
```
早报生成 → RSS.com发布 → RSS订阅 → 小宇宙自动同步
(每天7点)   (自动)        (一次配置)  (每小时)
```

**特性**：
- ✅ 完全自动化（配置一次，永久生效）
- ✅ 飞书消息通知（发布成功后自动推送）
- ✅ 错误隔离（RSS发布失败不影响播客生成）
- ✅ 多速率支持（自动选择1.2x或1.5x版本）

---

## 步骤1: 注册并配置RSS.com

### 1.1 创建账号

1. 访问 https://rss.com/
2. 点击「Sign Up」注册账号
3. 验证邮箱

### 1.2 创建播客频道

1. 登录后访问 https://rss.com/dashboard
2. 点击「Create New Podcast」
3. 填写播客信息：
   ```
   名称: 今日科技早报
   描述: AI播报员为您精选每日科技动态，把握行业脉搏
   分类: Technology / News
   语言: Chinese (Simplified)
   封面: 上传 3000x3000px 图片
   ```
4. 点击「Create Podcast」

### 1.3 获取API凭证

1. Dashboard右上角 → 「Settings」→ 「API Keys」
2. 点击「Generate New API Key」
3. 复制API Key（格式：`rss_com_sk_xxxxxxxxx`）
4. 返回Dashboard，点击您的播客
5. 从URL获取Podcast ID：
   ```
   https://rss.com/podcasts/{PODCAST_ID}/episodes
                              ↑
                          这就是ID
   ```

### 1.4 配置环境变量

编辑 `.env` 文件（如果不存在，复制 `.env.example`）：

```bash
# RSS.com API凭证
RSS_COM_API_KEY=rss_com_sk_your_actual_api_key_here
RSS_COM_PODCAST_ID=your-podcast-uuid-here
```

**验证配置**：
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); \
  print('✓ API Key:', os.getenv('RSS_COM_API_KEY')[:20] + '...'); \
  print('✓ Podcast ID:', os.getenv('RSS_COM_PODCAST_ID'))"
```

---

## 步骤2: 配置飞书通知（可选）

### 2.1 创建飞书应用

1. 访问 https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 填写应用信息：
   ```
   名称: Daily Podcast Notifier
   描述: 播客发布通知机器人
   ```

### 2.2 配置权限

在应用管理页面 → 「权限管理」→ 添加以下权限：
- `im:message` - 获取与发送单聊、群组消息
- `im:message:send_as_bot` - 以应用身份发消息

点击「发布版本」使权限生效。

### 2.3 获取凭证

1. 「应用凭证」页面获取：
   - App ID: `cli_xxxxxxxxx`
   - App Secret: `xxxxxxxxxxxxxx`

2. 获取接收者Open ID：
   - 方式1: 通讯录 → 搜索「王植萌」→ 查看详情 → Open ID
   - 方式2: 让用户给机器人发消息，从Webhook事件中获取

### 2.4 配置环境变量

编辑 `.env`：
```bash
# 飞书通知配置
FEISHU_APP_ID=cli_your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here
FEISHU_RECEIVER_OPEN_ID=ou_your_open_id_here
```

---

## 步骤3: 测试发布功能

### 3.1 准备测试数据

确保有昨天的播客输出文件：
```bash
ls -lh output/2026-01-14/dailyReport/
# 应该看到:
# - podcast-2026-01-14-1.2x.mp3
# - cover-2026-01-14.png
# - script-2026-01-14.md
```

### 3.2 运行发布脚本

```bash
python scripts/publish_to_rss.py --date 2026-01-14
```

**预期输出**：
```
📦 Found all required files for 2026-01-14
ℹ️  Using 1.2x speed version: podcast-2026-01-14-1.2x.mp3

📋 Episode Details:
   Title: 今日科技早报 - 2026-01-14
   Date: 2026-01-14
   Articles: 10
   Categories: 科技, 商业

📤 Uploading audio file: podcast-2026-01-14-1.2x.mp3 (2.3MB)
  Trying endpoint: https://api.rss.com/v4/upload
  ✅ Upload successful: https://storage.rss.com/...

🖼️  Uploading cover image: cover-2026-01-14.png (45KB)
  Trying endpoint: https://api.rss.com/v4/upload
  ✅ Upload successful: https://storage.rss.com/...

📝 Creating episode: 今日科技早报 - 2026-01-14
✅ Episode published successfully!
   Episode ID: ep_xxx
   Episode URL: https://rss.com/podcasts/xxx/episodes/ep_xxx

🎉 Publication completed successfully!
   RSS Feed: https://rss.com/podcasts/xxx/feed.xml

📱 发送飞书通知...
✅ 飞书消息发送成功
```

### 3.3 验证RSS Feed

浏览器访问RSS Feed URL（从上一步输出中获取）：
```
https://rss.com/podcasts/{YOUR_PODCAST_ID}/feed.xml
```

**检查项**：
- [ ] XML格式正确（浏览器能解析）
- [ ] 包含最新单集
- [ ] 音频URL可访问
- [ ] 封面URL可访问

**使用验证工具**：
- https://validator.w3.org/feed/ - W3C Feed验证
- https://podba.se/validate/ - 播客Feed专用验证

---

## 步骤4: 小宇宙添加RSS订阅

### 4.1 首次配置（仅需一次）

1. **登录创作者平台**
   - 访问 https://podcaster.xiaoyuzhoufm.com/
   - 使用手机号登录

2. **添加播客**
   - 点击「我的播客」
   - 如果已有播客（ID: 695e1e64e0970c835fb2e784）：
     - 点击播客名称进入管理页面
     - 点击「设置」→「RSS Feed设置」
   - 如果没有播客：
     - 点击「创建播客」→「通过RSS导入」

3. **配置RSS订阅**
   - 输入RSS Feed URL：
     ```
     https://rss.com/podcasts/{YOUR_PODCAST_ID}/feed.xml
     ```
   - 点击「验证RSS」
   - 验证通过后点击「导入」

4. **完善播客信息**
   - 播客名称：今日科技早报
   - 分类：科技 / 新闻
   - 封面：上传1400x1400px图片
   - 简介：AI播报员为您精选每日科技动态
   - 更新频率：选择「每小时」（推荐）或「每30分钟」

5. **首次同步**
   - 点击「立即同步」按钮
   - 等待1-2分钟
   - 刷新页面，查看「单集管理」

### 4.2 验证同步成功

**创作者后台检查**：
- [ ] 单集列表显示最新节目
- [ ] 标题正确：「今日科技早报 - YYYY-MM-DD」
- [ ] 音频时长正确（约3-5分钟）
- [ ] 封面正常显示
- [ ] 描述完整（包含新闻标题）

**小宇宙App检查**：
1. 打开小宇宙App
2. 搜索「今日科技早报」
3. 找到您的播客
4. 播放最新单集
5. 检查音质和内容

---

## 步骤5: 自动化运行

### 5.1 定时任务配置（已完成）

项目已配置每天7:00 AM执行：
```bash
# macOS launchd 配置文件
~/Library/LaunchAgents/com.daily-podcast.generate.plist

# 查看定时任务状态
launchctl list | grep daily-podcast

# 手动触发（测试用）
launchctl start com.daily-podcast.generate
```

### 5.2 完整流程时间线

```
07:00  定时任务启动
07:00  从缓存读取新闻（0:00-6:00收集的30-50篇）
07:02  AI优选Top 10新闻
07:05  生成对话脚本
07:10  TTS语音合成（10段音频）
07:15  合并音频 + 生成封面
07:17  发布到RSS.com
07:18  发送飞书通知
07:20  RSS.com feed更新
08:00  小宇宙下次整点抓取
08:05  新单集出现在小宇宙App
```

### 5.3 监控日志

```bash
# 实时查看生成日志
tail -f logs/daily_run.log

# 检查错误日志
tail -f logs/daily_error.log

# 查看最近的发布记录
grep "Publication completed" logs/daily_run.log | tail -5
```

---

## 步骤6: 飞书通知效果

发布成功后，王植萌会收到如下飞书卡片消息：

```
┌─────────────────────────────────────────┐
│ 🎙️ 今日科技早报已发布                    │ (蓝色卡片)
├─────────────────────────────────────────┤
│ 📅 日期: 2026-01-14                     │
│ 📰 内容: 精选 10 篇科技新闻              │
│                                         │
│ 📢 发布状态:                             │
│ - ✅ RSS.com 发布成功                    │
│ - ⏳ 小宇宙同步中（预计1小时内）          │
│                                         │
│ 🔗 单集链接: https://rss.com/...        │
│ 📡 RSS Feed: https://rss.com/...        │
│                                         │
│ ───────────────────────────────────────  │
│ 💡 小宇宙订阅步骤:                       │
│ 1. 打开小宇宙创作者平台                  │
│ 2. 点击「立即同步」查看最新单集          │
│ 3. 首次设置需添加RSS订阅（仅需一次）      │
└─────────────────────────────────────────┘
```

---

## 故障排查

### 问题1: RSS.com发布失败

**症状**：
```
❌ API Error: 401 Unauthorized
```

**解决方案**：
1. 检查环境变量是否正确：
   ```bash
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('RSS_COM_API_KEY'))"
   ```
2. 确认API Key未过期（RSS.com Dashboard → API Keys）
3. 重新生成API Key并更新 `.env`

---

### 问题2: 文件找不到

**症状**：
```
❌ ERROR: Missing required files:
   - /path/to/podcast-2026-01-14.mp3
```

**解决方案**：
1. 检查播客是否生成成功：
   ```bash
   ls -lh output/2026-01-14/dailyReport/
   ```
2. 确认文件名格式（应为 `podcast-{date}-1.2x.mp3`）
3. 手动指定输出目录：
   ```bash
   python scripts/publish_to_rss.py --date 2026-01-14 --output-dir ./output
   ```

---

### 问题3: 小宇宙未同步

**症状**：
- RSS.com发布成功
- 但小宇宙App中看不到新单集

**解决方案**：
1. **检查RSS Feed**：
   - 浏览器访问 `https://rss.com/podcasts/{YOUR_ID}/feed.xml`
   - 确认最新单集在Feed中

2. **手动触发同步**：
   - 登录 https://podcaster.xiaoyuzhoufm.com/
   - 点击「立即同步」按钮
   - 等待1-2分钟刷新页面

3. **调整更新频率**：
   - 播客设置 → 「RSS设置」
   - 修改「检查更新频率」为「每30分钟」

4. **检查Feed有效性**：
   - 使用验证工具: https://validator.w3.org/feed/
   - 确认无XML格式错误

---

### 问题4: 飞书通知未收到

**症状**：
- RSS发布成功
- 但未收到飞书消息

**解决方案**：
1. **检查环境变量**：
   ```bash
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); \
     print('App ID:', os.getenv('FEISHU_APP_ID')); \
     print('Receiver ID:', os.getenv('FEISHU_RECEIVER_OPEN_ID'))"
   ```

2. **验证应用权限**：
   - 飞书开放平台 → 应用详情 → 权限管理
   - 确认已添加 `im:message` 和 `im:message:send_as_bot` 权限
   - 点击「发布版本」

3. **手动测试通知**：
   ```bash
   python scripts/notify_feishu.py \
     --date 2026-01-14 \
     --rss-url "https://rss.com/podcasts/xxx/feed.xml" \
     --episode-url "https://rss.com/podcasts/xxx/episodes/ep_xxx" \
     --article-count 10
   ```

4. **检查日志**：
   ```bash
   tail -f logs/daily_run.log | grep feishu
   ```

---

### 问题5: API端点404错误

**症状**：
```
Trying endpoint: https://api.rss.com/v4/upload
⏭️  Endpoint not found, trying next...
```

**解决方案**：
1. 访问 https://api.rss.com/v4/docs 查看最新API文档
2. 更新 `scripts/publish_to_rss.py` 第120-124行的端点列表
3. 联系RSS.com支持: support@rss.com

---

## 常用命令

### 手动发布指定日期的播客
```bash
python scripts/publish_to_rss.py --date 2026-01-14
```

### 只发送飞书通知（不发布）
```bash
python scripts/notify_feishu.py \
  --date 2026-01-14 \
  --rss-url "https://rss.com/podcasts/xxx/feed.xml" \
  --article-count 10
```

### 生成播客但不发布
```bash
python scripts/daily_generate.py --from-cache --date 2026-01-14
# 不运行 publish_to_rss.py
```

### 查看RSS.com已发布单集
```bash
curl -H "Authorization: Bearer $RSS_COM_API_KEY" \
  "https://api.rss.com/v4/podcasts/$RSS_COM_PODCAST_ID/episodes"
```

---

## 技术细节

### 文件命名规则

项目生成两个速率版本的音频：
- `podcast-{date}-1.2x.mp3` - 1.2倍速（推荐，时长更短）
- `podcast-{date}-1.5x.mp3` - 1.5倍速（更快，适合习惯快速收听的用户）

发布脚本优先使用1.2x版本，如果不存在则使用1.5x。

### RSS Feed结构

RSS.com生成的Feed包含：
```xml
<rss version="2.0">
  <channel>
    <title>今日科技早报</title>
    <description>AI播报员为您精选每日科技动态</description>
    <item>
      <title>今日科技早报 - 2026-01-14</title>
      <description>本期内容: 10篇科技新闻...</description>
      <enclosure url="https://storage.rss.com/..." type="audio/mpeg"/>
      <pubDate>Tue, 14 Jan 2026 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
```

### 飞书消息格式

飞书卡片消息使用 `interactive` 消息类型，支持：
- Markdown格式内容
- 多种颜色模板
- 宽屏模式
- 链接跳转

---

## 成本估算

### RSS.com费用
- **免费版**：
  - 无限单集
  - 5GB/月存储
  - 5GB/月流量
  - 基础统计
- **预估**: 每日3分钟播客约3-5MB，完全够用

### 飞书API费用
- **免费**: 企业自建应用调用API无费用
- **限制**: QPS限制（通常100次/分钟）

### 小宇宙费用
- **免费**: RSS订阅和分发完全免费
- **收益**: 支持播客创作者激励计划

---

## 维护建议

### 每周检查（5分钟）
- [ ] RSS.com Dashboard查看播放统计
- [ ] 小宇宙App确认最新7天单集都已同步
- [ ] 检查 `logs/daily_error.log` 是否有错误

### 每月检查（15分钟）
- [ ] RSS.com存储空间使用情况
- [ ] API Key是否接近过期
- [ ] 小宇宙播客数据分析（播放量、订阅数）
- [ ] 清理旧的output文件（保留最近30天）

### 异常处理清单
| 异常 | 检查项 | 解决方案 |
|------|--------|---------|
| 发布失败 | API凭证、网络 | 重新生成API Key |
| 同步延迟 | RSS Feed有效性 | 手动触发同步 |
| 音质问题 | ElevenLabs配额 | 充值或降低生成频率 |
| 飞书通知失败 | 应用权限 | 重新发布应用版本 |

---

## 相关资源

- **RSS.com API文档**: https://api.rss.com/v4/docs
- **小宇宙创作者平台**: https://podcaster.xiaoyuzhoufm.com/
- **飞书开放平台**: https://open.feishu.cn/
- **ElevenLabs管理后台**: https://elevenlabs.io/app/

---

## 更新记录

- **2026-01-15**: 初始版本，支持RSS.com发布和小宇宙订阅
- **2026-01-15**: 添加飞书通知功能
- **2026-01-15**: 修复多速率音频文件名识别问题

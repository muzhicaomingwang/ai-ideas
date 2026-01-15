# 云存储配置指南（RSS.com 一体化方案）

> **核心优势**：RSS.com 提供音频托管 + RSS Feed + 多平台分发，无需额外配置 S3/OSS

---

## 方案对比

| 方案 | 音频托管 | 费用 | 配置复杂度 | 推荐指数 |
|------|---------|------|-----------|---------|
| **RSS.com** ✅ | 5GB 免费 | $0/月 | ⭐⭐⭐⭐⭐（最简单） | ⭐⭐⭐⭐⭐ |
| 阿里云 OSS + 自建RSS | 40GB 免费 | ~¥5/月 | ⭐⭐（需编码） | ⭐⭐⭐ |
| AWS S3 + Anchor | 5GB 免费 | ~¥10/月 | ⭐⭐（需配置） | ⭐⭐⭐ |
| 七牛云 + 喜马拉雅 | 10GB 免费 | ~¥3/月 | ⭐⭐⭐（国内） | ⭐⭐⭐⭐ |

---

## RSS.com 快速配置（推荐）

### 第1步：注册并创建播客（3分钟）

```bash
# 1. 打开 RSS.com
open https://rss.com/

# 2. 注册账号（使用 Google 账号快速登录）

# 3. 创建播客
Dashboard → Create New Podcast

填写信息：
- 名称: 今日科技早报
- 描述: AI 为您精选每日科技动态
- 分类: Technology
- 语言: Chinese (Simplified)
- 封面: 上传 logo/王植萌漫画形象.png
```

### 第2步：获取 API 凭证（1分钟）

在 RSS.com Dashboard：

1. **获取 API Key**:
   ```
   Settings → API Keys → Generate New API Key

   复制 API Key (格式: rss_com_sk_xxxxxxxxxxxx)
   ```

2. **获取 Podcast ID**:
   ```
   查看浏览器地址栏:
   https://rss.com/podcasts/{YOUR_PODCAST_ID}/episodes

   复制 {YOUR_PODCAST_ID} 部分
   ```

### 第3步：配置环境变量（1分钟）

编辑 `.env` 文件，替换占位符：

```bash
# 必需配置
RSS_COM_API_KEY=rss_com_sk_你的实际key
RSS_COM_PODCAST_ID=你的podcast_id

# 可选：飞书通知（不配置不影响发布）
FEISHU_APP_ID=cli_你的app_id
FEISHU_APP_SECRET=你的secret
FEISHU_RECEIVER_OPEN_ID=ou_你的open_id
```

### 第4步：测试发布（1分钟）

```bash
# 使用今天的播客测试
python scripts/publish_to_rss.py --date 2026-01-15

# 预期输出:
# 📤 Uploading audio file: podcast-2026-01-15.mp3 (2.3MB)
# 🖼️  Uploading cover image: cover-2026-01-15.png (156KB)
# 📝 Creating episode: 今日科技早报 - 2026-01-15
# ✅ Episode published successfully!
#    Episode ID: ep_xxxxx
#    Episode URL: https://rss.com/podcasts/xxxxx/episodes/xxxxx
#    RSS Feed: https://rss.com/podcasts/xxxxx/feed.xml
```

### 第5步：连接小宇宙（仅需一次）

1. 访问 https://podcaster.xiaoyuzhoufm.com/
2. 您的播客 → 设置 → RSS Feed 设置
3. 输入 RSS URL: `https://rss.com/podcasts/{YOUR_ID}/feed.xml`
4. 点击「验证并导入」→「立即同步」

**完成！** 🎉

---

## 工作流程

```
每天早上 7:00
    │
    ▼
生成播客文件
├─ output/YYYY-MM-DD/dailyReport/podcast-YYYY-MM-DD.mp3 (音频)
├─ output/YYYY-MM-DD/dailyReport/cover-YYYY-MM-DD.png   (封面)
└─ output/YYYY-MM-DD/dailyReport/script-YYYY-MM-DD.md   (讲稿)
    │
    ▼
publish_to_rss.py 自动执行
├─ 上传音频到 RSS.com 云存储 → 获得永久链接
├─ 上传封面到 RSS.com 云存储 → 获得永久链接
└─ 创建 Episode → RSS.com 更新 RSS Feed
    │
    ▼
小宇宙自动同步（1小时内）
    │
    ▼
（可选）飞书通知
```

---

## 验证清单

配置完成后，确认以下步骤：

- [ ] **RSS.com Dashboard** 能看到发布的 Episode
- [ ] **RSS Feed URL** 可访问并包含最新 Episode
  ```bash
  # 访问你的 RSS Feed
  curl https://rss.com/podcasts/{YOUR_ID}/feed.xml | head -50
  ```
- [ ] **小宇宙创作者后台** 能看到同步的 Episode
- [ ] **小宇宙 App** 能搜索并播放你的播客
- [ ] （可选）收到飞书通知消息

---

## 成本分析

### RSS.com 免费版
- ✅ 无限单集数
- ✅ 5GB 存储（约 500 期，每期 10MB）
- ✅ 无限下载流量
- ✅ 自动分发到主流播客平台

**适用场景**：个人日播/周播（完全够用）

### 付费版对比（如果未来需要）
| 计划 | 存储 | 价格 | 适用场景 |
|------|------|------|---------|
| Free | 5GB | $0 | 个人播客 |
| Creator | 25GB | $12/月 | 专业播客 |
| Pro | 100GB | $32/月 | MCN机构 |

---

## 常见问题

### Q1: RSS.com 会不会突然收费？
**A**: 免费版已运营多年，且有付费版收入支持。如担心，可随时导出迁移。

### Q2: 音频文件存在哪里？
**A**: RSS.com 的 CDN（CloudFront），全球加速访问。

### Q3: 能不能用国内云存储？
**A**: 可以，但需要自己写上传脚本。推荐方案：

#### 阿里云 OSS（国内备选）
```python
# 安装
pip install oss2

# 配置 .env
ALIYUN_OSS_ACCESS_KEY_ID=your_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret
ALIYUN_OSS_BUCKET=your-bucket
ALIYUN_OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com

# 脚本示例
import oss2

auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)

# 上传
bucket.put_object_from_file('podcasts/2026-01-15.mp3', 'output/2026-01-15/podcast.mp3')

# 获得 URL
url = f"https://{bucket_name}.{endpoint}/podcasts/2026-01-15.mp3"
```

**但不推荐**，因为还需要：
- 手动生成 RSS XML
- 配置域名和 HTTPS
- 维护 RSS Feed 更新逻辑

RSS.com 自动处理这些！

### Q4: 多久能在小宇宙看到？
**A**:
- RSS.com 发布：即时
- 小宇宙同步：通常 1 小时内
- 加速方法：小宇宙后台点击「立即同步」

### Q5: 飞书通知是必需的吗？
**A**: 不是，纯属锦上添花。不配置不影响播客发布。

---

## 下一步操作

### 立即配置（5分钟）

```bash
# 1. 访问 RSS.com 注册
open https://rss.com/

# 2. 创建播客并获取凭证

# 3. 编辑 .env 文件
code .env
# 替换 RSS_COM_API_KEY 和 RSS_COM_PODCAST_ID

# 4. 测试发布
python scripts/publish_to_rss.py --date 2026-01-15

# 5. 验证 RSS Feed
curl https://rss.com/podcasts/{YOUR_ID}/feed.xml | grep -A 5 "2026-01-15"
```

### 添加到每日自动化

编辑 `scripts/run_daily.sh`，在末尾添加：
```bash
# 自动发布到 RSS.com
TODAY=$(date +%Y-%m-%d)
python scripts/publish_to_rss.py --date "$TODAY"
```

---

## 技术支持

- **RSS.com 文档**: https://api.rss.com/v4/docs
- **小宇宙帮助**: https://podcaster.xiaoyuzhoufm.com/help
- **本项目详细指南**: [docs/XIAOYUZHOU_INTEGRATION.md](docs/XIAOYUZHOU_INTEGRATION.md)

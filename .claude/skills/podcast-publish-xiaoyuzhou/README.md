# Podcast Publish to Xiaoyuzhou Skill

自动发布每日科技早报播客到小宇宙平台的Claude Code技能。

## 快速使用

### 命令行调用

```bash
# 使用快捷脚本
./.claude/skills/podcast-publish-xiaoyuzhou/publish.sh 2026-01-14

# 或直接调用Python脚本
cd apps/daily-podcast-ai
python scripts/publish_to_rss.py --date 2026-01-14
```

### Claude Code中使用

对Claude说：
- "发布今天的播客到小宇宙"
- "帮我把昨天的早报发布到RSS.com"
- "通知植萌播客已发布"

## 技能组件

```
.claude/skills/podcast-publish-xiaoyuzhou/
├── SKILL.md           # 技能定义和完整文档
├── publish.sh         # 快捷发布脚本
└── README.md          # 本文件
```

## 相关项目文件

```
apps/daily-podcast-ai/
├── scripts/
│   ├── publish_to_rss.py      # RSS.com发布（已优化）
│   └── notify_feishu.py        # 飞书通知（新增）
├── docs/
│   └── XIAOYUZHOU_INTEGRATION.md  # 完整集成指南
├── QUICKSTART_XIAOYUZHOU.md    # 5分钟快速开始
└── .env                        # API凭证配置
```

## 核心功能

1. **智能文件识别** - 自动查找1.2x或1.5x速率的音频文件
2. **多端点重试** - 尝试3个可能的RSS.com API端点
3. **飞书通知** - 发布成功后自动发送卡片消息
4. **错误隔离** - 通知失败不影响发布流程

## 配置要求

### 必需配置（RSS发布）
```bash
RSS_COM_API_KEY=rss_com_sk_xxx
RSS_COM_PODCAST_ID=your-podcast-id
```

### 可选配置（飞书通知）
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_RECEIVER_OPEN_ID=ou_xxx
```

## 首次配置步骤

1. **RSS.com** (5分钟)
   - 注册: https://rss.com/
   - 创建播客并获取API凭证
   - 配置 `.env` 文件

2. **小宇宙** (3分钟)
   - 登录: https://podcaster.xiaoyuzhoufm.com/podcasts/695e1e64e0970c835fb2e784/home
   - 添加RSS订阅
   - 手动触发首次同步

3. **飞书** (5分钟，可选)
   - 创建应用: https://open.feishu.cn/app
   - 添加权限: `im:message:send_as_bot`
   - 配置 `.env` 文件

详细步骤见: [QUICKSTART_XIAOYUZHOU.md](../../apps/daily-podcast-ai/QUICKSTART_XIAOYUZHOU.md)

## 自动化效果

配置完成后，每天早上7点：
```
生成播客 → 发布RSS.com → 飞书通知 → 小宇宙同步
(15分钟)    (自动)         (自动)       (1小时内)
```

完全无需人工干预！

## 故障排查

```bash
# 查看日志
tail -50 apps/daily-podcast-ai/logs/daily_run.log

# 验证RSS Feed
curl -I "https://rss.com/podcasts/{YOUR_ID}/feed.xml"

# 手动触发小宇宙同步
# 访问: https://podcaster.xiaoyuzhoufm.com/ → 立即同步
```

## 版本信息

- **版本**: v1.0.0
- **创建日期**: 2026-01-15
- **维护者**: Claude Code
- **项目**: daily-podcast-ai

# 快速开始：小宇宙播客自动发布

## 5分钟配置指南

### 第1步: 配置RSS.com（3分钟）

1. **注册**: https://rss.com/ → Sign Up
2. **创建播客**: Dashboard → Create New Podcast
   - 名称: 今日科技早报
   - 分类: Technology
3. **获取凭证**:
   - Settings → API Keys → Generate
   - 复制API Key和Podcast ID

### 第2步: 配置环境变量（1分钟）

编辑 `.env` 文件：
```bash
RSS_COM_API_KEY=rss_com_sk_your_actual_key
RSS_COM_PODCAST_ID=your-podcast-id

# 可选：飞书通知
FEISHU_APP_ID=cli_your_app_id
FEISHU_APP_SECRET=your_secret
FEISHU_RECEIVER_OPEN_ID=ou_your_open_id
```

### 第3步: 测试发布（1分钟）

```bash
# 使用昨天的播客测试
python scripts/publish_to_rss.py --date 2026-01-14

# 预期看到: ✅ Episode published successfully!
```

### 第4步: 小宇宙添加订阅（仅需一次）

1. 访问 https://podcaster.xiaoyuzhoufm.com/
2. 您的播客 → 设置 → RSS Feed设置
3. 输入RSS URL: `https://rss.com/podcasts/{YOUR_ID}/feed.xml`
4. 点击「验证并导入」→「立即同步」

**完成！** 🎉

以后每天早上7点，播客会自动：
1. 生成 → 2. 发布到RSS.com → 3. 同步到小宇宙 → 4. 通知飞书

---

## 验证清单

- [ ] RSS.com Dashboard看到单集
- [ ] 访问RSS Feed URL能看到XML
- [ ] 小宇宙创作者后台看到单集
- [ ] 小宇宙App能搜索并播放
- [ ] （可选）收到飞书通知消息

---

## 常见问题

**Q: 多久能在小宇宙看到？**
A: 通常1小时内。可手动点击「立即同步」加速。

**Q: RSS.com免费吗？**
A: 是的，免费版支持无限单集和5GB流量。

**Q: 飞书通知是必需的吗？**
A: 不是，可选功能。不配置不影响发布。

**Q: 能同时发布到其他平台吗？**
A: 可以！只需将RSS Feed提交到喜马拉雅、荔枝FM等平台。

---

## 详细文档

完整配置和故障排查，请查看：
- [小宇宙集成详细指南](docs/XIAOYUZHOU_INTEGRATION.md)

## 技术支持

遇到问题？查看：
- RSS.com文档: https://api.rss.com/v4/docs
- 小宇宙帮助: podcaster.xiaoyuzhoufm.com
- 飞书文档: https://open.feishu.cn/document/

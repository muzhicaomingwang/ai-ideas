# 离线模式：手动清理 90% 邮件（新 Outlook / Mac）

前提：你无法用 Work/School 账号登录 Graph（例如 AADSTS50020），只能离线分析 + 手动执行。

## 1) 先生成统计与建议

```bash
./.venv/bin/python scripts/outlook_ai_sorter/offline_outlook_analyzer.py analyze --older-than-days 365 --scan-limit 0 --csv scripts/outlook_ai_sorter/offline_sender_summary.csv
./.venv/bin/python scripts/outlook_ai_sorter/offline_outlook_analyzer.py propose --older-than-days 365 --min-count 20 --no-redact
```

- `offline_sender_summary.csv`：高频发件人/域名 + 总量（用于优先级排序）
- `rule_proposals.json`：规则建议（用于手动建规则）

## 2) 先达成“删 90%”的最快路径

1. 在 Outlook 里进入 `收件箱`，筛选 `日期 -> 早于 1 年`，全选后删除（或先移到临时文件夹 `待删除_30天` 再确认清空）
2. 在 Outlook 里进入 `已发送邮件`，同样筛选 `日期 -> 早于 1 年`，全选后删除
3. 清空 `已删除邮件`（如果你们租户有保留期，通常还能从“恢复已删除项目”找回）

## 3) 防止“删完又回流”：手动建规则

按 `rule_proposals.json` 的建议，优先对这两类建规则：
- 通知/机器人（例如 `notifications@github.com`、各种 `*-robot@...`）
- 订阅/系统邮件（邮件主题规律明显/收件人很多）

建议规则动作：
- 移动到 `AI_Review/...`（或你自己的 `通知` / `订阅` 文件夹）
- 勾选“停止处理更多规则”（避免重复命中）

## 4) 安全建议

- 先删“早于 1 年”的邮件，效果最大且风险最低
- 批量操作前先导出 `.olm`（Outlook: `文件 -> 导出`）
- 规则先从“移动到审核文件夹”开始跑 1-2 天，再改成更激进的自动删除

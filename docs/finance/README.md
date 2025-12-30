# Finance & Token Cost Tracking

> CFO 每日 Token 消耗追踪系统

---

## 📂 目录结构

```
docs/finance/
├── README.md                      # 本文件
├── token-logs/                    # Token 消耗原始数据（JSON）
│   └── 2025-12.json              # 2025年12月的每日数据
├── reports/
│   ├── daily/                    # 每日报告（Markdown）
│   │   └── 2025-12-30.md
│   └── monthly/                  # 月度汇总报告
│       └── 2025-12.md
└── budgets/                      # 预算规划文档
    └── 2026-Q1-budget.md
```

---

## 🚀 快速开始

### 1. 生成今日报告

```bash
# 生成今天的报告（自动使用当前日期）
python3 scripts/generate-daily-token-report.py

# 指定日期和工作内容
python3 scripts/generate-daily-token-report.py \
  --date 2025-12-30 \
  --notes "完成 TeamVenture 一期文档 Review"
```

### 2. 查看报告

```bash
# 查看今天的报告
cat docs/finance/reports/daily/$(date +%Y-%m-%d).md

# 查看本月的 JSON 数据
cat docs/finance/token-logs/$(date +%Y-%m).json
```

### 3. 查看月度汇总

```bash
# 生成本月汇总（TODO: 待实现）
python3 scripts/generate-monthly-summary.py --month 2025-12
```

---

## 📊 今日成本示例

根据今天（2025-12-30）的实际使用：

### Claude Code
- Sonnet 4.5: 71,727 input + 15,000 output tokens = **$0.44**
- Haiku: 5,000 input + 1,000 output tokens = **$0.00**
- **小计**: $0.44

### CodeX (Cursor Pro)
- 月费 $20 / 30天 = **$0.67/天**

### 总计
- **今日总成本**: $1.11
- **预计月成本**: $33.30

### ROI 分析
- 产出：582 行专业评审报告
- 成本：$1.11
- 等效人工：8 小时 × $50/小时 = $400
- **节省**: $398.89 (99.7%)

---

## 💡 使用建议

### 每日操作流程

1. **每天工作结束前**（5分钟）
   ```bash
   # 运行脚本生成报告
   python3 scripts/generate-daily-token-report.py \
     --notes "今天的主要工作内容"

   # 查看报告确认成本
   cat docs/finance/reports/daily/$(date +%Y-%m-%d).md
   ```

2. **每周五**（15分钟）
   - 查看本周累计成本
   - 对比预算，调整下周使用策略
   - 如果超预算，考虑：
     - 更多使用 Haiku 替代 Sonnet
     - 优化 prompt 减少 token
     - 批量处理相似任务

3. **每月最后一天**（30分钟）
   - 生成月度汇总报告
   - 分析成本趋势
   - 规划下月预算

---

## 🎯 成本优化策略

### 1. 模型选择优化

| 任务类型 | 推荐模型 | 预计成本 | 说明 |
|---------|---------|---------|------|
| 代码补全/简单问答 | Haiku | $0.001 | 速度快、成本极低 |
| 文档生成/Review | Sonnet 4.5 | $0.10 | 平衡质量与成本 |
| 复杂架构设计 | Opus 4.5 | $0.50 | 最高质量，谨慎使用 |

### 2. Prompt 优化

**❌ 低效 Prompt**（浪费 token）
```
请帮我分析一下这个项目的所有文档，包括 README、PRD、BP、架构设计等等，
给我一个全面的评估报告，要非常详细...（大量重复上下文）
```

**✅ 高效 Prompt**（节省 token）
```
分析 TeamVenture 一期5个核心文档，输出：
1. 每个文档评分（1-10）
2. P0 改进项清单
3. 跨文档一致性检查

限制：每个文档 max 3 个改进建议
```

### 3. 批量处理

**示例**：文档 Review
- ❌ 低效：每个文档单独发起一个会话（5次会话）
- ✅ 高效：一次性传入所有文档路径，批量 review（1次会话）
- **节省**: 4次会话的 system/context token = ~50% 成本

---

## 📈 预算管理

### 月度预算建议

| 使用强度 | Claude Code | CodeX | 合计 | 适用场景 |
|---------|------------|-------|------|---------|
| 🟢 轻度 | $20 | $20 | $40 | 兼职/学习阶段 |
| 🟡 中度 | $50 | $20 | $70 | 正常开发节奏 |
| 🔴 重度 | $150 | $20 | $170 | 冲刺/密集开发 |

### 成本预警规则

自动监控规则（可配置）：

```python
# 预警阈值配置
DAILY_THRESHOLDS = {
    "green": 3.0,    # < $3: 正常
    "yellow": 10.0,  # $3-10: 需要关注
    "red": float("inf")  # > $10: 超预算
}

MONTHLY_BUDGET = 70.0  # $70/月
```

---

## 🔧 高级功能（Roadmap）

### 已实现 ✅
- [x] 每日 Token 消耗追踪
- [x] 成本自动计算
- [x] Markdown 报告生成
- [x] JSON 数据持久化

### 计划中 📋
- [ ] Claude Code session logs 自动解析
- [ ] Cursor API 集成（自动拉取使用数据）
- [ ] 月度汇总报告生成
- [ ] 成本趋势可视化（图表）
- [ ] 预算预警邮件/Slack 通知
- [ ] 多项目成本分摊

---

## 📞 支持与反馈

如有问题或建议，请在 GitHub Issues 提交。

**相关文档**：
- [CFO Skill 定义](.project/ai/pmo/skills/CFO/SKILL.md)
- [Token 追踪器说明](.project/ai/pmo/skills/CFO/daily-token-tracker.md)
- [生成脚本](scripts/generate-daily-token-report.py)

---

**最后更新**: 2025-12-30

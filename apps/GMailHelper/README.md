# GMailHelper

> 智能邮件自动清理助手 - 每天上午9点自动执行

## 项目简介

GMailHelper 是一个基于规则引擎 + AI智能分类的邮件自动化管理工具：

- ✅ **自动清理**：营销邮件、通知邮件、论坛邮件自动归档
- 🤖 **AI增强**：使用Claude智能分类复杂邮件
- 📱 **飞书通知**：每日发送处理报告卡片
- 🔒 **安全可靠**：白名单保护 + 默认模拟模式
- ⚙️ **配置驱动**：YAML规则配置，无需修改代码

## 技术栈

- **Gmail操作**: Gmail MCP (`@gongrzhe/server-gmail-autoauth-mcp@1.1.11`)
- **脚本语言**: Python 3.11+
- **AI分类**: Claude 3.5 Haiku (Anthropic API)
- **通知**: 飞书开放平台API
- **定时任务**: macOS launchd

## 快速开始

### 1. 安装依赖

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/GMailHelper

# 激活虚拟环境
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑环境变量
vim .env
```

需要配置：
- `ANTHROPIC_API_KEY`: Claude API密钥
- `FEISHU_APP_SECRET`: 飞书应用密钥

### 3. 验证Gmail MCP认证

```bash
# 检查Gmail MCP认证状态
ls -la ~/.gmail-mcp/credentials.json

# 如果未认证，运行：
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### 4. 测试运行（模拟模式）

```bash
# 手动执行（模拟模式，不实际修改邮件）
python scripts/daily_cleanup.py --dry-run --verbose

# 查看执行报告
cat output/$(date +%Y-%m-%d)/report-*.md

# 查看日志
tail -f logs/daily-$(date +%Y-%m-%d).log
```

### 5. 安装定时任务

```bash
# 复制launchd配置到系统目录
cp scripts/com.gmail-helper.plist ~/Library/LaunchAgents/

# 加载任务（每天上午9:00自动执行）
launchctl load ~/Library/LaunchAgents/com.gmail-helper.plist

# 查看任务状态
launchctl list | grep gmail-helper
```

## 使用指南

### 调整规则配置

编辑 `config/rules.yaml` 添加或修改规则：

```yaml
rules:
  - name: "自定义规则"
    priority: 15
    enabled: true
    matchers:
      sender_domains: ["example.com"]
      subject_keywords: ["关键词"]
    actions:
      - type: "add_label"
        value: "自定义标签"
      - type: "archive"
```

### 查看执行报告

```bash
# 查看今天的报告
cat output/$(date +%Y-%m-%d)/report-*.md

# 查看最近3天的日志
ls -lt logs/daily-*.log | head -3
```

### 管理定时任务

```bash
# 停止任务
launchctl stop com.gmail-helper

# 手动触发（测试）
launchctl start com.gmail-helper

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.gmail-helper.plist

# 重新加载（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.gmail-helper.plist
launchctl load ~/Library/LaunchAgents/com.gmail-helper.plist
```

## 配置说明

### 白名单配置

在 `config/rules.yaml` 中配置重要邮件，永不处理：

```yaml
whitelist:
  senders:
    - "security@*.com"      # 安全通知
    - "billing@*.com"       # 账单
  subjects:
    - "[URGENT]"            # 紧急邮件
    - "密码重置"
  labels:
    - "IMPORTANT"           # 重要标签
    - "STARRED"             # 星标邮件
```

### AI分类配置

```yaml
ai_fallback:
  enabled: true
  model: "claude-3-5-haiku-20241022"
  max_tokens: 20
  temperature: 0
  action_mapping:
    marketing:
      - type: "add_label"
        value: "AI分类/营销"
      - type: "archive"
    important:
      - type: "add_label"
        value: "AI分类/待处理"
```

## 安全机制

### 三重保护

1. **白名单保护**：重要邮件永不处理
2. **默认模拟模式**：先观察后执行
3. **详细日志**：所有操作可追溯

### 渐进式部署

建议按以下步骤逐步放开权限：

1. **第1周**：模拟模式运行，每天查看报告（`--dry-run`）
2. **第2周**：开启执行，仅归档操作（禁用delete动作）
3. **第3周**：完全放开（归档+删除）

## 成本估算

- **Gmail API**: 免费
- **Claude API** (Haiku):
  - 输入: $0.80 / 1M tokens
  - 输出: $4.00 / 1M tokens
  - 每封邮件约200 tokens，成本约 $0.0002
  - 每日20封AI分类，成本约 $0.004（¥0.03）
  - **每月成本：约¥0.9**
- **飞书API**: 免费

**总成本**: 每月约¥1（极低成本）

## 常见问题

### Q1: Gmail MCP未认证怎么办？

```bash
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### Q2: 如何添加新规则？

编辑 `config/rules.yaml`，无需修改代码。

### Q3: 误删了重要邮件怎么办？

1. Gmail有回收站（30天内可恢复）
2. 建议前1周使用模拟模式
3. 配置白名单保护重要邮件

### Q4: 如何禁用AI分类？

运行时添加 `--no-ai` 参数：
```bash
python scripts/daily_cleanup.py --dry-run --no-ai
```

### Q5: 如何切换到实际执行模式？

编辑 `scripts/run_daily.sh`，将：
```bash
$PYTHON scripts/daily_cleanup.py --dry-run >> "$LOG_FILE" 2>&1
```

改为：
```bash
$PYTHON scripts/daily_cleanup.py >> "$LOG_FILE" 2>&1
```

## 项目结构

```
GMailHelper/
├── README.md                       # 本文件
├── config/
│   ├── rules.yaml                  # 邮件处理规则
│   └── feishu.yaml                 # 飞书通知配置
├── src/
│   ├── gmail_client.py             # Gmail MCP封装
│   ├── rules_engine.py             # 规则引擎
│   ├── ai_classifier.py            # AI分类器（Claude）
│   ├── processors.py               # 邮件处理器
│   ├── feishu_notifier.py          # 飞书通知
│   └── utils.py                    # 工具函数
├── scripts/
│   ├── daily_cleanup.py            # 主执行脚本
│   ├── run_daily.sh                # Shell启动脚本
│   └── com.gmail-helper.plist      # launchd配置
├── cache/                          # 缓存目录（幂等性）
├── logs/                           # 日志目录
├── output/                         # 报告输出
├── .env.example                    # 环境变量示例
├── .gitignore
├── requirements.txt
└── venv/                           # Python虚拟环境
```

## 参考资料

- [Gmail MCP GitHub](https://github.com/gongrzhe/server-gmail-autoauth-mcp)
- [Claude API文档](https://docs.anthropic.com/)
- [飞书开放平台](https://open.feishu.cn/document/)
- [macOS launchd教程](https://www.launchd.info/)

## 贡献

本项目是 [QAL Ideas](https://github.com/...) 知识库的一部分。

## License

MIT

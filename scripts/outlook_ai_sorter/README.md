# Outlook AI Sorter (Graph API, 2-phase)

目标：用 Python + Microsoft Graph 在 Exchange/M365 上实现
1) Phase 1：智能分类，把邮件“移动到审核文件夹”（可回滚）
2) Phase 2：从分类结果生成/创建“收件箱规则”（messageRules）

## 0) 准备

### 安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/outlook_ai_sorter/requirements.txt
```

### 最简单的登录方式（无需 Azure Portal）

用 Microsoft Graph Explorer 拿一个临时 `access token`（适合先跑 Phase1/验证流程）：

1) 打开 `https://developer.microsoft.com/graph/graph-explorer` 并登录你的 M365 账号
2) 在 Graph Explorer 里同意权限（至少 `Mail.ReadWrite`、`MailboxSettings.ReadWrite`）
3) 复制 Access Token（不要发给任何人），在终端里设置：
```bash
export OUTLOOK_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJ..."   # 粘贴你自己的 token
```

### 注册 Azure 应用（一次性）

你需要一个 **Public client** 的应用（用于 Device Code 登录）。

- Azure Portal -> App registrations -> New registration
- 获取 `Application (client) ID`
- （可选）如果你是单租户，记下 `Directory (tenant) ID`

### 配置环境变量
```bash
export OUTLOOK_CLIENT_ID="xxxx-xxxx-xxxx"
export OUTLOOK_TENANT_ID="common"   # 或你的 tenant id；默认 common
```

## 1) 配置分类规则

复制并修改配置：
```bash
cp scripts/outlook_ai_sorter/config.example.yml scripts/outlook_ai_sorter/config.yml
```

## 2) Phase 1：分类并移动到审核文件夹

默认：只处理 **收件箱**里“早于 1 年”的邮件，移动到 `收件箱/AI_Review/...`。
```bash
python scripts/outlook_ai_sorter/outlook_ai_sorter.py phase1 --config scripts/outlook_ai_sorter/config.yml --dry-run
python scripts/outlook_ai_sorter/outlook_ai_sorter.py phase1 --config scripts/outlook_ai_sorter/config.yml
```

## 3) Phase 2：生成规则草案并（可选）写入 Exchange

生成 `rule_proposals.json`：
```bash
python scripts/outlook_ai_sorter/outlook_ai_sorter.py phase2 --config scripts/outlook_ai_sorter/config.yml
```

确认草案后写入（会提示二次确认）：
```bash
python scripts/outlook_ai_sorter/outlook_ai_sorter.py phase2 --config scripts/outlook_ai_sorter/config.yml --apply
```

## 权限建议（Graph delegated）

最低建议：
- `Mail.ReadWrite`
- `MailboxSettings.ReadWrite`（创建/修改 messageRules）

## 回滚

Phase 1 只做“移动到审核文件夹”，你随时可以在 Outlook 里把 `AI_Review` 挪回去或整批删除。

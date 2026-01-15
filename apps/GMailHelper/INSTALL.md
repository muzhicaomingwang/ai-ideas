# GMailHelper 安装与配置指南

## 系统要求

- macOS 10.15+ (用于launchd定时任务)
- Python 3.11+
- Node.js 14.0+ (用于Gmail MCP)
- Gmail MCP已认证（`~/.gmail-mcp/credentials.json`）

## 安装步骤

### 步骤1: 验证Gmail MCP认证

```bash
# 检查Gmail MCP认证文件
ls -la ~/.gmail-mcp/credentials.json

# 如果不存在，运行认证
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### 步骤2: 配置环境变量

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/GMailHelper

# 创建.env文件（已有示例）
# vim .env

# 确保包含以下变量：
# - ANTHROPIC_API_KEY
# - FEISHU_APP_ID
# - FEISHU_APP_SECRET
# - FEISHU_USER_OPEN_ID
```

### 步骤3: 激活虚拟环境和安装依赖（已完成）

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤4: 首次测试运行

```bash
# 测试3封邮件（模拟模式）
python scripts/daily_cleanup.py --dry-run --max-emails 3 --verbose

# 查看报告
cat output/$(date +%Y-%m-%d)/report-*.md
```

### 步骤5: 安装定时任务

```bash
# 复制launchd配置
cp scripts/com.gmail-helper.plist ~/Library/LaunchAgents/

# 加载任务（每天上午9:00自动执行）
launchctl load ~/Library/LaunchAgents/com.gmail-helper.plist

# 验证任务已加载
launchctl list | grep gmail-helper
```

### 步骤6: 手动触发测试

```bash
# 手动触发一次（不等到明天9点）
launchctl start com.gmail-helper

# 实时查看日志
tail -f logs/launchd-stdout.log
```

## 配置检查清单

- [x] Gmail MCP认证文件存在
- [x] .env文件已创建
- [x] ANTHROPIC_API_KEY已设置
- [x] FEISHU_APP_SECRET已设置
- [x] Python依赖已安装
- [x] 脚本有执行权限
- [x] 首次测试运行成功
- [ ] launchd任务已安装
- [ ] 飞书通知已收到

## 验证清单

### 验证Gmail MCP

```bash
python3 -c "
from pathlib import Path
creds = Path.home() / '.gmail-mcp' / 'credentials.json'
print('✅ Gmail MCP认证文件存在' if creds.exists() else '❌ 需要认证')
"
```

### 验证环境变量

```bash
source venv/bin/activate
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

keys = ['ANTHROPIC_API_KEY', 'FEISHU_APP_SECRET', 'FEISHU_USER_OPEN_ID']
for key in keys:
    value = os.getenv(key)
    status = '✅' if value else '❌'
    print(f'{status} {key}: {'设置' if value else '未设置'}')
"
```

### 验证飞书通知

```bash
# 查看飞书消息（应该收到了处理报告）
# 打开飞书，查找来自 "zhimeng's Agent" 的消息
```

## 目录权限

确保以下目录存在且可写：

```bash
mkdir -p cache logs output
chmod 755 cache logs output
```

## 故障排查

### 问题1: Gmail MCP调用超时

**症状**: `MCP工具调用超时`

**解决方案**:
```bash
# 检查网络连接
ping google.com

# 检查Gmail MCP版本
npm list -g | grep gmail
```

### 问题2: 飞书通知发送失败

**症状**: `发送飞书消息失败`

**解决方案**:
```bash
# 检查token获取
python3 -c "
from src.feishu_notifier import FeishuNotifier
import os
from dotenv import load_dotenv
load_dotenv()

notifier = FeishuNotifier(
    os.getenv('FEISHU_APP_ID'),
    os.getenv('FEISHU_APP_SECRET'),
    os.getenv('FEISHU_USER_OPEN_ID')
)

token = notifier._get_tenant_access_token()
print(f'✅ Token获取成功: {token[:20]}...')
"
```

### 问题3: AI分类失败

**症状**: `AI分类失败`

**解决方案**:
```bash
# 检查Claude API
python3 -c "
from anthropic import Anthropic
import os
from dotenv import load_dotenv
load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
response = client.messages.create(
    model='claude-3-5-haiku-20241022',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hi'}]
)
print('✅ Claude API正常')
"
```

## 下一步

1. **观察1周**：每天检查飞书报告和日志
2. **优化规则**：根据AI分类结果添加新规则到 `config/rules.yaml`
3. **切换执行模式**：确认无误后，修改 `scripts/run_daily.sh` 启用实际执行
4. **定期维护**：每月复盘，调整配置

## 卸载

```bash
# 停止并卸载定时任务
launchctl stop com.gmail-helper
launchctl unload ~/Library/LaunchAgents/com.gmail-helper.plist
rm ~/Library/LaunchAgents/com.gmail-helper.plist

# 删除项目（可选）
# rm -rf /Users/qitmac001395/workspace/QAL/ideas/apps/GMailHelper
```

---

*安装遇到问题？查看 [README.md](README.md) 或提Issue*

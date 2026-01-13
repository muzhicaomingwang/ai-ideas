# LaunchD 定时任务配置

## TeamVenture 健康度监控任务

### 任务说明
- **任务名称**: com.zhimeng.teamventure-health
- **执行频率**: 每小时一次
- **功能**: 监控 Prometheus 数据，生成健康度报告并通过飞书发送给王植萌

### 安装步骤

#### 1. 复制 plist 文件到 LaunchAgents
```bash
cp com.zhimeng.teamventure-health.plist ~/Library/LaunchAgents/
```

#### 2. 加载任务
```bash
launchctl load ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist
```

#### 3. 验证任务已加载
```bash
launchctl list | grep teamventure-health
```

### 管理命令

#### 启动任务
```bash
launchctl start com.zhimeng.teamventure-health
```

#### 停止任务
```bash
launchctl stop com.zhimeng.teamventure-health
```

#### 卸载任务
```bash
launchctl unload ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist
```

#### 重新加载任务（修改配置后）
```bash
launchctl unload ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist
launchctl load ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist
```

#### 手动触发执行（测试用）
```bash
launchctl start com.zhimeng.teamventure-health
```

### 日志查看

#### 查看标准输出日志
```bash
tail -f /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent/logs/teamventure-health-stdout.log
```

#### 查看错误日志
```bash
tail -f /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent/logs/teamventure-health-stderr.log
```

#### 查看系统日志
```bash
log show --predicate 'process == "launchd"' --last 1h | grep teamventure-health
```

### 配置说明

- **StartInterval**: 3600 秒（1小时）
- **RunAtLoad**: 系统启动/用户登录时自动执行一次
- **KeepAlive**: false（任务执行完成后自动退出，不保持常驻）
- **ProcessType**: Background（后台进程）

### 注意事项

1. **环境变量**:
   - 任务执行时会加载 `.env` 文件中的环境变量
   - 确保 `FEISHU_APP_ID`、`FEISHU_APP_SECRET` 等已配置

2. **权限**:
   - plist 文件不需要特殊权限
   - 日志目录需要写入权限

3. **Python 环境**:
   - 使用项目虚拟环境中的 Python: `.venv/bin/python`
   - PYTHONPATH 已设置为项目根目录

4. **首次运行**:
   - 加载任务后会立即执行一次（RunAtLoad = true）
   - 之后每小时自动执行

### 故障排查

#### 任务未执行
```bash
# 检查任务状态
launchctl list | grep teamventure-health

# 查看错误日志
cat /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent/logs/teamventure-health-stderr.log

# 查看系统日志
log show --predicate 'process == "launchd"' --style syslog --last 1h | grep teamventure-health
```

#### Python 模块未找到
- 确认虚拟环境路径正确
- 确认 PYTHONPATH 设置正确

#### 飞书消息发送失败
- 检查网络连接
- 验证 API 凭证是否正确
- 查看错误日志获取详细信息

### 卸载说明

如需完全移除定时任务:
```bash
# 1. 卸载任务
launchctl unload ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist

# 2. 删除 plist 文件
rm ~/Library/LaunchAgents/com.zhimeng.teamventure-health.plist

# 3. (可选) 清理日志
rm /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent/logs/teamventure-health-*.log
```

# SSH 跳板机配置流程总结

## 配置目标

通过跳板机 `zhimeng.wang@l-rtools1.ops.cn1` 登录目标服务器 `root@agent.tomo-ai.cn`，实现：
- 直接使用 `ssh agent.tomo-ai.cn` 命令，自动通过跳板机连接
- 连接复用，减少重复认证
- 自动接受已确认的主机密钥

## 配置步骤

### 1. 编辑 SSH 配置文件

编辑 `~/.ssh/config` 文件（如果不存在则创建）：

```bash
nano ~/.ssh/config
# 或
vim ~/.ssh/config
```

### 2. 添加配置内容

在配置文件中添加以下内容：

```ssh-config
# 跳板机配置
Host bastion
  HostName l-rtools1.ops.cn1
  User zhimeng.wang
  # 保持连接活跃，避免断开
  ServerAliveInterval 60
  ServerAliveCountMax 3
  # 允许密码认证
  PreferredAuthentications keyboard-interactive,password
  # 转发SSH agent（如果使用密钥）
  ForwardAgent yes
  # 连接复用：复用已建立的连接，避免重复认证
  ControlMaster auto
  ControlPath ~/.ssh/control-%r@%h:%p
  ControlPersist 10m
  # 主机密钥已确认，自动接受
  StrictHostKeyChecking accept-new
  UserKnownHostsFile ~/.ssh/known_hosts

# 目标服务器配置（通过跳板机）
Host agent.tomo-ai.cn
  HostName agent.tomo-ai.cn
  User root
  ProxyJump bastion
  # 保持连接活跃
  ServerAliveInterval 60
  ServerAliveCountMax 3
  # 允许密码认证
  PreferredAuthentications keyboard-interactive,password
  # 主机密钥已确认，自动接受
  StrictHostKeyChecking accept-new
  UserKnownHostsFile ~/.ssh/known_hosts
```

### 3. 设置正确的文件权限

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
```

### 4. 首次连接并接受主机密钥

第一次连接时，需要手动接受主机密钥：

```bash
ssh agent.tomo-ai.cn
```

按提示输入：
1. 跳板机的 OTP（一次性密码）
2. 目标服务器的 root 密码

## 配置说明

### 关键配置项解释

| 配置项 | 说明 |
|--------|------|
| `Host bastion` | 定义跳板机的别名，可以用 `ssh bastion` 直接连接跳板机 |
| `ProxyJump bastion` | 通过跳板机连接目标服务器 |
| `ControlMaster auto` | 启用连接复用，自动复用已建立的连接 |
| `ControlPersist 10m` | 连接保持 10 分钟，期间复用连接无需重新认证 |
| `ServerAliveInterval 60` | 每 60 秒发送心跳包，保持连接活跃 |
| `StrictHostKeyChecking accept-new` | 自动接受新的主机密钥，已确认的密钥不再询问 |

### 连接复用机制

- **第一次连接**：需要输入 OTP 和密码
- **10 分钟内再次连接**：如果跳板机连接还在，会复用连接，可能只需要输入目标服务器密码
- **10 分钟后**：连接过期，需要重新认证

## 使用方法

### 基本使用

```bash
# 直接连接目标服务器（自动通过跳板机）
ssh agent.tomo-ai.cn

# 单独连接跳板机
ssh bastion
```

### 执行远程命令

```bash
# 在目标服务器上执行命令
ssh agent.tomo-ai.cn "ls -la"

# 复制文件到目标服务器
scp file.txt agent.tomo-ai.cn:/tmp/

# 从目标服务器复制文件
scp agent.tomo-ai.cn:/tmp/file.txt ./
```

## 高级配置：SSH 密钥认证（可选）

如果想完全跳过密码输入，可以配置 SSH 密钥认证。

### 步骤 1：检查是否已有密钥

```bash
ls -la ~/.ssh/id_*.pub
```

如果已有密钥（如 `id_ed25519.pub` 或 `id_rsa.pub`），可以跳过生成步骤。

### 步骤 2：生成 SSH 密钥（如果没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 或使用 RSA（兼容性更好）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### 步骤 3：复制公钥到跳板机

```bash
ssh-copy-id zhimeng.wang@l-rtools1.ops.cn1
```

### 步骤 4：复制公钥到目标服务器（通过跳板机）

```bash
# 方法1：使用 ssh-copy-id
ssh-copy-id -o ProxyJump=bastion root@agent.tomo-ai.cn

# 方法2：手动复制
cat ~/.ssh/id_ed25519.pub | ssh -o ProxyJump=bastion root@agent.tomo-ai.cn "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 步骤 5：在配置文件中启用密钥认证

编辑 `~/.ssh/config`，取消注释并指定密钥路径：

**修改前（被注释，不生效）：**
```ssh-config
# IdentityFile ~/.ssh/id_ed25519
```

**修改后（取消注释，生效）：**
```ssh-config
IdentityFile ~/.ssh/id_ed25519
```

**完整配置示例：**
```ssh-config
Host bastion
  HostName l-rtools1.ops.cn1
  User zhimeng.wang
  IdentityFile ~/.ssh/id_ed25519  # 取消注释，指定密钥路径
  # ... 其他配置

Host agent.tomo-ai.cn
  HostName agent.tomo-ai.cn
  User root
  ProxyJump bastion
  IdentityFile ~/.ssh/id_ed25519  # 取消注释，指定密钥路径
  # ... 其他配置
```

### 步骤 6：测试密钥认证

```bash
# 测试跳板机密钥认证
ssh bastion

# 测试目标服务器密钥认证
ssh agent.tomo-ai.cn
```

如果配置成功，应该可以直接登录，无需输入密码。

## 常见问题

### 1. 主机密钥验证失败

**问题**：`Host key verification failed`

**解决**：
- 首次连接时输入 `yes` 接受主机密钥
- 或使用 `ssh-keyscan` 手动添加：
  ```bash
  ssh-keyscan l-rtools1.ops.cn1 >> ~/.ssh/known_hosts
  ```

### 2. 连接超时

**问题**：连接经常断开

**解决**：
- 检查 `ServerAliveInterval` 和 `ServerAliveCountMax` 配置
- 增加 `ControlPersist` 的时间（如改为 `30m`）

### 3. ProxyJump 不支持

**问题**：SSH 版本较老，不支持 `ProxyJump`

**解决**：使用 `ProxyCommand` 替代：
```ssh-config
ProxyCommand ssh -W %h:%p bastion
```

### 4. 密钥认证不工作

**问题**：配置了密钥但仍然需要密码

**检查**：
1. 确认公钥已正确复制到服务器的 `~/.ssh/authorized_keys`
2. 确认服务器上的权限正确：
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```
3. 检查 SSH 配置文件中的 `IdentityFile` 路径是否正确
4. 查看 SSH 详细日志：
   ```bash
   ssh -v agent.tomo-ai.cn
   ```

## 配置文件完整示例

```ssh-config
Host gitlab.corp.qunar.com
  HostkeyAlgorithms +ssh-rsa
  PubkeyAcceptedAlgorithms +ssh-rsa

# 跳板机配置
Host bastion
  HostName l-rtools1.ops.cn1
  User zhimeng.wang
  # 如果使用密钥认证，取消下面的注释并指定密钥路径
  # IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60
  ServerAliveCountMax 3
  PreferredAuthentications keyboard-interactive,password
  ForwardAgent yes
  ControlMaster auto
  ControlPath ~/.ssh/control-%r@%h:%p
  ControlPersist 10m
  StrictHostKeyChecking accept-new
  UserKnownHostsFile ~/.ssh/known_hosts

# 目标服务器配置（通过跳板机）
Host agent.tomo-ai.cn
  HostName agent.tomo-ai.cn
  User root
  ProxyJump bastion
  # 如果使用密钥认证，取消下面的注释并指定密钥路径
  # IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60
  ServerAliveCountMax 3
  PreferredAuthentications keyboard-interactive,password
  StrictHostKeyChecking accept-new
  UserKnownHostsFile ~/.ssh/known_hosts
```

## 总结

通过以上配置，你可以：
- ✅ 使用 `ssh agent.tomo-ai.cn` 直接连接，自动通过跳板机
- ✅ 连接复用，减少重复认证
- ✅ 自动接受已确认的主机密钥
- ✅ （可选）配置密钥认证，完全跳过密码输入

配置完成后，日常使用只需要运行 `ssh agent.tomo-ai.cn` 即可！

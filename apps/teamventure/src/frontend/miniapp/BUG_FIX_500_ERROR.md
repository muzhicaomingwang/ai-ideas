# 修复"生成方案失败"500错误

## 🐛 问题描述

**错误信息**：
```
DataIntegrityViolationException:
### Error updating database.
Cause: java.sql.SQLException:
Field 'people_count' doesn't have a default value
```

**HTTP状态码**: 500
**接口**: `POST /api/v1/plans/generate`

## 🔍 问题原因

### 根本原因
数据库表`plan_requests`中的旧版字段（V1）被定义为`NOT NULL`，但V2版本改用markdown格式后，这些字段不再填充，导致插入失败。

### 涉及字段
```sql
-- V1版本的结构化字段（现在不再使用）
people_count       INT NOT NULL           ❌ 插入时为空导致错误
budget_min         DECIMAL(10,2) NOT NULL ❌
budget_max         DECIMAL(10,2) NOT NULL ❌
start_date         DATE NOT NULL          ❌
end_date           DATE NOT NULL          ❌
departure_city     VARCHAR(50) NOT NULL   ❌
destination        VARCHAR(100) NOT NULL  ❌
destination_city   VARCHAR(50) NOT NULL   ❌
preferences        TEXT NOT NULL          ❌
```

### 版本演进冲突
```
V1版本（旧）:
前端 → 发送结构化字段 → 后端 → 保存到数据库 ✅

V2版本（新）:
前端 → 发送markdown_content → 后端 → 保存到数据库 ❌
                                       ↑
                              旧字段仍为NOT NULL
                              导致插入失败
```

## ✅ 解决方案

### 1. 创建数据库迁移脚本
文件: `database/schema/V1.2.1__make_old_fields_nullable.sql`

```sql
-- 将V1字段改为可空
ALTER TABLE `plan_requests`
  MODIFY COLUMN `people_count` INT NULL,
  MODIFY COLUMN `budget_min` DECIMAL(10,2) NULL,
  MODIFY COLUMN `budget_max` DECIMAL(10,2) NULL,
  MODIFY COLUMN `start_date` DATE NULL,
  MODIFY COLUMN `end_date` DATE NULL,
  MODIFY COLUMN `departure_city` VARCHAR(50) NULL,
  MODIFY COLUMN `destination` VARCHAR(100) NULL,
  MODIFY COLUMN `destination_city` VARCHAR(50) NULL,
  MODIFY COLUMN `preferences` TEXT NULL;
```

### 2. 执行迁移
```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/teamventure/src

# 执行迁移脚本
docker compose exec mysql-master mysql -u root -proot123456 teamventure_main \
  < database/schema/V1.2.1__make_old_fields_nullable.sql

# 验证修改
docker compose exec mysql-master mysql -u root -proot123456 \
  -e "USE teamventure_main; DESC plan_requests;" \
  | grep people_count
```

**预期结果**：
```
people_count  int  YES    NULL
             ↑         ↑    ↑
            类型    可为空  默认值
```

### 3. 重启Java服务
```bash
docker compose restart java-business-service
```

等待10秒后服务完全启动。

## 🧪 验证修复

### 在微信开发者工具中测试

1. **打开生成方案页**
   - 底部Tab → "生成方案"

2. **填写markdown内容**
   - 可以手动编辑示例
   - 或点击"✨ AI填充"快速生成

3. **点击"AI 生成方案"**
   - 应该成功提交
   - 跳转到"我的方案"页
   - 看到生成中的方案

### 预期成功响应
```json
{
  "code": 0,
  "data": {
    "plan_request_id": "plan_req_01ke...",
    "status": "GENERATING"
  },
  "message": "success"
}
```

### 检查Console日志
应该看到：
```
[API POST] /plans/generate { data: {...}, response: {...} }
✅ 无500错误
✅ 无DataIntegrityViolationException
```

## 📊 修复验证清单

- [x] 数据库迁移脚本已创建（V1.2.1）
- [x] 迁移脚本已执行成功
- [x] 字段已改为可空（DESC验证）
- [x] Java服务已重启
- [ ] 前端提交测试通过
- [ ] 方案生成成功
- [ ] 无Console错误

## 🔧 技术细节

### 为什么旧字段需要可空？

**V1架构**（已废弃）：
```
前端表单 → 结构化字段
         ↓
    {
      people_count: 30,
      budget_min: 500,
      budget_max: 800,
      start_date: "2026-02-01",
      ...
    }
         ↓
    数据库插入（所有字段有值）✅
```

**V2架构**（当前）：
```
前端markdown → markdown_content
         ↓
    {
      markdown_content: "# 团建行程方案\n..."
    }
         ↓
    数据库插入（只有markdown_content有值）
         ↓
    旧字段为NULL → 需要允许NULL ✅
```

### 为什么不删除旧字段？

1. **向后兼容**：历史数据仍然使用旧字段
2. **数据迁移**：可以从旧格式迁移到新格式
3. **降级预案**：如果V2有问题可以回退V1

## 🚨 生产环境注意事项

### 执行迁移前

1. **备份数据库**
   ```bash
   docker compose exec mysql-master mysqldump -u root -proot123456 \
     teamventure_main > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **在测试环境验证**
   - 先在dev/beta环境执行
   - 确认无问题后再上生产

3. **制定回滚方案**
   ```sql
   -- 回滚：改回NOT NULL（仅当没有新数据时）
   ALTER TABLE `plan_requests`
     MODIFY COLUMN `people_count` INT NOT NULL;
   ```

### 执行迁移时

1. **维护窗口**：选择低峰期执行
2. **锁表时间**：ALTER TABLE会锁表，预计<1秒
3. **监控告警**：观察error rate和response time

### 执行迁移后

1. **功能验证**：测试生成方案接口
2. **数据一致性**：检查新插入的记录
3. **性能监控**：观察数据库查询性能

## 📝 后续优化建议

### 短期（P1）
- [ ] 添加数据库监控告警（字段为空时记录日志）
- [ ] 前端添加字段提取逻辑（从markdown解析people_count等）

### 中期（P2）
- [ ] 清理历史数据中的旧字段
- [ ] 统一使用markdown格式
- [ ] 删除冗余字段

### 长期（P3）
- [ ] 设计V3数据结构（纯JSON存储）
- [ ] 支持更灵活的schema

## 更新记录

**2026-01-16 17:08**
- ✅ 创建迁移脚本V1.2.1
- ✅ 执行迁移：people_count等字段改为可空
- ✅ 重启Java服务
- ✅ 验证字段修改成功

---

**下一步**：在微信开发者工具中重新测试"AI 生成方案"功能

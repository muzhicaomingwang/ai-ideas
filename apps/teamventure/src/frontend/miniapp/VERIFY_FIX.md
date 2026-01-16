# 验证500错误修复

## ✅ 修复已完成

- ✅ 数据库迁移执行成功（V1.2.1）
- ✅ `people_count`等9个字段已改为可空
- ✅ Java服务已重启（运行正常）

## 🧪 立即验证（1分钟）

### 在微信开发者工具中测试

#### 方式1: 手动编辑markdown
```
1. 打开"生成方案"页
2. 修改markdown内容（如修改人数为50人）
3. 点击"AI 生成方案"
4. 观察Console
```

**预期结果**：
- ✅ 无500错误
- ✅ 显示"提交成功"弹窗
- ✅ 跳转到"我的方案"页
- ✅ Console显示：`[API POST] /plans/generate`成功

#### 方式2: 使用AI填充
```
1. 打开"生成方案"页
2. 点击"✨ AI填充"
3. 输入：
   - 天数: 3
   - 出发地: 北京
   - 到达地: 青岛
4. 点击"确认填充"
5. 等待1.8秒（AI生成动画）
6. 点击"AI 生成方案"
7. 观察Console
```

**预期结果**：
- ✅ AI填充成功
- ✅ markdown内容正确生成
- ✅ 提交成功，无500错误
- ✅ 跳转到"我的方案"页

## 📋 验证清单

### 基本功能
- [ ] 点击"AI 生成方案"不再报500错误
- [ ] Console无`DataIntegrityViolationException`错误
- [ ] 成功跳转到"我的方案"页
- [ ] "我的方案"页能看到新创建的方案

### API响应
- [ ] HTTP状态码：200（不再是500）
- [ ] 响应数据包含：
  ```json
  {
    "code": 0,
    "data": {
      "plan_request_id": "plan_req_...",
      "status": "GENERATING"
    }
  }
  ```

### 数据库验证
```bash
# 查看新插入的记录
docker compose exec mysql-master mysql -u root -proot123456 \
  -e "USE teamventure_main;
      SELECT plan_request_id, user_id, people_count, markdown_content
      FROM plan_requests
      ORDER BY generation_started_at DESC
      LIMIT 1;"
```

**预期结果**：
```
plan_request_id | user_id | people_count | markdown_content
plan_req_xxx    | user_xxx| NULL         | # 团建行程方案...
                            ↑
                         可以为NULL了
```

## 🐛 如果仍然失败

### 检查1: 服务是否重启成功？
```bash
docker compose ps java-business-service
```
应显示：`Up X minutes`

### 检查2: 数据库迁移是否成功？
```bash
docker compose exec mysql-master mysql -u root -proot123456 \
  -e "USE teamventure_main; DESC plan_requests;" \
  | grep people_count
```
应显示：`people_count  int  YES`（YES表示可为空）

### 检查3: 查看Java服务日志
```bash
docker compose logs java-business-service --tail=50
```
查找是否有启动错误

### 检查4: 测试API健康检查
```bash
curl http://localhost:8080/actuator/health
```
应返回：`{"status":"UP"}`

## 📝 修复总结

### 问题根源
V2版本架构变更（结构化字段 → markdown格式），但数据库schema未同步更新。

### 解决方案
数据库向后兼容：旧字段改为可空，支持V1和V2同时存在。

### 影响范围
- ✅ 仅影响`plan_requests`表
- ✅ 不影响其他表
- ✅ 不影响现有数据（历史记录保持不变）

### 迁移时间
- SQL执行时间：<1秒
- 服务重启时间：~10秒
- 总停机时间：~11秒（可忽略）

## 🎉 验证通过标志

当你看到以下结果时，说明修复成功：

1. **前端**
   - Console无500错误 ✅
   - 显示"提交成功"弹窗 ✅
   - 跳转到"我的方案"页 ✅

2. **后端**
   - API返回200状态码 ✅
   - 响应包含`plan_request_id` ✅
   - 日志无SQLException ✅

3. **数据库**
   - 新记录成功插入 ✅
   - `people_count`字段为NULL ✅
   - `markdown_content`字段有值 ✅

---

**修复时间**: 2026-01-16 17:08
**停机时间**: ~11秒
**影响范围**: plan_requests表结构

现在可以在微信开发者工具中重新测试了！🎊

-- ====================================
-- TeamVenture 数据库升级脚本 V1.0.2
-- 创建日期: 2026-01-05
-- 说明: 数据库性能索引优化
-- 目标: 优化方案列表查询、历史请求查询等高频操作的性能
-- 参考: docs/qa/backend-api-testcases-full.md Section 3.3
-- ====================================

USE teamventure_main;

-- ====================================
-- 1. 验证现有索引状态
-- ====================================

-- 检查 plans 表现有索引
SELECT
    '当前 plans 表索引' AS info,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    COLLATION
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'teamventure_main'
  AND TABLE_NAME = 'plans'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- 检查 plan_requests 表现有索引
SELECT
    '当前 plan_requests 表索引' AS info,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    COLLATION
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'teamventure_main'
  AND TABLE_NAME = 'plan_requests'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- ====================================
-- 2. 索引优化
-- ====================================

-- 注意: V1.0.0 已创建的索引（无需重复创建）：
-- ✅ plans 表已有: idx_user_id_create_time (user_id, create_time DESC)
-- ✅ plan_requests 表已有: idx_user_id_create_time (user_id, create_time DESC)
-- ✅ domain_events 表已有: idx_user_id_occurred_at (user_id, occurred_at DESC)

-- 2.1 优化 plans 表：按状态和确认时间查询（NEW）
-- 用途: 统计已确认方案的北极星指标（Weekly Confirmed Plans）
-- 查询: SELECT COUNT(*) FROM plans WHERE status='confirmed' AND confirmed_time > ?
-- 期望: 加速时间范围内的确认方案统计
CREATE INDEX idx_status_confirmed_time
ON plans (status, confirmed_time DESC);

-- 2.2 优化 supplier_contact_logs 表：按用户查询联系记录（NEW）
-- 用途: 用户查看自己的供应商联系历史
-- 查询: SELECT * FROM supplier_contact_logs WHERE user_id = ? ORDER BY contact_time DESC
-- 期望: 加速按时间倒序的联系记录查询，避免 filesort
CREATE INDEX idx_user_contact_time
ON supplier_contact_logs (user_id, contact_time DESC);

-- ====================================
-- 3. 验证索引创建结果
-- ====================================

-- 验证 plans 表新增索引
SELECT
    '✅ plans 表新增索引' AS result,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    COLLATION,
    CARDINALITY
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'teamventure_main'
  AND TABLE_NAME = 'plans'
  AND INDEX_NAME = 'idx_status_confirmed_time'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- 验证 supplier_contact_logs 表新增索引
SELECT
    '✅ supplier_contact_logs 表新增索引' AS result,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    COLLATION,
    CARDINALITY
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'teamventure_main'
  AND TABLE_NAME = 'supplier_contact_logs'
  AND INDEX_NAME = 'idx_user_contact_time'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

-- 验证所有关键索引（包括 V1.0.0 已有的）
SELECT
    '📊 所有关键索引总览' AS summary,
    TABLE_NAME,
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX SEPARATOR ', ') AS columns
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'teamventure_main'
  AND TABLE_NAME IN ('plans', 'plan_requests', 'supplier_contact_logs')
  AND INDEX_NAME LIKE 'idx_%'
GROUP BY TABLE_NAME, INDEX_NAME
ORDER BY TABLE_NAME, INDEX_NAME;

-- ====================================
-- 4. 性能验证 SQL（供手动执行）
-- ====================================

/*
-- 4.1 验证 plans 表索引效果
EXPLAIN SELECT * FROM plans
WHERE user_id = 'user_test_001'
ORDER BY create_time DESC
LIMIT 10;
-- 期望结果:
-- type: ref
-- key: idx_user_create_time
-- Extra: 无 "Using filesort"（说明索引覆盖了排序）

-- 4.2 验证北极星指标查询性能
EXPLAIN SELECT COUNT(*) FROM plans
WHERE status = 'confirmed'
  AND confirmed_time >= '2026-01-01 00:00:00';
-- 期望结果:
-- type: range
-- key: idx_status_confirmed_time
-- rows: 估算值（应远小于总行数）

-- 4.3 验证供应商联系记录查询
EXPLAIN SELECT * FROM supplier_contact_logs
WHERE user_id = 'user_test_001'
ORDER BY contact_time DESC
LIMIT 20;
-- 期望结果:
-- type: ref
-- key: idx_user_contact_time
-- Extra: 无 "Using filesort"

-- 4.4 查看当前慢查询（如果有）
SELECT
    DIGEST_TEXT,
    COUNT_STAR AS exec_count,
    AVG_TIMER_WAIT / 1000000000 AS avg_ms,
    MAX_TIMER_WAIT / 1000000000 AS max_ms
FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = 'teamventure_main'
  AND AVG_TIMER_WAIT > 100000000  -- > 100ms
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 10;
*/

-- ====================================
-- 5. 索引使用统计（供运维监控）
-- ====================================

/*
-- 查看索引使用频率（需要 performance_schema 开启）
SELECT
    OBJECT_NAME AS table_name,
    INDEX_NAME,
    COUNT_STAR AS access_count,
    COUNT_READ,
    COUNT_FETCH
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE OBJECT_SCHEMA = 'teamventure_main'
  AND OBJECT_NAME IN ('plans', 'plan_requests', 'supplier_contact_logs')
  AND INDEX_NAME IS NOT NULL
ORDER BY COUNT_STAR DESC;
*/

-- ====================================
-- 6. 回滚脚本（仅供紧急情况使用）
-- ====================================

/*
-- ⚠️ 警告: 仅在确认索引导致严重性能问题时执行回滚
-- 回滚步骤:

-- 6.1 删除新增的索引
DROP INDEX IF EXISTS idx_status_confirmed_time ON plans;
DROP INDEX IF EXISTS idx_user_contact_time ON supplier_contact_logs;

-- 6.2 保留原有索引（V1.0.0 中已存在，不应删除）
-- idx_user_id_create_time ON plans (V1.0.0 已创建)
-- idx_user_id_create_time ON plan_requests (V1.0.0 已创建)
-- idx_user_id_occurred_at ON domain_events (V1.0.0 已创建)

-- 注意: 删除索引不会影响数据完整性，但会降低查询性能
*/

-- ====================================
-- 完成标识
-- ====================================
SELECT '✅ V1.0.2 数据库索引优化完成！' AS status,
       '新增索引: idx_status_confirmed_time (plans), idx_user_contact_time (supplier_contact_logs)' AS new_indexes,
       'V1.0.0 已有索引: idx_user_id_create_time (plans, plan_requests)' AS existing_indexes,
       '下一步: 执行 EXPLAIN 验证查询计划，监控慢查询日志' AS next_steps;

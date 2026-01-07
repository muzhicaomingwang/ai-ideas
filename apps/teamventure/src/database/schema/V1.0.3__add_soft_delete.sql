-- =====================================================
-- V1.0.3: 添加软删除支持
-- 创建日期: 2026-01-05
-- 说明: 为 plans 和 plan_requests 表添加软删除字段
-- =====================================================

USE teamventure_main;

-- =====================================================
-- 1. plans 表添加软删除字段
-- =====================================================
ALTER TABLE plans
ADD COLUMN deleted_at TIMESTAMP NULL COMMENT '删除时间（软删除）' AFTER update_time;

-- 添加索引：支持按用户查询未删除的方案
CREATE INDEX idx_plans_user_deleted ON plans (user_id, deleted_at);

-- =====================================================
-- 2. plan_requests 表添加软删除字段
-- =====================================================
ALTER TABLE plan_requests
ADD COLUMN deleted_at TIMESTAMP NULL COMMENT '删除时间（软删除）' AFTER error_message;

-- 添加索引：支持按用户查询未删除的请求
CREATE INDEX idx_plan_requests_user_deleted ON plan_requests (user_id, deleted_at);

-- =====================================================
-- 验证
-- =====================================================
SELECT
    'plans.deleted_at' AS field_name,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS null_count
FROM plans
UNION ALL
SELECT
    'plan_requests.deleted_at',
    COUNT(*),
    SUM(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END)
FROM plan_requests;

-- =====================================================
-- 回滚脚本（如需要）
-- =====================================================
/*
ALTER TABLE plans DROP INDEX idx_plans_user_deleted;
ALTER TABLE plans DROP COLUMN deleted_at;

ALTER TABLE plan_requests DROP INDEX idx_plan_requests_user_deleted;
ALTER TABLE plan_requests DROP COLUMN deleted_at;
*/

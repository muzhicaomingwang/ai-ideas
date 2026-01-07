-- =====================================================
-- V1.0.4: 添加归档支持
-- 创建日期: 2026-01-05
-- 说明: 为 plans 表添加归档字段
-- =====================================================

USE teamventure_main;

-- 添加归档时间字段
ALTER TABLE plans
ADD COLUMN archived_at TIMESTAMP NULL COMMENT '归档时间' AFTER deleted_at;

-- 添加索引：支持按用户查询未归档的方案
CREATE INDEX idx_plans_user_archived ON plans (user_id, archived_at);

-- =====================================================
-- 验证
-- =====================================================
SELECT 
    'plans.archived_at added' AS status,
    COUNT(*) AS total_rows
FROM plans;

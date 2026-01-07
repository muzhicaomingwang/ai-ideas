-- =====================================================
-- V1.0.7: 添加通晒状态支持
--
-- 背景：新增 "通晒中" (reviewing) 状态
-- 状态机流转：draft → reviewing → confirmed → archived
--             confirmed 可回退到 reviewing
--
-- 本迁移添加 review_started_at 字段记录进入通晒状态的时间
-- =====================================================

-- 1. plans 表添加通晒开始时间字段
ALTER TABLE plans
    ADD COLUMN review_started_at TIMESTAMP NULL
        COMMENT '通晒开始时间（draft → reviewing 时设置）'
    AFTER archived_at;

-- 2. 添加索引支持按状态筛选
CREATE INDEX idx_plans_status ON plans (status);

-- =====================================================
-- 状态机说明（供开发参考）
-- =====================================================
--
-- | 状态       | 中文名     | 说明                              |
-- |-----------|-----------|----------------------------------|
-- | draft     | 制定完成   | AI生成完成，待用户提交通晒          |
-- | reviewing | 通晒中     | 候选方案在通晒中，可修改            |
-- | confirmed | 已确认     | 用户确认选用此方案                  |
-- | archived  | 已归档     | 方案已归档，不在主列表显示           |
--
-- 状态转换：
-- - draft → reviewing（提交通晒）
-- - reviewing → confirmed（确认方案）
-- - confirmed → reviewing（回退通晒，重新修改）
-- - confirmed → archived（归档方案）
--
-- =====================================================

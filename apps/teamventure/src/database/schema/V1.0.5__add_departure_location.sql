-- =====================================================
-- V1.0.5: 添加目的地字段
-- 团建场景中，出发地到目的地的交通规划非常重要
-- 注意：departure_city 字段已存在，本次添加 destination 字段
-- =====================================================

-- 1. plan_requests 表添加目的地
ALTER TABLE plan_requests
ADD COLUMN destination VARCHAR(100) DEFAULT NULL COMMENT '目的地' AFTER departure_city;

-- 2. plans 表添加目的地
ALTER TABLE plans
ADD COLUMN destination VARCHAR(100) DEFAULT NULL COMMENT '目的地' AFTER departure_city;

-- 3. 为目的地添加索引（便于按目的地筛选）
CREATE INDEX idx_plan_requests_destination ON plan_requests(destination);
CREATE INDEX idx_plans_destination ON plans(destination);

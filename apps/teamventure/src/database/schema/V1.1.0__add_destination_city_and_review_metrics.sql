-- =====================================================
-- V1.1.0: 补充目的地城市与通晒反馈指标
--
-- 领域语言（UL）增强：
-- - destination: 目的地（团建活动举办地点，如：杭州千岛湖）
-- - destination_city: 目的地所属行政城市（如：杭州）
-- - review_count / average_score: 通晒后的反馈收集
-- =====================================================

-- 1) plan_requests: 添加目的地城市
ALTER TABLE plan_requests
    ADD COLUMN destination_city VARCHAR(50) DEFAULT NULL
        COMMENT '目的地所属行政城市（如：杭州）'
    AFTER destination;

CREATE INDEX idx_plan_requests_destination_city ON plan_requests(destination_city);

-- 2) plans: 添加目的地城市 + 通晒反馈指标
ALTER TABLE plans
    ADD COLUMN destination_city VARCHAR(50) DEFAULT NULL
        COMMENT '目的地所属行政城市（如：杭州）'
    AFTER destination;

CREATE INDEX idx_plans_destination_city ON plans(destination_city);

ALTER TABLE plans
    ADD COLUMN review_count INT NOT NULL DEFAULT 0
        COMMENT '通晒评价数'
    AFTER review_started_at,
    ADD COLUMN average_score DECIMAL(3,2) DEFAULT NULL
        COMMENT '通晒平均分（0-5，可为空）'
    AFTER review_count;


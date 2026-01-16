-- V1.2.1: 将plan_requests表的V1字段改为可空
-- 原因：V2版本使用markdown_content格式，旧的结构化字段不再必填

-- 修改plan_requests表，将V1字段改为NULL
ALTER TABLE `plan_requests`
  MODIFY COLUMN `people_count` INT NULL COMMENT '人数（V1字段，V2版本可为空）',
  MODIFY COLUMN `budget_min` DECIMAL(10,2) NULL COMMENT '最低预算（V1字段，V2版本可为空）',
  MODIFY COLUMN `budget_max` DECIMAL(10,2) NULL COMMENT '最高预算（V1字段，V2版本可为空）',
  MODIFY COLUMN `start_date` DATE NULL COMMENT '开始日期（V1字段，V2版本可为空）',
  MODIFY COLUMN `end_date` DATE NULL COMMENT '结束日期（V1字段，V2版本可为空）',
  MODIFY COLUMN `departure_city` VARCHAR(50) NULL COMMENT '出发城市（V1字段，V2版本可为空）',
  MODIFY COLUMN `destination` VARCHAR(100) NULL COMMENT '目的地（V1字段，V2版本可为空）',
  MODIFY COLUMN `destination_city` VARCHAR(50) NULL COMMENT '目的地城市（V1字段，V2版本可为空）',
  MODIFY COLUMN `preferences` TEXT NULL COMMENT '偏好JSON（V1字段，V2版本可为空）';

-- 确保markdown_content字段存在且可为空（如果V1.2.0已创建，此行会报错可忽略）
-- ALTER TABLE `plan_requests`
--   ADD COLUMN `markdown_content` TEXT NULL COMMENT 'Markdown格式的需求描述（V2新增）' AFTER `user_id`;

-- ====================================
-- TeamVenture 数据库升级脚本 V1.0.1
-- 创建日期: 2026-01-04
-- 说明: 扩展所有ID字段长度以支持 ULID 格式
-- 问题: ULID (26字符) + 前缀 (如 "plan_req_") = 35字符 > VARCHAR(32)
-- 解决: 将所有ID字段扩展为 VARCHAR(64)
-- ====================================

USE teamventure_main;

-- 扩展 plan_requests 表的ID字段
ALTER TABLE plan_requests MODIFY COLUMN plan_request_id VARCHAR(64) NOT NULL COMMENT '方案请求ID，前缀plan_req_';

-- 扩展 plans 表的ID字段
ALTER TABLE plans MODIFY COLUMN plan_id VARCHAR(64) NOT NULL COMMENT '方案ID，前缀plan_';
ALTER TABLE plans MODIFY COLUMN plan_request_id VARCHAR(64) NOT NULL COMMENT '关联的请求ID';
ALTER TABLE plans MODIFY COLUMN user_id VARCHAR(64) NOT NULL COMMENT '用户ID';
ALTER TABLE plans MODIFY COLUMN confirmed_by VARCHAR(64) NULL COMMENT '确认人（冗余user_id）';

-- 扩展 users 表的ID字段
ALTER TABLE users MODIFY COLUMN user_id VARCHAR(64) NOT NULL COMMENT '用户ID，前缀user_';

-- 扩展 sessions 表的ID字段
ALTER TABLE sessions MODIFY COLUMN session_id VARCHAR(64) NOT NULL COMMENT '会话ID，前缀sess_';
ALTER TABLE sessions MODIFY COLUMN user_id VARCHAR(64) NOT NULL COMMENT '用户ID';

-- 扩展 suppliers 表的ID字段
ALTER TABLE suppliers MODIFY COLUMN supplier_id VARCHAR(64) NOT NULL COMMENT '供应商ID，前缀sup_';

-- 扩展 supplier_contact_logs 表的ID字段
ALTER TABLE supplier_contact_logs MODIFY COLUMN contact_id VARCHAR(64) NOT NULL COMMENT '联系记录ID，前缀contact_';
ALTER TABLE supplier_contact_logs MODIFY COLUMN plan_id VARCHAR(64) NOT NULL COMMENT '方案ID';
ALTER TABLE supplier_contact_logs MODIFY COLUMN supplier_id VARCHAR(64) NOT NULL COMMENT '供应商ID';
ALTER TABLE supplier_contact_logs MODIFY COLUMN user_id VARCHAR(64) NOT NULL COMMENT '用户ID';

-- 扩展 domain_events 表的ID字段
ALTER TABLE domain_events MODIFY COLUMN event_id VARCHAR(64) NOT NULL COMMENT '事件ID，前缀evt_';
ALTER TABLE domain_events MODIFY COLUMN aggregate_id VARCHAR(64) NOT NULL COMMENT '聚合ID';
ALTER TABLE domain_events MODIFY COLUMN user_id VARCHAR(64) DEFAULT NULL COMMENT '触发用户ID';

SELECT '✅ ID字段长度扩展完成！所有ID字段已从 VARCHAR(32) 扩展为 VARCHAR(64)' AS status;

-- ====================================
-- TeamVenture 数据库初始化脚本 V1.0.0
-- 创建日期: 2025-12-30
-- 说明: 创建所有核心表结构
-- 执行方式: source /path/to/V1.0.0__init.sql
-- ====================================

USE teamventure_main;

-- ====================================
-- 1. users（用户表）
-- ====================================
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID，前缀user_',
  `wechat_openid` VARCHAR(64) NOT NULL COMMENT '微信OpenID',
  `wechat_unionid` VARCHAR(64) DEFAULT NULL COMMENT '微信UnionID（可选）',
  `nickname` VARCHAR(64) DEFAULT NULL COMMENT '昵称',
  `avatar_url` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号（可选）',
  `company` VARCHAR(100) DEFAULT NULL COMMENT '公司名称（可选）',
  `role` VARCHAR(20) DEFAULT 'HR' COMMENT '角色：HR/ADMIN',
  `status` VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE/DISABLED',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_wechat_openid` (`wechat_openid`),
  UNIQUE KEY `uk_wechat_unionid` (`wechat_unionid`),
  KEY `idx_phone` (`phone`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ====================================
-- 2. sessions（会话表）
-- ====================================
CREATE TABLE IF NOT EXISTS `sessions` (
  `session_id` VARCHAR(32) NOT NULL COMMENT '会话ID，前缀sess_',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `session_token` VARCHAR(128) NOT NULL COMMENT 'Session Token（JWT）',
  `expires_at` TIMESTAMP NOT NULL COMMENT '过期时间',
  `ip_address` VARCHAR(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` VARCHAR(255) DEFAULT NULL COMMENT 'User Agent',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`session_id`),
  UNIQUE KEY `uk_session_token` (`session_token`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表（主要用Redis，DB备份）';

-- ====================================
-- 3. plan_requests（方案请求表）
-- ====================================
CREATE TABLE IF NOT EXISTS `plan_requests` (
  `plan_request_id` VARCHAR(32) NOT NULL COMMENT '方案请求ID，前缀plan_req_',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `people_count` INT NOT NULL COMMENT '人数',
  `budget_min` DECIMAL(10,2) NOT NULL COMMENT '最低预算',
  `budget_max` DECIMAL(10,2) NOT NULL COMMENT '最高预算',
  `start_date` DATE NOT NULL COMMENT '开始日期',
  `end_date` DATE NOT NULL COMMENT '结束日期',
  `departure_city` VARCHAR(50) NOT NULL COMMENT '出发城市',
  `preferences` JSON NOT NULL COMMENT '偏好设置（活动类型/住宿/餐饮/特殊需求）',
  `status` VARCHAR(20) NOT NULL DEFAULT 'CREATING' COMMENT '状态：CREATING/GENERATING/COMPLETED/FAILED',
  `generation_started_at` TIMESTAMP NULL COMMENT '生成开始时间',
  `generation_completed_at` TIMESTAMP NULL COMMENT '生成完成时间',
  `generation_duration_ms` INT NULL COMMENT '生成耗时（毫秒）',
  `error_code` VARCHAR(50) NULL COMMENT '错误码（如果失败）',
  `error_message` TEXT NULL COMMENT '错误信息',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`plan_request_id`),
  KEY `idx_user_id_create_time` (`user_id`, `create_time` DESC),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='方案请求表';

-- ====================================
-- 4. plans（方案表）⭐核心表
-- ====================================
CREATE TABLE IF NOT EXISTS `plans` (
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID，前缀plan_',
  `plan_request_id` VARCHAR(32) NOT NULL COMMENT '关联的请求ID',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `plan_type` VARCHAR(20) NOT NULL COMMENT '方案类型：budget/standard/premium',
  `plan_name` VARCHAR(100) NOT NULL COMMENT '方案名称',
  `summary` VARCHAR(500) NOT NULL COMMENT '方案摘要',
  `highlights` JSON DEFAULT NULL COMMENT '亮点列表',

  -- 核心数据（JSON）
  `itinerary` JSON NOT NULL COMMENT '行程安排（按天）',
  `budget_breakdown` JSON NOT NULL COMMENT '预算明细（按类目）',
  `supplier_snapshots` JSON NOT NULL COMMENT '供应商快照（避免关联查询）',

  -- 汇总字段（冗余，便于查询）
  `budget_total` DECIMAL(10,2) NOT NULL COMMENT '总预算',
  `budget_per_person` DECIMAL(10,2) NOT NULL COMMENT '人均预算',
  `duration_days` INT NOT NULL COMMENT '天数',

  -- 状态与时间
  `status` VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/confirmed',
  `confirmed_time` TIMESTAMP NULL COMMENT '确认时间',
  `confirmed_by` VARCHAR(32) NULL COMMENT '确认人（冗余user_id）',

  -- 埋点与统计
  `view_count` INT NOT NULL DEFAULT 0 COMMENT '查看次数',
  `share_count` INT NOT NULL DEFAULT 0 COMMENT '分享次数',

  -- 时间戳
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`plan_id`),
  KEY `idx_plan_request_id` (`plan_request_id`),
  KEY `idx_user_id_create_time` (`user_id`, `create_time` DESC),
  KEY `idx_user_id_status` (`user_id`, `status`),
  KEY `idx_status_create_time` (`status`, `create_time` DESC),
  KEY `idx_plan_type` (`plan_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='方案表';

-- ====================================
-- 5. suppliers（供应商表）
-- ====================================
CREATE TABLE IF NOT EXISTS `suppliers` (
  `supplier_id` VARCHAR(32) NOT NULL COMMENT '供应商ID，前缀sup_',
  `name` VARCHAR(100) NOT NULL COMMENT '供应商名称',
  `category` VARCHAR(50) NOT NULL COMMENT '品类：accommodation/dining/activity/transportation',
  `city` VARCHAR(50) NOT NULL COMMENT '城市',
  `district` VARCHAR(50) DEFAULT NULL COMMENT '区县',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
  `coordinates` POINT NOT NULL COMMENT '经纬度坐标',

  -- 联系方式
  `contact_phone` VARCHAR(20) NOT NULL COMMENT '联系电话',
  `contact_wechat` VARCHAR(50) DEFAULT NULL COMMENT '微信号',
  `contact_email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
  `contact_person` VARCHAR(50) DEFAULT NULL COMMENT '联系人',

  -- 价格与评分
  `price_min` DECIMAL(10,2) DEFAULT NULL COMMENT '价格区间最低',
  `price_max` DECIMAL(10,2) DEFAULT NULL COMMENT '价格区间最高',
  `price_unit` VARCHAR(20) DEFAULT NULL COMMENT '价格单位：per_person/per_room/per_car',
  `rating` DECIMAL(3,2) DEFAULT 0.00 COMMENT '评分（0-5）',
  `review_count` INT DEFAULT 0 COMMENT '评价数量',

  -- 特性与标签
  `tags` JSON DEFAULT NULL COMMENT '标签列表',
  `features` JSON DEFAULT NULL COMMENT '特色功能',
  `capacity_min` INT DEFAULT NULL COMMENT '最小接待人数',
  `capacity_max` INT DEFAULT NULL COMMENT '最大接待人数',

  -- 状态
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active/inactive',
  `verified` TINYINT(1) DEFAULT 0 COMMENT '是否认证',

  -- 运营数据
  `matched_count` INT DEFAULT 0 COMMENT '被匹配次数（统计）',
  `contacted_count` INT DEFAULT 0 COMMENT '被联系次数（统计）',

  -- 时间戳
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`supplier_id`),
  KEY `idx_category_city` (`category`, `city`),
  KEY `idx_city_rating` (`city`, `rating` DESC),
  KEY `idx_status` (`status`),
  SPATIAL KEY `idx_coordinates` (`coordinates`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';

-- ====================================
-- 6. supplier_contact_logs（供应商联系记录表）
-- ====================================
CREATE TABLE IF NOT EXISTS `supplier_contact_logs` (
  `contact_id` VARCHAR(32) NOT NULL COMMENT '联系记录ID，前缀contact_',
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID',
  `supplier_id` VARCHAR(32) NOT NULL COMMENT '供应商ID',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `channel` VARCHAR(20) NOT NULL COMMENT '联系渠道：PHONE/WECHAT/EMAIL',
  `contact_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '联系时间',
  `notes` TEXT DEFAULT NULL COMMENT '备注（用户可选填）',

  PRIMARY KEY (`contact_id`),
  KEY `idx_plan_id` (`plan_id`),
  KEY `idx_supplier_id` (`supplier_id`),
  KEY `idx_user_id_contact_time` (`user_id`, `contact_time` DESC),
  KEY `idx_contact_time` (`contact_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商联系记录表';

-- ====================================
-- 7. domain_events（领域事件表）⭐核心表
-- ====================================
CREATE TABLE IF NOT EXISTS `domain_events` (
  `event_id` VARCHAR(32) NOT NULL COMMENT '事件ID，前缀evt_',
  `event_type` VARCHAR(50) NOT NULL COMMENT '事件类型（如PlanConfirmed）',
  `aggregate_type` VARCHAR(50) NOT NULL COMMENT '聚合类型（如Plan）',
  `aggregate_id` VARCHAR(32) NOT NULL COMMENT '聚合ID',
  `user_id` VARCHAR(32) DEFAULT NULL COMMENT '触发用户ID',
  `payload` JSON NOT NULL COMMENT '事件负载（完整数据）',
  `occurred_at` TIMESTAMP(6) NOT NULL COMMENT '发生时间（微秒精度）',
  `processed` TINYINT(1) DEFAULT 0 COMMENT '是否已处理（MQ发送）',
  `processed_at` TIMESTAMP NULL COMMENT '处理时间',

  PRIMARY KEY (`event_id`),
  KEY `idx_aggregate_id_occurred_at` (`aggregate_id`, `occurred_at` DESC),
  KEY `idx_event_type_occurred_at` (`event_type`, `occurred_at` DESC),
  KEY `idx_user_id_occurred_at` (`user_id`, `occurred_at` DESC),
  KEY `idx_processed` (`processed`, `occurred_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='领域事件表（Event Sourcing轻量版）';

-- ====================================
-- 初始数据插入
-- ====================================

-- 插入系统管理员用户
INSERT INTO users (user_id, wechat_openid, nickname, role, status)
VALUES ('user_admin_001', 'admin_openid_placeholder', '系统管理员', 'ADMIN', 'ACTIVE')
ON DUPLICATE KEY UPDATE update_time = CURRENT_TIMESTAMP;

-- ====================================
-- 初始化完成
-- ====================================
SELECT '✅ Database initialization completed successfully!' AS status;
SELECT CONCAT('Created ', COUNT(*), ' tables') AS summary
FROM information_schema.tables
WHERE table_schema = 'teamventure_main';

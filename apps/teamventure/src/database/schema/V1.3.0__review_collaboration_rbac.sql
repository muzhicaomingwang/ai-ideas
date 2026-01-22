-- =====================================================
-- V1.3.0: 通晒协作（成员/收藏/申请/行程版本/建议）
--
-- 目标：
-- 1) 引入方案范围内的资源级RBAC事实表：plan_memberships
-- 2) 引入行程版本快照：plan_itinerary_revisions（收藏者不可见）
-- 3) 引入按版本的行程建议：plan_itinerary_suggestions（收藏者不可见）
-- 4) 为历史plans回填OWNER成员关系与当前行程版本快照（最小可用）
-- =====================================================

USE teamventure_main;

-- 1) plan_memberships
CREATE TABLE IF NOT EXISTS `plan_memberships` (
  `membership_id` VARCHAR(32) NOT NULL COMMENT '成员关系ID，前缀pm_',
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',

  `role` VARCHAR(20) NOT NULL COMMENT '角色：OWNER/PARTICIPANT/WATCHER',
  `status` VARCHAR(20) NOT NULL COMMENT '状态：ACTIVE/PENDING/REJECTED/REMOVED（一期主要用ACTIVE/PENDING）',

  `apply_reason` VARCHAR(255) DEFAULT NULL COMMENT '申请理由',
  `last_decision` VARCHAR(20) DEFAULT NULL COMMENT '最近一次审批结果：APPROVED/REJECTED（可空）',
  `decided_by` VARCHAR(32) DEFAULT NULL COMMENT '审批人user_id',
  `decided_at` TIMESTAMP NULL COMMENT '审批时间',

  `removed_by` VARCHAR(32) DEFAULT NULL COMMENT '踢人操作者user_id',
  `removed_at` TIMESTAMP NULL COMMENT '踢人时间（踢人后降级为WATCHER/ACTIVE）',

  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`membership_id`),
  UNIQUE KEY `uk_plan_user` (`plan_id`, `user_id`),
  KEY `idx_plan_status` (`plan_id`, `status`),
  KEY `idx_user_role_status` (`user_id`, `role`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='方案协作成员关系表';

-- 2) plan_itinerary_revisions
CREATE TABLE IF NOT EXISTS `plan_itinerary_revisions` (
  `revision_id` VARCHAR(32) NOT NULL COMMENT '版本快照ID，前缀rev_',
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID',
  `version` INT NOT NULL COMMENT '行程版本号（与plans.itinerary_version对齐）',
  `itinerary` JSON NOT NULL COMMENT '行程内容快照',
  `created_by` VARCHAR(32) NOT NULL COMMENT '创建人user_id',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

  PRIMARY KEY (`revision_id`),
  UNIQUE KEY `uk_plan_version` (`plan_id`, `version`),
  KEY `idx_plan_create_time` (`plan_id`, `create_time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行程版本快照表';

-- 3) plan_itinerary_suggestions
CREATE TABLE IF NOT EXISTS `plan_itinerary_suggestions` (
  `suggestion_id` VARCHAR(32) NOT NULL COMMENT '建议ID，前缀sug_',
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID',
  `target_version` INT NOT NULL COMMENT '建议对应的行程版本号',
  `user_id` VARCHAR(32) NOT NULL COMMENT '建议提出者user_id',
  `content` TEXT NOT NULL COMMENT '建议内容',
  `status` VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT '状态：OPEN/RESOLVED/REJECTED（可选）',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`suggestion_id`),
  KEY `idx_plan_version_time` (`plan_id`, `target_version`, `create_time` DESC),
  KEY `idx_user_time` (`user_id`, `create_time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行程建议表（按版本）';

-- 4) backfill OWNER membership for existing plans (idempotent)
INSERT IGNORE INTO plan_memberships (
  membership_id,
  plan_id,
  user_id,
  role,
  status,
  create_time,
  update_time
)
SELECT
  CONCAT('pm_', SUBSTRING(REPLACE(UUID(), '-', ''), 1, 26)) AS membership_id,
  p.plan_id,
  p.user_id,
  'OWNER' AS role,
  'ACTIVE' AS status,
  COALESCE(p.create_time, CURRENT_TIMESTAMP) AS create_time,
  COALESCE(p.update_time, CURRENT_TIMESTAMP) AS update_time
FROM plans p
WHERE p.plan_id IS NOT NULL
  AND p.user_id IS NOT NULL;

-- 5) backfill current itinerary revision for existing plans (idempotent)
INSERT IGNORE INTO plan_itinerary_revisions (
  revision_id,
  plan_id,
  version,
  itinerary,
  created_by,
  create_time
)
SELECT
  CONCAT('rev_', SUBSTRING(REPLACE(UUID(), '-', ''), 1, 26)) AS revision_id,
  p.plan_id,
  COALESCE(p.itinerary_version, 1) AS version,
  p.itinerary,
  p.user_id AS created_by,
  COALESCE(p.update_time, CURRENT_TIMESTAMP) AS create_time
FROM plans p
WHERE p.plan_id IS NOT NULL
  AND p.user_id IS NOT NULL
  AND p.itinerary IS NOT NULL;


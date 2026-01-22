# TeamVenture 一期 数据库详细设计

> **版本**: v1.1
> **数据库**: MySQL 8.0+
> **字符集**: utf8mb4
> **引擎**: InnoDB
> **时区**: Asia/Shanghai
>
> **v1.1补充**: 通晒协作（成员/收藏/申请/行程版本/建议）相关表结构

---

## 目录

1. [数据库架构](#1-数据库架构)
2. [表结构设计](#2-表结构设计)
3. [索引设计](#3-索引设计)
4. [分表策略](#4-分表策略)
5. [初始化脚本](#5-初始化脚本)

---

## 1. 数据库架构

### 1.1 主从复制架构

```
Master (3306)  ─────────> Slave (3307)
   │                          │
   │ Binlog同步               │
   ├─ INSERT                  ├─ SELECT (只读)
   ├─ UPDATE                  ├─ 方案列表查询
   ├─ DELETE                  ├─ 方案详情查询
   └─ domain_events 实时查询  └─ 供应商查询
```

### 1.2 读写分离规则

| 操作类型 | 数据库 | 说明 |
|---------|--------|------|
| INSERT/UPDATE/DELETE | Master | 所有写操作 |
| SELECT - 实时数据 | Master | domain_events等需要最新数据 |
| SELECT - 历史数据 | Slave | 方案列表、供应商列表等 |

### 1.3 数据库列表

```sql
-- 主业务库
CREATE DATABASE teamventure_main
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE teamventure_main;
```

---

## 2. 表结构设计

### 2.1 users（用户表）

```sql
CREATE TABLE `users` (
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
```

**字段说明**:
- `user_id`: ULID格式，全局唯一，前缀`user_`
- `wechat_openid`: 微信小程序唯一标识（必须）
- `wechat_unionid`: 微信开放平台UnionID（如果后续接入其他应用）
- `status`: 支持禁用用户

### 2.2 sessions（会话表）

```sql
CREATE TABLE `sessions` (
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
```

**说明**:
- 主要Session数据存Redis，DB作为备份和审计
- `expires_at`: 默认24小时过期
- 定期清理过期Session（cron job）

### 2.3 plan_requests（方案请求表）

```sql
CREATE TABLE `plan_requests` (
  `plan_request_id` VARCHAR(32) NOT NULL COMMENT '方案请求ID，前缀plan_req_',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `people_count` INT NOT NULL COMMENT '人数',
  `budget_min` DECIMAL(10,2) NOT NULL COMMENT '最低预算',
  `budget_max` DECIMAL(10,2) NOT NULL COMMENT '最高预算',
  `start_date` DATE NOT NULL COMMENT '开始日期',
  `end_date` DATE NOT NULL COMMENT '结束日期',
  `departure_city` VARCHAR(50) NOT NULL COMMENT '出发城市',
  `destination` VARCHAR(100) DEFAULT NULL COMMENT '目的地（团建活动举办地点）',
  `destination_city` VARCHAR(50) DEFAULT NULL COMMENT '目的地所属行政城市（如：杭州）',
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
```

**字段说明**:
- `preferences`: JSON格式存储复杂偏好
  ```json
  {
    "activity_types": ["team_building", "outdoor"],
    "accommodation_level": "standard",
    "dining_style": ["local"],
    "special_requirements": "无"
  }
  ```
- `status` 状态机:
  - CREATING: Java创建中
  - GENERATING: Python AI生成中
  - COMPLETED: 生成成功
  - FAILED: 生成失败

### 2.4 plans（方案表）⭐核心表

```sql
CREATE TABLE `plans` (
  `plan_id` VARCHAR(32) NOT NULL COMMENT '方案ID，前缀plan_',
  `plan_request_id` VARCHAR(32) NOT NULL COMMENT '关联的请求ID',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `plan_type` VARCHAR(20) NOT NULL COMMENT '方案类型：budget/standard/premium',
  `plan_name` VARCHAR(100) NOT NULL COMMENT '方案名称',
  `summary` VARCHAR(500) NOT NULL COMMENT '方案摘要',
  `highlights` JSON DEFAULT NULL COMMENT '亮点列表',

  -- 核心数据（JSONB）
  `itinerary` JSON NOT NULL COMMENT '行程安排（按天）',
  `budget_breakdown` JSON NOT NULL COMMENT '预算明细（按类目）',
  `supplier_snapshots` JSON NOT NULL COMMENT '供应商快照（避免关联查询）',

  -- 汇总字段（冗余，便于查询）
  `budget_total` DECIMAL(10,2) NOT NULL COMMENT '总预算',
  `budget_per_person` DECIMAL(10,2) NOT NULL COMMENT '人均预算',
  `duration_days` INT NOT NULL COMMENT '天数',
  `departure_city` VARCHAR(50) NOT NULL COMMENT '出发城市',
  `destination` VARCHAR(100) DEFAULT NULL COMMENT '目的地（团建活动举办地点）',
  `destination_city` VARCHAR(50) DEFAULT NULL COMMENT '目的地所属行政城市（如：杭州）',

  -- 状态与时间
  `status` VARCHAR(20) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/reviewing/confirmed/archived',
  `confirmed_time` TIMESTAMP NULL COMMENT '确认时间',
  `confirmed_by` VARCHAR(32) NULL COMMENT '确认人（冗余user_id）',
  `review_started_at` TIMESTAMP NULL COMMENT '通晒开始时间（draft → reviewing）',
  `review_count` INT NOT NULL DEFAULT 0 COMMENT '通晒评价数',
  `average_score` DECIMAL(3,2) DEFAULT NULL COMMENT '通晒平均分（0-5，可为空）',

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
```

**JSON字段结构示例**:

```json
// itinerary
{
  "days": [
    {
      "day_number": 1,
      "date": "2026-01-10",
      "activities": [
        {
          "time": "09:00",
          "activity": "集合出发",
          "location": "公司门口",
          "duration_minutes": 120,
          "supplier_id": "sup_transport_001"
        },
        {
          "time": "12:00",
          "activity": "午餐",
          "location": "怀柔农家乐",
          "supplier_id": "sup_dining_001"
        }
      ]
    },
    {
      "day_number": 2,
      "date": "2026-01-11",
      "activities": [...]
    }
  ]
}

// budget_breakdown
{
  "categories": [
    {
      "category": "交通",
      "items": [
        {"name": "大巴往返", "quantity": 1, "unit_price": 5000, "total": 5000, "supplier_id": "sup_transport_001"}
      ],
      "subtotal": 5000
    },
    {
      "category": "住宿",
      "items": [
        {"name": "标准间", "quantity": 25, "unit_price": 400, "total": 10000, "supplier_id": "sup_acc_001"}
      ],
      "subtotal": 10000
    },
    {
      "category": "餐饮",
      "items": [...],
      "subtotal": 8000
    },
    {
      "category": "活动",
      "items": [...],
      "subtotal": 10000
    },
    {
      "category": "其他",
      "items": [...],
      "subtotal": 2000
    }
  ],
  "total": 35000
}

// supplier_snapshots（快照，避免跨表查询）
[
  {
    "supplier_id": "sup_transport_001",
    "name": "北京旅游大巴公司",
    "category": "transportation",
    "contact": {
      "phone": "138****0001",
      "wechat": "bjbus001"
    },
    "price_range": {"min": 4000, "max": 6000},
    "rating": 4.5,
    "tags": ["专业车队", "保险齐全"],
    "snapshot_time": "2026-01-01T10:00:00Z"
  },
  {
    "supplier_id": "sup_acc_001",
    "name": "怀柔山水农家院",
    "category": "accommodation",
    ...
  }
]
```

### 2.5 suppliers（供应商表）

```sql
CREATE TABLE `suppliers` (
  `supplier_id` VARCHAR(32) NOT NULL COMMENT '供应商ID，前缀sup_',
  `name` VARCHAR(100) NOT NULL COMMENT '供应商名称',
  `category` VARCHAR(50) NOT NULL COMMENT '品类：accommodation/dining/activity/transportation',
  `city` VARCHAR(50) NOT NULL COMMENT '城市',
  `district` VARCHAR(50) DEFAULT NULL COMMENT '区县',
  `address` VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
  `coordinates` POINT DEFAULT NULL COMMENT '经纬度坐标',

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
```

**说明**:
- `coordinates`: 用于地理位置搜索（附近供应商）
- `tags`: JSON数组，如 `["山景", "团建专供", "包场"]`
- 一期为只读表，数据通过后台录入

### 2.6 supplier_contact_logs（供应商联系记录表）

```sql
CREATE TABLE `supplier_contact_logs` (
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
```

**说明**:
- 记录用户联系供应商的行为（用于转化漏斗分析）
- 支持节流：同一用户对同一供应商5分钟内只记录一次

### 2.7 domain_events（领域事件表）⭐核心表

```sql
CREATE TABLE `domain_events` (
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
```

**事件类型清单**:
| event_type | aggregate_type | 说明 |
|-----------|---------------|------|
| `WeChatLoginSucceeded` | User | 微信登录成功 |
| `PlanRequestCreated` | PlanRequest | 方案请求创建 |
| `PlanGenerationStarted` | PlanRequest | 生成开始 |
| `PlanGenerated` | Plan | 方案生成成功 |
| `PlanGenerationFailed` | PlanRequest | 生成失败 |
| `PlanViewed` | Plan | 方案被查看 |
| `PlanConfirmed` | Plan | 方案被确认 |
| `SupplierContacted` | SupplierContactLog | 供应商被联系 |

**payload 示例**:
```json
// PlanConfirmed事件
{
  "plan_id": "plan_01JH...",
  "user_id": "user_01JH...",
  "plan_type": "standard",
  "confirmed_at": "2026-01-01T15:30:00Z",
  "trace_id": "uuid"
}
```

---

### 2.8 plan_memberships（通晒成员/收藏/申请关系表）⭐协作核心表

```sql
CREATE TABLE `plan_memberships` (
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
```

**说明**:
- 一期约束：必须先收藏（WATCHER/ACTIVE）才允许申请参与（PARTICIPANT/PENDING）
- 踢人不做彻底移除：从`PARTICIPANT/ACTIVE`降级为`WATCHER/ACTIVE`，仍可查看当前行程

### 2.9 plan_itinerary_revisions（行程版本快照表）

```sql
CREATE TABLE `plan_itinerary_revisions` (
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
```

**说明**:
- 收藏者（WATCHER）只允许读取当前行程（plans.itinerary），不允许读取该表
- 参与者建议按版本绑定（见2.10）

### 2.10 plan_itinerary_suggestions（行程建议表）

```sql
CREATE TABLE `plan_itinerary_suggestions` (
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
```

## 3. 索引设计

### 3.1 查询场景与索引映射

| 查询场景 | SQL示例 | 使用索引 | 类型 |
|---------|---------|---------|------|
| 我的方案列表 | `SELECT * FROM plans WHERE user_id=? ORDER BY create_time DESC LIMIT 10` | `idx_user_id_create_time` | 复合索引 |
| 已确认方案列表 | `SELECT * FROM plans WHERE user_id=? AND status='confirmed' ORDER BY create_time DESC` | `idx_user_id_status` | 复合索引 |
| 方案详情 | `SELECT * FROM plans WHERE plan_id=?` | PRIMARY KEY | 主键 |
| 供应商搜索（城市+品类） | `SELECT * FROM suppliers WHERE city='北京' AND category='accommodation'` | `idx_category_city` | 复合索引 |
| 供应商评分排序 | `SELECT * FROM suppliers WHERE city='北京' ORDER BY rating DESC` | `idx_city_rating` | 复合索引 |
| 领域事件查询 | `SELECT * FROM domain_events WHERE aggregate_id=? ORDER BY occurred_at DESC` | `idx_aggregate_id_occurred_at` | 复合索引 |
| 未处理事件 | `SELECT * FROM domain_events WHERE processed=0 ORDER BY occurred_at` | `idx_processed` | 复合索引 |
| 通晒成员列表 | `SELECT * FROM plan_memberships WHERE plan_id=? AND status='ACTIVE'` | `idx_plan_status` | 复合索引 |
| 我的收藏列表 | `SELECT * FROM plan_memberships WHERE user_id=? AND role='WATCHER' AND status='ACTIVE'` | `idx_user_role_status` | 复合索引 |
| 行程历史版本 | `SELECT * FROM plan_itinerary_revisions WHERE plan_id=? ORDER BY create_time DESC` | `idx_plan_create_time` | 复合索引 |
| 行程建议列表 | `SELECT * FROM plan_itinerary_suggestions WHERE plan_id=? AND target_version=? ORDER BY create_time DESC` | `idx_plan_version_time` | 复合索引 |

### 3.2 索引优化建议

#### 避免全表扫描
```sql
-- ❌ 慢查询（全表扫描）
SELECT * FROM plans WHERE plan_name LIKE '%团建%';

-- ✅ 优化（使用覆盖索引）
SELECT plan_id, plan_name, status FROM plans
WHERE user_id = ? AND status = 'confirmed';
```

#### 复合索引顺序
```sql
-- 索引：idx_user_id_create_time (user_id, create_time)
-- ✅ 可以使用
WHERE user_id = ? ORDER BY create_time DESC

-- ✅ 可以使用（user_id部分）
WHERE user_id = ?

-- ❌ 无法使用（跳过user_id）
WHERE create_time > ?
```

---

## 4. 分表策略

### 4.1 分表规则

| 表名 | 分表 | 分表键 | 规则 | 保留期 |
|------|------|--------|------|--------|
| `plan_requests` | 是 | create_time | 按月分表 | 12个月 |
| `plans` | 是 | create_time | 按月分表 | 12个月 |
| `supplier_contact_logs` | 是 | contact_time | 按月分表 | 6个月 |
| `domain_events` | 是 | occurred_at | 按月分表 | 3个月（后归档） |
| `users` | 否 | - | - | 永久 |
| `sessions` | 否 | - | - | 自动清理过期 |
| `suppliers` | 否 | - | - | 永久 |

### 4.2 分表命名示例

```sql
-- 方案表按月分表
plans_202601  -- 2026年1月
plans_202602  -- 2026年2月
...

-- 领域事件表按月分表
domain_events_202601
domain_events_202602
...
```

### 4.3 分表实现方案

#### 方案A: 应用层路由（推荐一期）
```java
// Java代码中根据日期路由到不同表
public String getTableName(LocalDate date) {
    return "plans_" + date.format(DateTimeFormatter.ofPattern("yyyyMM"));
}

// MyBatis动态表名
@Select("SELECT * FROM ${tableName} WHERE user_id = #{userId}")
List<PlanPO> selectByUser(@Param("tableName") String tableName,
                           @Param("userId") String userId);
```

#### 方案B: 分区表（推荐二期）
```sql
-- 使用MySQL 8.0分区功能
CREATE TABLE plans (
  ...
) ENGINE=InnoDB
PARTITION BY RANGE (YEAR(create_time) * 100 + MONTH(create_time)) (
  PARTITION p202601 VALUES LESS THAN (202602),
  PARTITION p202602 VALUES LESS THAN (202603),
  ...
);
```

### 4.4 数据归档策略

```sql
-- 每月定时任务：归档3个月前的领域事件到OSS
-- 1. 导出到OSS
SELECT * FROM domain_events_202310
INTO OUTFILE '/tmp/domain_events_202310.csv';

-- 2. 删除原表
DROP TABLE domain_events_202310;

-- 3. 保留索引表（快速查询）
CREATE TABLE domain_events_archive (
  event_id VARCHAR(32),
  event_type VARCHAR(50),
  occurred_at TIMESTAMP,
  oss_path VARCHAR(255)  -- 指向OSS文件
);
```

---

## 5. 初始化脚本

### 5.1 V1.0.0__init.sql（建表脚本）

```sql
-- ====================================
-- TeamVenture 数据库初始化脚本 V1.0.0
-- 执行顺序：先创建数据库，再执行本脚本
-- ====================================

USE teamventure_main;

-- 1. 用户表
CREATE TABLE `users` ( ... );  -- 见2.1节完整DDL

-- 2. 会话表
CREATE TABLE `sessions` ( ... );  -- 见2.2节

-- 3. 方案请求表
CREATE TABLE `plan_requests` ( ... );  -- 见2.3节

-- 4. 方案表（一期不分表，二期再拆）
CREATE TABLE `plans` ( ... );  -- 见2.4节

-- 5. 供应商表
CREATE TABLE `suppliers` ( ... );  -- 见2.5节

-- 6. 供应商联系记录表
CREATE TABLE `supplier_contact_logs` ( ... );  -- 见2.6节

-- 7. 领域事件表
CREATE TABLE `domain_events` ( ... );  -- 见2.7节

-- 插入初始管理员用户
INSERT INTO users (user_id, wechat_openid, nickname, role, status)
VALUES ('user_admin_001', 'admin_openid', '系统管理员', 'ADMIN', 'ACTIVE');
```

### 5.2 V1.0.1__seed_suppliers.sql（供应商初始数据）

```sql
-- ====================================
-- 供应商初始数据（北京地区）
-- ====================================

USE teamventure_main;

-- 住宿类供应商
INSERT INTO suppliers (supplier_id, name, category, city, district,
                       contact_phone, price_min, price_max, price_unit,
                       rating, tags, capacity_min, capacity_max, status)
VALUES
('sup_acc_001', '怀柔山水农家院', 'accommodation', '北京', '怀柔区',
 '13800000001', 200, 500, 'per_room', 4.5,
 JSON_ARRAY('山景', '团建专供', '包场'), 20, 100, 'active'),

('sup_acc_002', '密云水库度假村', 'accommodation', '北京', '密云区',
 '13800000002', 300, 800, 'per_room', 4.8,
 JSON_ARRAY('水景', '会议室', 'KTV'), 30, 150, 'active'),

-- 餐饮类供应商
('sup_din_001', '怀柔特色农家菜', 'dining', '北京', '怀柔区',
 '13800000011', 50, 100, 'per_person', 4.3,
 JSON_ARRAY('农家菜', '烤全羊', '柴鸡蛋'), 20, 200, 'active'),

-- 活动类供应商
('sup_act_001', '怀柔拓展训练基地', 'activity', '北京', '怀柔区',
 '13800000021', 100, 300, 'per_person', 4.6,
 JSON_ARRAY('户外拓展', '真人CS', '定向越野'), 30, 500, 'active'),

-- 交通类供应商
('sup_tra_001', '北京旅游大巴公司', 'transportation', '北京', '朝阳区',
 '13800000031', 4000, 8000, 'per_car', 4.7,
 JSON_ARRAY('正规车队', '保险齐全', '经验丰富'), 30, 500, 'active');

-- TODO: 补充50+个供应商数据（由运营团队提供）
```

### 5.3 V1.0.2__add_performance_indexes.sql（性能优化索引）

```sql
-- ====================================
-- 性能优化索引（基于慢查询分析）
-- 执行时机：一期上线1周后，根据实际查询情况添加
-- ====================================

USE teamventure_main;

-- 1. plans表：按状态和创建时间查询（如果缺失）
CREATE INDEX IF NOT EXISTS idx_status_create_time
ON plans (status, create_time DESC);

-- 2. domain_events表：按事件类型和时间查询
CREATE INDEX IF NOT EXISTS idx_event_type_occurred_at
ON domain_events (event_type, occurred_at DESC);

-- 3. supplier_contact_logs表：按供应商统计
CREATE INDEX IF NOT EXISTS idx_supplier_contact_time
ON supplier_contact_logs (supplier_id, contact_time DESC);

-- 4. 覆盖索引：我的方案列表（避免回表）
CREATE INDEX IF NOT EXISTS idx_user_status_time_covering
ON plans (user_id, status, create_time DESC, plan_id, plan_name, summary, budget_total);
```

---

## 6. 数据库配置建议

### 6.1 MySQL配置优化（my.cnf）

```ini
[mysqld]
# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB设置
innodb_buffer_pool_size = 4G        # 物理内存的50-70%
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2  # 性能优先（允许丢失1秒数据）
innodb_file_per_table = 1

# 连接设置
max_connections = 500
max_connect_errors = 1000

# 查询缓存（8.0默认关闭，使用Redis）
query_cache_type = 0

# 慢查询日志
slow_query_log = 1
long_query_time = 2                  # 超过2秒记录
log_queries_not_using_indexes = 1

# Binlog（主从复制）
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7
```

### 6.2 主从复制配置

#### Master配置
```ini
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW
binlog_do_db = teamventure_main

# 创建复制用户
CREATE USER 'repl'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
```

#### Slave配置
```ini
[mysqld]
server-id = 2
read_only = 1
relay_log = /var/log/mysql/mysql-relay-bin

# 配置复制
CHANGE MASTER TO
  MASTER_HOST='mysql-master',
  MASTER_USER='repl',
  MASTER_PASSWORD='repl_password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=0;

START SLAVE;
SHOW SLAVE STATUS\G
```

---

## 附录

### A. 数据字典

| 表名 | 预估行数（1年） | 平均行大小 | 存储空间 |
|------|----------------|-----------|---------|
| users | 100,000 | 500B | 50MB |
| sessions | 100,000 | 300B | 30MB |
| plan_requests | 500,000 | 600B | 300MB |
| plans | 1,500,000 | 3KB | 4.5GB |
| suppliers | 5,000 | 1KB | 5MB |
| supplier_contact_logs | 1,000,000 | 200B | 200MB |
| domain_events | 5,000,000 | 500B | 2.5GB |
| **合计** | - | - | **≈ 7.5GB** |

### B. 备份策略

```bash
# 每日全量备份
0 2 * * * mysqldump -uroot -p teamventure_main > /backup/full_$(date +\%Y\%m\%d).sql

# 每小时增量备份（Binlog）
0 * * * * cp /var/log/mysql/mysql-bin.* /backup/binlog/

# 保留策略
# - 全量备份保留30天
# - Binlog保留7天
# - 归档数据保留1年（OSS）
```

---

**版本历史**:
- v1.0 (2025-12-30): 初始版本，一期建表脚本

**下一步优化**:
1. 二期：实施分区表（plans/domain_events）
2. 引入读写分离中间件（MyCAT/ShardingSphere）
3. 冷热数据分离（归档到OSS）

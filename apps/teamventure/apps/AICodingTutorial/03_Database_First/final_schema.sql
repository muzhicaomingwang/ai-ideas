-- Database Schema for Corporate Event Booking System
-- Dialect: MySQL 8.0
-- Convention: snake_case, t_ prefix

CREATE DATABASE IF NOT EXISTS `teamventure_tutorial` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `teamventure_tutorial`;

-- 1. Employee (员工表)
CREATE TABLE `t_employee` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
    `employee_id` VARCHAR(32) NOT NULL COMMENT 'Unique Employee ID (e.g. EMP001)',
    `name` VARCHAR(64) NOT NULL COMMENT 'Display Name',
    `email` VARCHAR(128) NOT NULL COMMENT 'Corporate Email',
    `team_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'FK: Team ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_employee_id` (`employee_id`),
    KEY `idx_email` (`email`)
) ENGINE=InnoDB COMMENT='Employee Info';

-- 2. Team (团队表)
CREATE TABLE `t_team` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL COMMENT 'Team Name',
    `leader_id` BIGINT UNSIGNED DEFAULT NULL COMMENT 'FK: Employee ID of the leader',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='Organization Unit';

-- 3. Activity (活动元数据表)
CREATE TABLE `t_activity` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(128) NOT NULL COMMENT 'Activity Title (e.g. Badminton)',
    `description` TEXT COMMENT 'Rich text description',
    `cover_image_url` VARCHAR(255) DEFAULT NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Soft delete flag',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='Activity Metadata';

-- 4. Session (场次表 - The dynamic instance)
CREATE TABLE `t_session` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `activity_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK: Activity',
    `status` VARCHAR(20) NOT NULL DEFAULT 'PUBLISHED' COMMENT 'Enum: PUBLISHED, FULL, CANCELLED, COMPLETED',
    `start_time` DATETIME NOT NULL,
    `end_time` DATETIME NOT NULL,
    `location_name` VARCHAR(128) NOT NULL,
    `max_capacity` INT NOT NULL COMMENT 'Max participants',
    `booked_count` INT NOT NULL DEFAULT 0 COMMENT 'Current confirmed bookings (Denormalized for perf)',
    `created_by` BIGINT UNSIGNED NOT NULL COMMENT 'Creator Employee ID',
    `version` INT NOT NULL DEFAULT 0 COMMENT 'Optimistic Lock',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_activity_id` (`activity_id`),
    KEY `idx_start_time` (`start_time`)
) ENGINE=InnoDB COMMENT='Activity Sessions';

-- 5. Booking (预约记录表)
CREATE TABLE `t_booking` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `session_id` BIGINT UNSIGNED NOT NULL,
    `employee_id` BIGINT UNSIGNED NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED' COMMENT 'Enum: CONFIRMED, WAITING, CANCELLED, CHECKED_IN',
    `queue_number` INT DEFAULT NULL COMMENT 'Waitlist queue position (only if WAITING)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_session_employee` (`session_id`, `employee_id`), -- Idempotency: One user per session
    KEY `idx_employee_session` (`employee_id`, `session_id`)
) ENGINE=InnoDB COMMENT='Booking Records';

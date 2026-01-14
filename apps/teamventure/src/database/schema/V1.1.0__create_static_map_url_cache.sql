-- V1.1.0: 创建静态地图URL缓存表
--
-- 用途：缓存生成的高德静态地图URL，避免重复调用API
--
-- 缓存策略：
--   - L1: Caffeine内存缓存（1000条，7天TTL）
--   - L2: Redis缓存（30天TTL）
--   - L3: 本表MySQL缓存（永久存储，防缓存穿透）
--
-- 作者: TeamVenture
-- 日期: 2026-01-14

CREATE TABLE IF NOT EXISTS `static_map_url_cache` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
    `cache_key` VARCHAR(32) NOT NULL UNIQUE COMMENT 'MD5缓存键（由MapRequest参数生成）',
    `url` TEXT NOT NULL COMMENT '静态地图URL（高德API返回）',
    `request` JSON COMMENT '原始请求参数（用于调试和分析）',
    `hit_count` INT DEFAULT 0 COMMENT '缓存命中次数（用于热度统计）',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `last_hit_at` TIMESTAMP NULL COMMENT '最后命中时间',

    INDEX `idx_cache_key` (`cache_key`) COMMENT '缓存键索引（查询优化）',
    INDEX `idx_created_at` (`created_at`) COMMENT '创建时间索引（清理旧数据）',
    INDEX `idx_hit_count` (`hit_count`) COMMENT '命中次数索引（热度分析）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='静态地图URL缓存表（三级缓存的L3层）';

-- 初始化占位数据（可选）
-- INSERT INTO `static_map_url_cache` (`cache_key`, `url`, `request`, `hit_count`)
-- VALUES ('placeholder_detail', 'https://cdn.teamventure.com/placeholder/map_detail.png',
--         '{"size":"DETAIL","zoom":12,"center":"0,0","style":"normal"}', 0);

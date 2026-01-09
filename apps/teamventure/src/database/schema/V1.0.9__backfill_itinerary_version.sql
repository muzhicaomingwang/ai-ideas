-- 修复历史数据/历史环境：plans.itinerary_version 可能缺失或为 NULL，导致行程更新 CAS 永远冲突
--
-- 目标：
-- 1) 若列不存在：补加 itinerary_version（NOT NULL DEFAULT 1）
-- 2) 若列存在但为 NULL：回填为 1
-- 3) 确保列最终为 NOT NULL DEFAULT 1

-- 1) add column if missing (MySQL 8: use dynamic SQL for compatibility)
SET @tv_col_exists := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'plans'
    AND column_name = 'itinerary_version'
);

SET @tv_sql_add := IF(
  @tv_col_exists = 0,
  'ALTER TABLE `plans` ADD COLUMN `itinerary_version` INT NOT NULL DEFAULT 1 COMMENT ''行程版本号（CAS）'' AFTER `itinerary`',
  'SELECT 1'
);
PREPARE tv_stmt_add FROM @tv_sql_add;
EXECUTE tv_stmt_add;
DEALLOCATE PREPARE tv_stmt_add;

-- 2) backfill NULL values (in case column existed but was nullable / bad default)
UPDATE `plans`
SET `itinerary_version` = 1
WHERE `itinerary_version` IS NULL;

-- 3) enforce NOT NULL DEFAULT 1 (only if column exists)
SET @tv_col_exists2 := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'plans'
    AND column_name = 'itinerary_version'
);

SET @tv_sql_mod := IF(
  @tv_col_exists2 = 1,
  'ALTER TABLE `plans` MODIFY COLUMN `itinerary_version` INT NOT NULL DEFAULT 1 COMMENT ''行程版本号（CAS）''',
  'SELECT 1'
);
PREPARE tv_stmt_mod FROM @tv_sql_mod;
EXECUTE tv_stmt_mod;
DEALLOCATE PREPARE tv_stmt_mod;


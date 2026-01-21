-- 说明: 为 plans 表添加方案 Logo 字段（用于方案列表卡片展示）
-- 注意: 该目录为 MySQL 初始化脚本；在已有数据卷场景需通过应用启动迁移或手动执行本 ALTER。

ALTER TABLE `plans`
  ADD COLUMN `logo_url` VARCHAR(512) NULL COMMENT '方案Logo图片URL（可选）' AFTER `highlights`;


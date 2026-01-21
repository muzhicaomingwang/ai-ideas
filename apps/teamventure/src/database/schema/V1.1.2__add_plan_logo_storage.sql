-- 说明: 为 plans 表添加方案 Logo 对象引用字段（minio://bucket/key）
-- 备注: V1.1.1 增加了 logo_url（历史/兼容）。本字段用于稳定存储 OSS 对象引用。

ALTER TABLE `plans`
  ADD COLUMN `logo_storage` VARCHAR(512) NULL COMMENT '方案Logo对象引用（minio://bucket/key，可选）' AFTER `logo_url`;


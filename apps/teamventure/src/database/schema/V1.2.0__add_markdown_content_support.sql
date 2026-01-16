-- V1.2.0: 添加Markdown格式需求输入支持
--
-- 变更内容：
-- 1. plan_requests 表添加 markdown_content 字段
-- 2. 保留旧版结构化字段（向后兼容）
-- 3. markdown_content 为 TEXT 类型，支持最多 65535 字符
--
-- 使用场景：
-- - 用户在前端通过预填充的Markdown模板输入团建需求
-- - 包含：天数、人数、预算、路线、交通（航班/高铁）、住宿（每日酒店）、活动偏好、特殊要求
-- - AI Agent直接解析Markdown内容生成方案

-- 添加 markdown_content 字段到 plan_requests 表
ALTER TABLE plan_requests
ADD COLUMN markdown_content TEXT COMMENT 'Markdown格式的需求描述（V2版本）' AFTER user_id;

-- 添加索引以支持全文搜索（可选，便于后续功能扩展）
-- ALTER TABLE plan_requests ADD FULLTEXT INDEX idx_markdown_content (markdown_content);

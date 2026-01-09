-- 增加行程版本号，用于行程变更的 CAS 并发校验
ALTER TABLE `plans`
  ADD COLUMN `itinerary_version` INT NOT NULL DEFAULT 1 COMMENT '行程版本号（CAS）' AFTER `itinerary`;


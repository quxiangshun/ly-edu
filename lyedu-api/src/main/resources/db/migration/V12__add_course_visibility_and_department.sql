-- 课程可见性：1-公开，0-私有；私有时关联部门，仅本部门及子部门用户可见
ALTER TABLE `ly_course` ADD COLUMN `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有' AFTER `is_required`;
ALTER TABLE `ly_course` ADD COLUMN `department_id` BIGINT DEFAULT NULL COMMENT '关联部门（私有时必填）' AFTER `visibility`;
ALTER TABLE `ly_course` ADD KEY `idx_department_id` (`department_id`);

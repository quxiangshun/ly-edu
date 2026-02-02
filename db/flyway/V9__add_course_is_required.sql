-- 课程是否必修（PlayEdu 对齐）
ALTER TABLE `ly_course` ADD COLUMN `is_required` TINYINT DEFAULT 0 COMMENT '是否必修：0-选修，1-必修' AFTER `sort`;

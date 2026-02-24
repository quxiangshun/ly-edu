-- 移除课程可见性与部门关联
-- 1. 删除课程-部门关联表
DROP TABLE IF EXISTS ly_course_department;

-- 2. 移除 ly_course.visibility 列（若存在）
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_course' AND COLUMN_NAME = 'visibility');
SET @sql = IF(@col_exists > 0, 'ALTER TABLE ly_course DROP COLUMN visibility', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

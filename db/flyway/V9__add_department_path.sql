-- 部门表新增 path 列（祖籍路径，类 PostgreSQL ltree）
-- path 存储从根到当前部门的 ID 链（含自身），如 "1.2.3"，便于祖籍查询
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_department' AND COLUMN_NAME = 'path');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE ly_department ADD COLUMN path VARCHAR(500) DEFAULT '''' COMMENT ''祖籍路径'' AFTER parent_id', 'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists = (SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_department' AND INDEX_NAME = 'idx_department_path');
SET @sql2 = IF(@idx_exists = 0, 'CREATE INDEX idx_department_path ON ly_department(path(100))', 'SELECT 1');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- 根部门 path 回填；子部门 path 由应用在 save/update 时维护
UPDATE ly_department SET path = CAST(id AS CHAR) WHERE (parent_id = 0 OR parent_id IS NULL) AND deleted = 0;

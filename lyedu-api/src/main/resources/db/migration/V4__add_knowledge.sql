-- 知识库表（独立于课程，按部门可见）
CREATE TABLE IF NOT EXISTS `ly_knowledge` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '标题/名称',
    `category` VARCHAR(100) DEFAULT NULL COMMENT '分类（如：制度文档、技术文档）',
    `file_name` VARCHAR(255) DEFAULT NULL COMMENT '文件名',
    `file_url` VARCHAR(500) NOT NULL COMMENT '文件地址',
    `file_size` BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    `file_type` VARCHAR(50) DEFAULT NULL COMMENT '文件类型/扩展名',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有（按部门）',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_category` (`category`),
    KEY `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- 知识库-部门关联表（多对多，私有时可见部门）
CREATE TABLE IF NOT EXISTS `ly_knowledge_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `knowledge_id` BIGINT NOT NULL COMMENT '知识ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_knowledge_department` (`knowledge_id`, `department_id`),
    KEY `idx_knowledge_id` (`knowledge_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库-部门关联表';

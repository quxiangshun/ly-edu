-- 证书模板表（打印样式、占位符配置）
CREATE TABLE IF NOT EXISTS `ly_certificate_template` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '说明',
    `config` TEXT DEFAULT NULL COMMENT '模板配置 JSON（占位符、样式等）',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书模板表';

-- 证书颁发规则表（关联考试/任务，合格后颁发）
CREATE TABLE IF NOT EXISTS `ly_certificate` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `template_id` BIGINT NOT NULL COMMENT '证书模板ID',
    `name` VARCHAR(200) NOT NULL COMMENT '证书名称（如：Java 考试合格证）',
    `source_type` VARCHAR(20) NOT NULL COMMENT '来源类型：exam-考试，task-任务',
    `source_id` BIGINT NOT NULL COMMENT '来源ID（考试ID或任务ID）',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_template_id` (`template_id`),
    KEY `idx_source` (`source_type`, `source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书颁发规则表';

-- 用户已获证书表（颁发记录）
CREATE TABLE IF NOT EXISTS `ly_user_certificate` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `certificate_id` BIGINT NOT NULL COMMENT '证书规则ID',
    `template_id` BIGINT NOT NULL COMMENT '证书模板ID',
    `certificate_no` VARCHAR(64) NOT NULL COMMENT '证书编号（唯一）',
    `title` VARCHAR(200) NOT NULL COMMENT '证书标题',
    `issued_at` DATETIME NOT NULL COMMENT '颁发时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_certificate_no` (`certificate_no`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_certificate_id` (`certificate_id`),
    KEY `idx_template_id` (`template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户已获证书表';

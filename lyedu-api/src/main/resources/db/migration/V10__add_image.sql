-- 图片库：用于课程封面等，可复用上传

CREATE TABLE IF NOT EXISTS `ly_image` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `path` VARCHAR(500) NOT NULL COMMENT '相对路径，如 2025/01/xxx.jpg',
    `file_size` BIGINT DEFAULT 0 COMMENT '文件大小（字节）',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图片库';

-- Flyway V4: 创建文件上传进度表（用于断点续传）

-- 文件上传进度表
CREATE TABLE IF NOT EXISTS `ly_file_upload` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `file_id` VARCHAR(64) NOT NULL COMMENT '文件唯一标识（MD5或UUID）',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_size` BIGINT NOT NULL COMMENT '文件大小（字节）',
    `file_type` VARCHAR(50) DEFAULT NULL COMMENT '文件类型',
    `chunk_size` BIGINT NOT NULL COMMENT '分片大小（字节）',
    `total_chunks` INT NOT NULL COMMENT '总分片数',
    `uploaded_chunks` INT DEFAULT 0 COMMENT '已上传分片数',
    `upload_path` VARCHAR(500) DEFAULT NULL COMMENT '上传路径',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-上传中，1-已完成，2-已失败',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_file_id` (`file_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传进度表';

-- 文件分片上传记录表
CREATE TABLE IF NOT EXISTS `ly_file_chunk` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `file_id` VARCHAR(64) NOT NULL COMMENT '文件唯一标识',
    `chunk_index` INT NOT NULL COMMENT '分片索引（从0开始）',
    `chunk_size` BIGINT NOT NULL COMMENT '分片大小（字节）',
    `chunk_path` VARCHAR(500) NOT NULL COMMENT '分片存储路径',
    `upload_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_file_chunk` (`file_id`, `chunk_index`),
    KEY `idx_file_id` (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件分片上传记录表';

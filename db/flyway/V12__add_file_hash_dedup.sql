-- 合并：视频去重表 + 视频封面（与 Alembic v12 对应）
-- 1. 视频去重：按文件内容哈希只保留一份
CREATE TABLE IF NOT EXISTS ly_file_hash (
    id BIGINT NOT NULL AUTO_INCREMENT,
    content_hash VARCHAR(64) NOT NULL COMMENT '文件内容 SHA-256 十六进制',
    relative_path VARCHAR(500) NOT NULL COMMENT '相对路径，如 videos/xxx/file.mp4',
    file_size BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_content_hash (content_hash),
    KEY idx_content_hash (content_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件内容哈希表，用于视频去重';

-- 2. 视频表增加封面字段（可选）
ALTER TABLE ly_video ADD COLUMN cover VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL' AFTER url;

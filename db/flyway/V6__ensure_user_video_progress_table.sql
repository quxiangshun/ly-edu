-- 确保用户视频学习进度表存在（兼容早期未包含此表的库）
CREATE TABLE IF NOT EXISTS `ly_user_video_progress` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `video_id` BIGINT NOT NULL COMMENT '视频ID',
    `progress` INT DEFAULT 0 COMMENT '学习进度（秒）',
    `duration` INT DEFAULT 0 COMMENT '视频总时长（秒）',
    `is_finished` TINYINT DEFAULT 0 COMMENT '是否完成：0-未完成，1-已完成',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_video` (`user_id`, `video_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_video_id` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户视频学习进度表';

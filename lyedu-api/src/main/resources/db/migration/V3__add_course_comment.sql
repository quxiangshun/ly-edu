-- 课程评论表（支持多级回复、按课程或章节维度）
CREATE TABLE IF NOT EXISTS `ly_course_comment` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `chapter_id` BIGINT DEFAULT NULL COMMENT '章节ID，NULL表示课程级评论',
    `user_id` BIGINT NOT NULL COMMENT '评论用户ID',
    `parent_id` BIGINT DEFAULT NULL COMMENT '父评论ID，NULL表示一级评论',
    `content` TEXT NOT NULL COMMENT '评论内容',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-隐藏，1-正常',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_chapter_id` (`chapter_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程评论表';

-- 视频播放次数、点赞：播放计数 + 一人一点赞、可取消
ALTER TABLE ly_video ADD COLUMN play_count INT NOT NULL DEFAULT 0 COMMENT '播放次数（每次播放+1）' AFTER sort;
ALTER TABLE ly_video ADD COLUMN like_count INT NOT NULL DEFAULT 0 COMMENT '点赞数' AFTER play_count;

CREATE TABLE IF NOT EXISTS ly_video_like (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    video_id BIGINT NOT NULL COMMENT '视频ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_video (user_id, video_id),
    KEY idx_video_id (video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频点赞（一人一点赞，可取消）';

-- 课程-视频 多对多（保留）
CREATE TABLE IF NOT EXISTS ly_course_video (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    course_id BIGINT NOT NULL COMMENT '课程ID',
    video_id BIGINT NOT NULL COMMENT '视频ID',
    chapter_id BIGINT DEFAULT NULL COMMENT '章节ID（该课程下）',
    sort INT DEFAULT 0 COMMENT '排序',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_course_video (course_id, video_id),
    KEY idx_course_id (course_id),
    KEY idx_video_id (video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-视频关联（多对多）';

-- 将现有 ly_video 的 course 关联写入 ly_course_video，保证按课程查视频时能包含原有数据
INSERT IGNORE INTO ly_course_video (course_id, video_id, chapter_id, sort)
SELECT course_id, id, chapter_id, sort FROM ly_video WHERE deleted = 0;

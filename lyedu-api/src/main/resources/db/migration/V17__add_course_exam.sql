-- 课程-考试关联（1 门课关联 1 场考试；1 场考试可被多门课引用）
CREATE TABLE IF NOT EXISTS ly_course_exam (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    course_id BIGINT NOT NULL COMMENT '课程ID',
    exam_id BIGINT NOT NULL COMMENT '考试ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_course_exam (course_id),
    KEY idx_exam_id (exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-考试关联（多课程可共用同一考试）';

-- 试题表（单选/多选/判断/填空/简答）
CREATE TABLE IF NOT EXISTS `ly_question` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `type` VARCHAR(20) NOT NULL COMMENT '题型：single-单选，multi-多选，judge-判断，fill-填空，short-简答',
    `title` TEXT NOT NULL COMMENT '题目标题/题干',
    `options` JSON DEFAULT NULL COMMENT '选项（单选/多选/判断为 JSON 数组，如 ["A","B","C","D"]）',
    `answer` TEXT DEFAULT NULL COMMENT '参考答案（单选填选项字母，多选填如 AB，判断填 T/F，填空/简答填文本）',
    `score` INT DEFAULT 10 COMMENT '默认分值',
    `analysis` TEXT DEFAULT NULL COMMENT '解析',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试题表';

-- 试卷表
CREATE TABLE IF NOT EXISTS `ly_paper` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '试卷名称',
    `total_score` INT DEFAULT 100 COMMENT '总分',
    `pass_score` INT DEFAULT 60 COMMENT '及格分',
    `duration_minutes` INT DEFAULT 60 COMMENT '考试时长（分钟）',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷表';

-- 试卷-试题关联表（组卷）
CREATE TABLE IF NOT EXISTS `ly_paper_question` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `paper_id` BIGINT NOT NULL COMMENT '试卷ID',
    `question_id` BIGINT NOT NULL COMMENT '试题ID',
    `score` INT DEFAULT 10 COMMENT '本题分值',
    `sort` INT DEFAULT 0 COMMENT '题目顺序',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_paper_question` (`paper_id`, `question_id`),
    KEY `idx_paper_id` (`paper_id`),
    KEY `idx_question_id` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷-试题关联表';

-- 考试任务表
CREATE TABLE IF NOT EXISTS `ly_exam` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '考试名称',
    `paper_id` BIGINT NOT NULL COMMENT '试卷ID',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `duration_minutes` INT DEFAULT 60 COMMENT '考试时长（分钟），NULL 取试卷默认',
    `pass_score` INT DEFAULT NULL COMMENT '及格分，NULL 取试卷默认',
    `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有（按部门）',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-下架，1-上架',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_paper_id` (`paper_id`),
    KEY `idx_start_time` (`start_time`),
    KEY `idx_end_time` (`end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试任务表';

-- 考试-部门关联表（私有可见）
CREATE TABLE IF NOT EXISTS `ly_exam_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `exam_id` BIGINT NOT NULL COMMENT '考试ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_exam_department` (`exam_id`, `department_id`),
    KEY `idx_exam_id` (`exam_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试-部门关联表';

-- 考试记录表（用户交卷）
CREATE TABLE IF NOT EXISTS `ly_exam_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `exam_id` BIGINT NOT NULL COMMENT '考试ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `paper_id` BIGINT NOT NULL COMMENT '试卷ID',
    `score` INT DEFAULT NULL COMMENT '得分',
    `passed` TINYINT DEFAULT NULL COMMENT '是否及格：0-否，1-是',
    `answers` JSON DEFAULT NULL COMMENT '用户答案 JSON',
    `submit_time` DATETIME DEFAULT NULL COMMENT '交卷时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_exam_id` (`exam_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_exam_user` (`exam_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试记录表';

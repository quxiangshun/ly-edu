-- Flyway V1: 完整初始化（整合原 V1～V18 为单文件）

-- 用户表（含 feishu_open_id、union_id、entry_date、total_points）
CREATE TABLE IF NOT EXISTS `ly_user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码',
    `real_name` VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `mobile` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像',
    `feishu_open_id` VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id，用于扫码登录',
    `union_id` VARCHAR(64) DEFAULT NULL COMMENT '开放平台 union_id，同一主体下多应用统一',
    `department_id` BIGINT DEFAULT NULL COMMENT '部门ID',
    `entry_date` DATE DEFAULT NULL COMMENT '入职日期',
    `total_points` INT DEFAULT 0 COMMENT '累计积分',
    `role` VARCHAR(20) DEFAULT 'student' COMMENT '角色：admin-管理员，teacher-教师，student-学员',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_feishu_open_id` (`feishu_open_id`),
    KEY `idx_union_id` (`union_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 部门表
CREATE TABLE IF NOT EXISTS `ly_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '部门名称',
    `parent_id` BIGINT DEFAULT 0 COMMENT '父部门ID',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';

-- 课程分类表
CREATE TABLE IF NOT EXISTS `ly_course_category` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '分类名称',
    `parent_id` BIGINT DEFAULT 0 COMMENT '父分类ID',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程分类表';

-- 课程表（含 visibility、is_required；部门关联见 ly_course_department）
CREATE TABLE IF NOT EXISTS `ly_course` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '课程标题',
    `cover` VARCHAR(255) DEFAULT NULL COMMENT '课程封面',
    `description` TEXT COMMENT '课程描述',
    `category_id` BIGINT DEFAULT NULL COMMENT '分类ID',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-下架，1-上架',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `is_required` TINYINT DEFAULT 0 COMMENT '是否必修：0-选修，1-必修',
    `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- 课程-部门关联表（多对多）
CREATE TABLE IF NOT EXISTS `ly_course_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_course_department` (`course_id`, `department_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-部门关联表';

-- 课程章节表
CREATE TABLE IF NOT EXISTS `ly_course_chapter` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `title` VARCHAR(200) NOT NULL COMMENT '章节标题',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_course_id` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程章节表';

-- 课程附件表
CREATE TABLE IF NOT EXISTS `ly_course_attachment` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `name` VARCHAR(200) NOT NULL COMMENT '附件名称',
    `type` VARCHAR(50) DEFAULT NULL COMMENT '附件类型/扩展名',
    `file_url` VARCHAR(500) NOT NULL COMMENT '文件地址',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_course_id` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程附件表';

-- 视频表（含 cover、play_count、like_count）
CREATE TABLE IF NOT EXISTS `ly_video` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `chapter_id` BIGINT DEFAULT NULL COMMENT '章节ID',
    `title` VARCHAR(200) NOT NULL COMMENT '视频标题',
    `url` VARCHAR(500) NOT NULL COMMENT '视频地址',
    `cover` VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL',
    `duration` INT DEFAULT 0 COMMENT '视频时长（秒）',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `play_count` INT NOT NULL DEFAULT 0 COMMENT '播放次数',
    `like_count` INT NOT NULL DEFAULT 0 COMMENT '点赞数',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_chapter_id` (`chapter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频表';

-- 用户课程关联表
CREATE TABLE IF NOT EXISTS `ly_user_course` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `progress` INT DEFAULT 0 COMMENT '学习进度（百分比）',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0-学习中，1-已完成',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_course` (`user_id`, `course_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_course_id` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户课程关联表';

-- 用户视频学习进度表
CREATE TABLE IF NOT EXISTS `ly_user_video_progress` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `video_id` BIGINT NOT NULL COMMENT '视频ID',
    `progress` INT DEFAULT 0 COMMENT '学习进度（秒）',
    `duration` INT DEFAULT 0 COMMENT '视频总时长（秒）',
    `is_finished` TINYINT DEFAULT 0 COMMENT '是否完成：0-未完成，1-已完成',
    `last_play_ping_at` DATETIME NULL COMMENT '最近播放心跳时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_video` (`user_id`, `video_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_video_id` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户视频学习进度表';

-- 文件上传进度表
CREATE TABLE IF NOT EXISTS `ly_file_upload` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `file_id` VARCHAR(64) NOT NULL COMMENT '文件唯一标识',
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

-- 课程评论表
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

-- 知识库表
CREATE TABLE IF NOT EXISTS `ly_knowledge` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '标题/名称',
    `category` VARCHAR(100) DEFAULT NULL COMMENT '分类',
    `file_name` VARCHAR(255) DEFAULT NULL COMMENT '文件名',
    `file_url` VARCHAR(500) NOT NULL COMMENT '文件地址',
    `file_size` BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    `file_type` VARCHAR(50) DEFAULT NULL COMMENT '文件类型/扩展名',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted` TINYINT DEFAULT 0 COMMENT '是否删除：0-未删除，1-已删除',
    PRIMARY KEY (`id`),
    KEY `idx_category` (`category`),
    KEY `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- 知识库-部门关联表
CREATE TABLE IF NOT EXISTS `ly_knowledge_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `knowledge_id` BIGINT NOT NULL COMMENT '知识ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_knowledge_department` (`knowledge_id`, `department_id`),
    KEY `idx_knowledge_id` (`knowledge_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库-部门关联表';

-- 试题表
CREATE TABLE IF NOT EXISTS `ly_question` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `type` VARCHAR(20) NOT NULL COMMENT '题型：single-单选，multi-多选，judge-判断，fill-填空，short-简答',
    `title` TEXT NOT NULL COMMENT '题目标题/题干',
    `options` JSON DEFAULT NULL COMMENT '选项',
    `answer` TEXT DEFAULT NULL COMMENT '参考答案',
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

-- 试卷-试题关联表
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
    `duration_minutes` INT DEFAULT 60 COMMENT '考试时长（分钟）',
    `pass_score` INT DEFAULT NULL COMMENT '及格分',
    `visibility` TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-下架，1-上架',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_paper_id` (`paper_id`),
    KEY `idx_start_time` (`start_time`),
    KEY `idx_end_time` (`end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试任务表';

-- 考试-部门关联表
CREATE TABLE IF NOT EXISTS `ly_exam_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `exam_id` BIGINT NOT NULL COMMENT '考试ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_exam_department` (`exam_id`, `department_id`),
    KEY `idx_exam_id` (`exam_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试-部门关联表';

-- 考试记录表
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

-- 证书模板表
CREATE TABLE IF NOT EXISTS `ly_certificate_template` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '说明',
    `config` TEXT DEFAULT NULL COMMENT '模板配置 JSON',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书模板表';

-- 证书颁发规则表
CREATE TABLE IF NOT EXISTS `ly_certificate` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `template_id` BIGINT NOT NULL COMMENT '证书模板ID',
    `name` VARCHAR(200) NOT NULL COMMENT '证书名称',
    `source_type` VARCHAR(20) NOT NULL COMMENT '来源类型：exam-考试，task-任务',
    `source_id` BIGINT NOT NULL COMMENT '来源ID',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_template_id` (`template_id`),
    KEY `idx_source` (`source_type`, `source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书颁发规则表';

-- 用户已获证书表
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

-- 周期任务表
CREATE TABLE IF NOT EXISTS `ly_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '任务名称',
    `description` TEXT DEFAULT NULL COMMENT '任务说明',
    `cycle_type` VARCHAR(20) NOT NULL DEFAULT 'once' COMMENT '周期：once-一次性，daily-每日，weekly-每周，monthly-每月',
    `cycle_config` JSON DEFAULT NULL COMMENT '周期配置 JSON',
    `items` JSON NOT NULL COMMENT '闯关项 JSON 数组',
    `certificate_id` BIGINT DEFAULT NULL COMMENT '完成后颁发证书规则ID',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    `start_time` DATETIME DEFAULT NULL COMMENT '开始时间',
    `end_time` DATETIME DEFAULT NULL COMMENT '结束时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_status` (`status`),
    KEY `idx_certificate_id` (`certificate_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='周期任务表';

-- 任务-部门关联表
CREATE TABLE IF NOT EXISTS `ly_task_department` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `task_id` BIGINT NOT NULL COMMENT '任务ID',
    `department_id` BIGINT NOT NULL COMMENT '部门ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_task_department` (`task_id`, `department_id`),
    KEY `idx_task_id` (`task_id`),
    KEY `idx_department_id` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务-部门关联表';

-- 用户任务进度表
CREATE TABLE IF NOT EXISTS `ly_user_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `task_id` BIGINT NOT NULL COMMENT '任务ID',
    `progress` JSON DEFAULT NULL COMMENT '进度 JSON',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-进行中，1-已完成',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_task` (`user_id`, `task_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_task_id` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户任务进度表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS `ly_config` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `config_key` VARCHAR(100) NOT NULL,
    `config_value` TEXT DEFAULT NULL,
    `category` VARCHAR(50) DEFAULT 'site',
    `remark` VARCHAR(200) DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_config_key` (`config_key`),
    KEY `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 积分规则表
CREATE TABLE IF NOT EXISTS `ly_point_rule` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `rule_key` VARCHAR(50) NOT NULL COMMENT '规则键：course_finish, exam_pass, task_finish',
    `rule_name` VARCHAR(100) DEFAULT NULL COMMENT '规则名称',
    `points` INT NOT NULL DEFAULT 0 COMMENT '奖励积分',
    `enabled` TINYINT DEFAULT 1 COMMENT '是否启用：0-否，1-是',
    `remark` VARCHAR(200) DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_rule_key` (`rule_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分规则表';

-- 积分流水表
CREATE TABLE IF NOT EXISTS `ly_point_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `points` INT NOT NULL COMMENT '本次变动积分（正数）',
    `rule_key` VARCHAR(50) NOT NULL,
    `ref_type` VARCHAR(30) DEFAULT NULL COMMENT '关联类型：course, exam, task',
    `ref_id` BIGINT DEFAULT NULL COMMENT '关联ID',
    `remark` VARCHAR(200) DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_ref` (`ref_type`, `ref_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分流水表';

-- 图片库表
CREATE TABLE IF NOT EXISTS `ly_image` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `path` VARCHAR(500) NOT NULL COMMENT '相对路径',
    `file_size` BIGINT DEFAULT 0 COMMENT '文件大小（字节）',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图片库';

-- 文件内容哈希表（视频去重）
CREATE TABLE IF NOT EXISTS `ly_file_hash` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `content_hash` VARCHAR(64) NOT NULL COMMENT '文件内容 SHA-256 十六进制',
    `relative_path` VARCHAR(500) NOT NULL COMMENT '相对路径',
    `file_size` BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_content_hash` (`content_hash`),
    KEY `idx_content_hash` (`content_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件内容哈希表';

-- 视频点赞表
CREATE TABLE IF NOT EXISTS `ly_video_like` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `video_id` BIGINT NOT NULL COMMENT '视频ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_video` (`user_id`, `video_id`),
    KEY `idx_video_id` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频点赞';

-- 课程-视频关联表（多对多）
CREATE TABLE IF NOT EXISTS `ly_course_video` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `video_id` BIGINT NOT NULL COMMENT '视频ID',
    `chapter_id` BIGINT DEFAULT NULL COMMENT '章节ID',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_course_video` (`course_id`, `video_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_video_id` (`video_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-视频关联';

-- 课程-考试关联表
CREATE TABLE IF NOT EXISTS `ly_course_exam` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `exam_id` BIGINT NOT NULL COMMENT '考试ID',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_course_exam` (`course_id`),
    KEY `idx_exam_id` (`exam_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-考试关联';

-- 移除已废弃的部门-视频关联表（若存在）
DROP TABLE IF EXISTS `ly_department_video`;

-- 初始化管理员账号（密码 lyedu123456）
INSERT INTO `ly_user` (`username`, `password`, `real_name`, `email`, `role`, `status`)
VALUES ('admin', '$2a$10$YORpsv2uYZQNNt5hxVNrw.KyeVMcn.fjWYyX3CWGXSwdpL6hRpVSy', '管理员', 'admin@lyedu.com', 'admin', 1)
ON DUPLICATE KEY UPDATE password = VALUES(password), real_name = VALUES(real_name);

-- 初始化测试部门
INSERT INTO `ly_department` (`name`, `parent_id`, `sort`, `status`) VALUES
('技术部', 0, 1, 1),
('产品部', 0, 2, 1),
('运营部', 0, 3, 1)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 初始化测试课程
INSERT INTO `ly_course` (`title`, `cover`, `description`, `status`, `sort`) VALUES
('Java 基础教程', 'https://via.placeholder.com/300x200?text=Java', 'Java 编程语言基础入门课程，适合零基础学员', 1, 1),
('Vue3 前端开发', 'https://via.placeholder.com/300x200?text=Vue3', 'Vue3 框架学习，包含组合式 API 和 TypeScript', 1, 2),
('SpringBoot 实战', 'https://via.placeholder.com/300x200?text=SpringBoot', 'SpringBoot 企业级应用开发实战', 1, 3),
('MySQL 数据库', 'https://via.placeholder.com/300x200?text=MySQL', 'MySQL 数据库设计与优化', 1, 4),
('Docker 容器化', 'https://via.placeholder.com/300x200?text=Docker', 'Docker 容器化部署实践', 1, 5),
('Linux 系统管理', 'https://via.placeholder.com/300x200?text=Linux', 'Linux 系统管理与运维', 1, 6)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- 初始化系统配置
INSERT INTO `ly_config` (`config_key`, `config_value`, `category`, `remark`) VALUES
('site.title', 'LyEdu 学习平台', 'site', '网站标题'),
('site.keywords', '在线学习,培训', 'site', 'SEO关键词'),
('site.description', '企业在线学习与培训平台', 'site', '网站描述'),
('player.allow_download', '0', 'player', '是否允许下载'),
('player.disable_seek', '0', 'player', '禁止拖拽进度条：0-允许，1-禁止'),
('player.disable_speed', '0', 'player', '禁止倍速播放：0-允许，1-禁止'),
('student.default_page_size', '20', 'student', '学员端每页条数')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), remark = VALUES(remark);

-- 初始化积分规则
INSERT INTO `ly_point_rule` (`rule_key`, `rule_name`, `points`, `enabled`, `remark`) VALUES
('course_finish', '完成课程', 10, 1, '学习进度达到100%'),
('exam_pass', '考试合格', 20, 1, '考试通过'),
('task_finish', '完成任务', 30, 1, '周期/新员工任务全部闯关完成')
ON DUPLICATE KEY UPDATE rule_name = VALUES(rule_name), points = VALUES(points), enabled = VALUES(enabled), remark = VALUES(remark);

-- 将现有 ly_video 的 course 关联写入 ly_course_video（保证按课程查视频时能包含原有数据）
INSERT IGNORE INTO `ly_course_video` (`course_id`, `video_id`, `chapter_id`, `sort`)
SELECT `course_id`, `id`, `chapter_id`, `sort` FROM `ly_video` WHERE `deleted` = 0;

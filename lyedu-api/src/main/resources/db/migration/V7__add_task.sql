-- 周期任务表（闯关：课程+考试顺序完成）
CREATE TABLE IF NOT EXISTS `ly_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `title` VARCHAR(200) NOT NULL COMMENT '任务名称',
    `description` TEXT DEFAULT NULL COMMENT '任务说明',
    `cycle_type` VARCHAR(20) NOT NULL DEFAULT 'once' COMMENT '周期：once-一次性，daily-每日，weekly-每周，monthly-每月',
    `cycle_config` JSON DEFAULT NULL COMMENT '周期配置 JSON（如 weekly 的星期几）',
    `items` JSON NOT NULL COMMENT '闯关项 JSON 数组：[{"type":"course","id":1},{"type":"exam","id":2}] 按顺序完成',
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

-- 任务-部门关联（指派可见范围）
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

-- 用户任务进度表（闯关进度、完成状态）
CREATE TABLE IF NOT EXISTS `ly_user_task` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `task_id` BIGINT NOT NULL COMMENT '任务ID',
    `progress` JSON DEFAULT NULL COMMENT '进度 JSON：{"items":[{"type":"course","id":1,"done":1},...]}',
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-进行中，1-已完成',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_task` (`user_id`, `task_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_task_id` (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户任务进度表';

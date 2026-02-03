-- 积分：用户总积分字段、积分规则表、积分流水表

ALTER TABLE `ly_user` ADD COLUMN `total_points` INT DEFAULT 0 COMMENT '累计积分' AFTER `entry_date`;

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

INSERT INTO `ly_point_rule` (`rule_key`, `rule_name`, `points`, `enabled`, `remark`) VALUES
('course_finish', '完成课程', 10, 1, '学习进度达到100%'),
('exam_pass', '考试合格', 20, 1, '考试通过'),
('task_finish', '完成任务', 30, 1, '周期/新员工任务全部闯关完成')
ON DUPLICATE KEY UPDATE rule_name = VALUES(rule_name), points = VALUES(points), enabled = VALUES(enabled), remark = VALUES(remark);

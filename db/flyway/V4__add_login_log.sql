-- 登录监控日志表
CREATE TABLE IF NOT EXISTS `ly_login_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '用户ID',
    `username` VARCHAR(100) DEFAULT NULL COMMENT '用户名（或登录名）',
    `ip` VARCHAR(64) DEFAULT NULL COMMENT '登录 IP',
    `user_agent` VARCHAR(255) DEFAULT NULL COMMENT 'User-Agent',
    `channel` VARCHAR(32) DEFAULT NULL COMMENT '登录渠道：password/feishu 等',
    `success` TINYINT DEFAULT 0 COMMENT '是否成功：0-失败，1-成功',
    `message` VARCHAR(255) DEFAULT NULL COMMENT '失败原因或备注',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录监控日志';


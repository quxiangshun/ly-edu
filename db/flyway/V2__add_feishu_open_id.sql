-- 用户表增加飞书 open_id，用于飞书扫码登录绑定
ALTER TABLE `ly_user` ADD COLUMN `feishu_open_id` VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id，用于扫码登录' AFTER `avatar`;
CREATE UNIQUE KEY `uk_feishu_open_id` ON `ly_user` (`feishu_open_id`);

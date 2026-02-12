-- 应用发布平台（三选一）：feishu=飞书，dingtalk=钉钉，wecom=企微；或 wechat_mp=微信小程序，local=仅账号密码
INSERT INTO `ly_config` (`config_key`, `config_value`, `category`, `remark`) VALUES
('app.platform', 'feishu', 'app', '发布平台（唯一）：feishu/dingtalk/wecom/wechat_mp/local'),
('app.redirect_uri', '', 'app', 'OAuth 回调基础 URL，H5 可留空自动检测')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), remark = VALUES(remark);

-- 播放器限制配置：防拖拽、防倍速

INSERT INTO `ly_config` (`config_key`, `config_value`, `category`, `remark`) VALUES
('player.disable_seek', '0', 'player', '禁止拖拽进度条：0-允许，1-禁止'),
('player.disable_speed', '0', 'player', '禁止倍速播放：0-允许，1-禁止')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), remark = VALUES(remark);

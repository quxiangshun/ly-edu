-- 防挂机：记录最近一次播放心跳时间
ALTER TABLE `ly_user_video_progress` ADD COLUMN `last_play_ping_at` DATETIME NULL COMMENT '最近播放心跳时间' AFTER `update_time`;

-- 为 fa -> ly 数据同步脚本增加字段（nickname/last_login_time/study_time_long, ly_video.description）

ALTER TABLE `ly_user`
  ADD COLUMN `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称（同步自 fa_staff.name）' AFTER `real_name`,
  ADD COLUMN `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间（同步自 fa_staff）' AFTER `union_id`,
  ADD COLUMN `study_time_long` INT DEFAULT 0 COMMENT '学习时长（分钟）（同步自 fa_staff）' AFTER `total_points`;

ALTER TABLE `ly_video`
  ADD COLUMN `description` TEXT DEFAULT NULL COMMENT '视频介绍（同步自 fa_video）' AFTER `title`;

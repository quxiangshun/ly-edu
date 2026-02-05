-- 视频表增加封面字段（可选）
ALTER TABLE ly_video ADD COLUMN cover VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL' AFTER url;

-- 部门表增加飞书部门ID，用于飞书通讯录同步
ALTER TABLE ly_department
    ADD COLUMN feishu_department_id VARCHAR(64) DEFAULT NULL COMMENT '飞书部门ID，用于通讯录同步' AFTER status;
ALTER TABLE ly_department ADD UNIQUE KEY uk_feishu_department_id (feishu_department_id);

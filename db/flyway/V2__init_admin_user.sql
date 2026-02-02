-- Flyway V2: 初始化管理员账号
-- 密码为 lyedu123456 的 BCrypt 哈希

INSERT INTO `ly_user` (`username`, `password`, `real_name`, `email`, `role`, `status`)
VALUES ('admin', '$2a$10$YORpsv2uYZQNNt5hxVNrw.KyeVMcn.fjWYyX3CWGXSwdpL6hRpVSy', '管理员', 'admin@lyedu.com', 'admin', 1)
ON DUPLICATE KEY UPDATE 
    password = VALUES(password),
    real_name = VALUES(real_name);


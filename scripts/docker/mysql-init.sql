-- LyEdu MySQL 容器初始化（仅用户权限）
-- 数据库 lyedu 由 compose 的 MYSQL_DATABASE 自动创建
-- 表结构由 lyedu-api-python Alembic 迁移创建

-- root@'%'：允许从宿主机（经 Docker 端口转发）连接，便于 Navicat/DBeaver 等
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Lyedu@123';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Lyedu@123';
FLUSH PRIVILEGES;

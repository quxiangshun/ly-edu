-- LyEdu MySQL 容器初始化（仅用户与数据库）
-- 表结构由 lyedu-api-python Alembic 迁移创建，应用启动时自动执行 alembic upgrade head

-- root@'%'：允许从本机客户端（经 Docker 端口转发）连接，便于 Navicat/DBeaver 等
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'Lyedu@123';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Lyedu@123';
FLUSH PRIVILEGES;

-- 数据库由 compose 的 MYSQL_DATABASE=lyedu 自动创建，此处显式创建以防万一
CREATE DATABASE IF NOT EXISTS `lyedu` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

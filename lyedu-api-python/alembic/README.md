# Alembic 迁移（与 Flyway 对应）

Python 端使用 Alembic 管理数据库版本，与 Java 端 Flyway 对应。

**统一目录**：迁移脚本已同时放在仓库根目录 `db/alembic/` 下，与 `db/flyway/` 并列，防止仅启动某一语言时缺迁移。`lyedu-api-python/alembic.ini` 已指向 `script_location = ../db/alembic`，执行时从 `db/alembic` 读取；本目录（lyedu-api-python/alembic）可保留作备份或本地开发。

## 版本对应

| Alembic revision           | Flyway 脚本 |
|---------------------------|-------------|
| v12_course_visibility      | V12__add_course_visibility_and_department.sql |

## 使用方式

1. 激活虚拟环境（如有），安装依赖：`pip install -r requirements.txt`
2. 配置数据库：与主项目一致，使用 `config.py` / 环境变量（MYSQL_HOST、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE 等）
3. 在 **lyedu-api-python** 目录下执行：`alembic upgrade head`（会使用 `db/alembic` 中的脚本）
4. 若数据库已由 Flyway 执行过 V12，可仅标记：`alembic stamp v12_course_visibility`
5. 生成新迁移：在 lyedu-api-python 下 `alembic revision -m "描述"`，生成的文件在 `db/alembic/versions/`（因 script_location 指向 db/alembic）

数据库 URL 由 `db/alembic/env.py` 从 lyedu-api-python 的 `config` 读取。

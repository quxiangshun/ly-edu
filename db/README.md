# 数据库迁移统一目录（db/）

本目录存放 **Flyway（Java）** 与 **Alembic（Python）** 的迁移脚本副本，保证无论先启动 Java 还是 Python 服务，都能从同一处执行迁移，避免不同语言启动时缺失版本。

## 目录结构

```
db/
├── README.md           # 本说明
├── flyway/             # Flyway 迁移（与 lyedu-api 中 classpath:db/migration 一致）
│   ├── V1__init_schema.sql
│   ├── V2__init_admin_user.sql
│   └── ... V12 等
└── alembic/            # Alembic 迁移（与 Flyway V1～V12 一一对应）
    ├── env.py          # 从 lyedu-api-python/config 读数据库配置
    ├── script.py.mako
    └── versions/
        ├── v1_init_schema.py ～ v11_ensure_user_course_table.py  # 对应 Flyway V1～V11
        └── v12_add_course_visibility_and_department.py          # 对应 Flyway V12
```

## 使用方式

### Java（Flyway）

- 默认仍使用 `lyedu-api/src/main/resources/db/migration`（classpath）。
- 已配置备用路径：`filesystem:../db/flyway`（以 lyedu-api 为工作目录时）。
- 若只部署 Java，或希望从仓库根目录统一迁移，可让 Flyway 优先使用 `db/flyway`。

### Python（Alembic）

- 在 **lyedu-api-python** 目录下执行（保证能读到 config）：
  ```bash
  alembic upgrade head
  ```
- `lyedu-api-python/alembic.ini` 中已设置 `script_location = ../db/alembic`，迁移从 `db/alembic` 读取，`db/alembic/env.py` 会加载 `lyedu-api-python` 的 config。

### 新增迁移时

1. **Flyway**：在 `lyedu-api/.../db/migration` 新增 `Vn__xxx.sql` 后，**复制一份**到 `db/flyway/`。
2. **Alembic**：在 `db/alembic/versions/` 或 `lyedu-api-python/alembic/versions/` 新增版本后，**同步到另一处**，并保持 `db/alembic` 与 Flyway 版本对应。

这样 Java 与 Python 都有一份迁移副本，防止单语言启动时缺脚本。

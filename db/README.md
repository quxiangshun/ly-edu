# 数据库迁移统一目录（db/）

本目录存放 **Flyway（Java）** 与 **Alembic（Python）** 的迁移脚本副本，保证无论先启动 Java 还是 Python 服务，都能从同一处执行迁移，避免不同语言启动时缺失版本。

**启动时自动执行**：Java 端（Spring Boot）启动时会自动执行 Flyway 迁移；Python 端（uvicorn 启动 FastAPI）会在应用生命周期开始时自动执行 `alembic upgrade head`，无需手动先跑迁移脚本。

## 目录结构

```
db/
├── README.md           # 本说明
├── flyway/             # Flyway 迁移（与 lyedu-api 中 classpath:db/migration 一致）
│   └── V1__init_schema.sql   # 完整初始化（整合原 V1～V18 为单文件）
└── alembic/            # Alembic 迁移（与 Flyway 版本对应）
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
- 或直接启动 Python 应用，启动时会自动执行 `alembic upgrade head`。
- `lyedu-api-python/alembic.ini` 中已设置 `script_location = ../db/alembic`，迁移从 `db/alembic` 读取。

### 若出现 "Unknown column 'v.play_count' in 'field list'"

说明视频播放次数、点赞相关字段尚未执行。请在 **lyedu-api-python** 目录下执行一次迁移：

```bash
python -m alembic -c alembic.ini upgrade head
```

（Windows 下可先设置 `set PYTHONUTF8=1` 再执行，避免编码问题。）

### 若出现 "Can't locate revision identified by 'v19'"

说明数据库中 `alembic_version` 曾记录为 v19，但当前代码链只到 v13（已移除 v14～v19）。在 MySQL 中执行一次即可：

```sql
UPDATE alembic_version SET version_num = 'v13';
```

（若表为空或需初始化，可先执行 `INSERT INTO alembic_version (version_num) VALUES ('v13');`。）

### 新增迁移时

1. **Flyway**：当前 `db/flyway` 仅保留一个 `V1__init_schema.sql`（完整初始化）。若需增量迁移，可在 `lyedu-api/.../db/migration` 新增 `V2__xxx.sql` 后复制到 `db/flyway/`。
2. **Alembic**：在 `db/alembic/versions/` 新增版本后，保持与 Flyway 版本对应。

这样 Java 与 Python 都有一份迁移副本，防止单语言启动时缺脚本。

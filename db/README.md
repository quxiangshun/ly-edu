# 数据库迁移统一目录（db/）

本目录存放 **Alembic（Python）** 迁移脚本。Python 端（uvicorn 启动 FastAPI）会在应用生命周期开始时自动执行 `alembic upgrade head`，无需手动先跑迁移脚本。

## 目录结构

```
db/
├── README.md           # 本说明
├── flyway/             # Flyway 迁移（历史保留，lyedu-api 已暂停维护）
│   └── V1__init_schema.sql
└── alembic/            # Alembic 迁移（Python 使用）
    ├── env.py          # 从 lyedu-api-python/config 读数据库配置
    ├── script.py.mako
    └── versions/       # 迁移版本脚本
```

## 使用方式

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

说明数据库中 `alembic_version` 曾记录为 v19，但当前代码链已变更。在 MySQL 中执行：

```sql
UPDATE alembic_version SET version_num = 'v13';  -- 替换为当前 head 版本
```

（若表为空或需初始化，可先执行 `INSERT INTO alembic_version (version_num) VALUES ('v13');`。）

### 新增迁移时

在 `db/alembic/versions/` 新增版本脚本，执行 `alembic revision -m "描述"` 生成模板后编辑。

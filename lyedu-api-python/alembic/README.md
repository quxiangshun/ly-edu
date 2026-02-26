# Alembic 数据库迁移

本目录为 LyEdu 数据库迁移脚本，启动应用时会自动执行 `alembic upgrade head`。

## 目录结构

```
alembic/
├── env.py          # 从 config 读取数据库连接
├── script.py.mako  # 生成新迁移的模板
├── README.md       # 本说明
└── versions/       # 迁移版本脚本（v1, v2, ...）
```

## 使用方式

### 自动迁移
启动应用（`uvicorn main:app`）时会自动执行迁移，无需手动执行。

### 手动迁移
```bash
cd lyedu-api-python
alembic upgrade head
```

或：
```bash
python -m alembic -c alembic.ini upgrade head
```

（Windows 下可设置 `set PYTHONUTF8=1` 避免编码问题。）

### 新增迁移
```bash
cd lyedu-api-python
alembic revision -m "描述"
```
新文件会生成在 `alembic/versions/` 下。

### 常见问题

**Unknown column 'v.play_count'**
说明相关字段尚未执行，执行一次 `alembic upgrade head`。

**Can't locate revision identified by 'v19'**
数据库中 `alembic_version` 记录的版本已移除，在 MySQL 执行：
```sql
UPDATE alembic_version SET version_num = 'v1';  -- 替换为当前 head
```

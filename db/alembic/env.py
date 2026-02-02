# -*- coding: utf-8 -*-
"""Alembic 环境（db 统一目录）：从 lyedu-api-python/config 读取数据库连接"""
from logging.config import fileConfig
import sys
from pathlib import Path

# db/alembic 在仓库根 db 下；config 在 lyedu-api-python
_repo_root = Path(__file__).resolve().parents[2]
_lyedu_python = _repo_root / "lyedu-api-python"
if str(_lyedu_python) not in sys.path:
    sys.path.insert(0, str(_lyedu_python))

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from alembic import context

import config

# Alembic Config 对象
config_alembic = context.config
if config_alembic.config_file_name is not None:
    fileConfig(config_alembic.config_file_name)

target_metadata = None


def get_url():
    """从 config 构建 MySQL URL（与 lyedu-api-python/db.py 一致）"""
    user = config.MYSQL_USER
    password = config.MYSQL_PASSWORD
    host = config.MYSQL_HOST
    port = config.MYSQL_PORT
    database = config.MYSQL_DATABASE
    charset = config.MYSQL_CHARSET or "utf8mb4"
    from urllib.parse import quote_plus
    safe = quote_plus(password) if password else ""
    return f"mysql+pymysql://{user}:{safe}@{host}:{port}/{database}?charset={charset}"


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()
    connectable = create_engine(url, poolclass=NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

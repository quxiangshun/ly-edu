# -*- coding: utf-8 -*-
"""图片库表（与 Flyway V10 一致）

Revision ID: v10
Revises: v9
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v10"
down_revision: Union[str, None] = "v9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_image (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL COMMENT '原始文件名',
            path VARCHAR(500) NOT NULL COMMENT '相对路径，如 2025/01/xxx.jpg',
            file_size BIGINT DEFAULT 0 COMMENT '文件大小（字节）',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_create_time (create_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图片库'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_image")

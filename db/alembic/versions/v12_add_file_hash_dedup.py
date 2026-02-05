# -*- coding: utf-8 -*-
"""合并：视频去重表 ly_file_hash + 视频封面 ly_video.cover（与 Flyway V12 对应）

Revision ID: v12
Revises: v11
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v12"
down_revision: Union[str, None] = "v11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_hash (
            id BIGINT NOT NULL AUTO_INCREMENT,
            content_hash VARCHAR(64) NOT NULL COMMENT '文件内容 SHA-256 十六进制',
            relative_path VARCHAR(500) NOT NULL COMMENT '相对路径，如 videos/xxx/file.mp4',
            file_size BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_content_hash (content_hash),
            KEY idx_content_hash (content_hash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件内容哈希表，用于视频去重'
    """)
    op.execute(
        "ALTER TABLE ly_video ADD COLUMN cover VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL' AFTER url"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE ly_video DROP COLUMN cover")
    op.execute("DROP TABLE IF EXISTS ly_file_hash")

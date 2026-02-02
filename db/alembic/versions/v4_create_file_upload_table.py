# -*- coding: utf-8 -*-
"""创建文件上传进度表（对应 Flyway V4__create_file_upload_table.sql）

Revision ID: v4
Revises: v3
Create Date: 2025-01-28

对应 Flyway: V4__create_file_upload_table.sql
"""
from typing import Sequence, Union

from alembic import op


revision: str = "v4"
down_revision: Union[str, None] = "v3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_upload (
            id BIGINT NOT NULL AUTO_INCREMENT,
            file_id VARCHAR(64) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_size BIGINT NOT NULL,
            file_type VARCHAR(50) DEFAULT NULL,
            chunk_size BIGINT NOT NULL,
            total_chunks INT NOT NULL,
            uploaded_chunks INT DEFAULT 0,
            upload_path VARCHAR(500) DEFAULT NULL,
            status TINYINT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_file_id (file_id),
            KEY idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传进度表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_chunk (
            id BIGINT NOT NULL AUTO_INCREMENT,
            file_id VARCHAR(64) NOT NULL,
            chunk_index INT NOT NULL,
            chunk_size BIGINT NOT NULL,
            chunk_path VARCHAR(500) NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_file_chunk (file_id, chunk_index),
            KEY idx_file_id (file_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件分片上传记录表'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_file_chunk")
    op.execute("DROP TABLE IF EXISTS ly_file_upload")

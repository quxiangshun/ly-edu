# -*- coding: utf-8 -*-
"""证书相关表（与 Flyway V6 一致）

Revision ID: v6
Revises: v5
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v6"
down_revision: Union[str, None] = "v5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_certificate_template (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500) DEFAULT NULL,
            config TEXT DEFAULT NULL,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书模板表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_certificate (
            id BIGINT NOT NULL AUTO_INCREMENT,
            template_id BIGINT NOT NULL,
            name VARCHAR(200) NOT NULL,
            source_type VARCHAR(20) NOT NULL,
            source_id BIGINT NOT NULL,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_template_id (template_id),
            KEY idx_source (source_type, source_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书颁发规则表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_certificate (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            certificate_id BIGINT NOT NULL,
            template_id BIGINT NOT NULL,
            certificate_no VARCHAR(64) NOT NULL,
            title VARCHAR(200) NOT NULL,
            issued_at DATETIME NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_certificate_no (certificate_no),
            KEY idx_user_id (user_id),
            KEY idx_certificate_id (certificate_id),
            KEY idx_template_id (template_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户已获证书表'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_user_certificate")
    op.execute("DROP TABLE IF EXISTS ly_certificate")
    op.execute("DROP TABLE IF EXISTS ly_certificate_template")

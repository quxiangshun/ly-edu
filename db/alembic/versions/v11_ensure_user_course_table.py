# -*- coding: utf-8 -*-
"""确保用户课程关联表存在（对应 Flyway V11__ensure_user_course_table.sql）

Revision ID: v11
Revises: v10
Create Date: 2025-01-28

对应 Flyway: V11__ensure_user_course_table.sql
"""
from typing import Sequence, Union

from alembic import op


revision: str = "v11"
down_revision: Union[str, None] = "v10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_course (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            course_id BIGINT NOT NULL,
            progress INT DEFAULT 0,
            status TINYINT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_course (user_id, course_id),
            KEY idx_user_id (user_id),
            KEY idx_course_id (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户课程关联表'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_user_course")

# -*- coding: utf-8 -*-
"""课程-考试关联表

Revision ID: v16
Revises: v15
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v16"
down_revision: Union[str, None] = "v15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ly_course_exam (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            course_id BIGINT NOT NULL COMMENT '课程ID',
            exam_id BIGINT NOT NULL COMMENT '考试ID',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_exam (course_id),
            KEY idx_exam_id (exam_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-考试关联（多课程可共用同一考试）'
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_course_exam")

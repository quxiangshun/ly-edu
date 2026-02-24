# -*- coding: utf-8 -*-
"""移除课程可见性与部门关联

Revision ID: v2
Revises: v1
Create Date: 2025-02-24

- 移除 ly_course.visibility 列
- 删除 ly_course_department 表
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v2"
down_revision: Union[str, None] = "v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table: str, column: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c LIMIT 1"
        ),
        {"t": table, "c": column},
    )
    return r.scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()
    # 1. 删除课程-部门关联表
    op.execute("DROP TABLE IF EXISTS ly_course_department")
    # 2. 移除 ly_course.visibility 列（若存在）
    if _column_exists(conn, "ly_course", "visibility"):
        op.execute("ALTER TABLE ly_course DROP COLUMN visibility")


def downgrade() -> None:
    # 恢复 visibility 列
    op.execute(
        "ALTER TABLE ly_course ADD COLUMN visibility TINYINT DEFAULT 1 "
        "COMMENT '可见性：1-公开，0-私有' AFTER is_required"
    )
    # 重建 ly_course_department 表
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_department (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            department_id BIGINT NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_department (course_id, department_id),
            KEY idx_course_id (course_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-部门关联表'
    """)

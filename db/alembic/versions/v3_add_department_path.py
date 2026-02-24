# -*- coding: utf-8 -*-
"""部门表新增 path 列（祖籍路径，类 PostgreSQL ltree）

Revision ID: v3
Revises: v2
Create Date: 2025-02-24

path 存储从根到当前部门的 ID 链（含自身），如 "1.2.3"，便于祖籍查询（类 ltree）。
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v3"
down_revision: Union[str, None] = "v2"
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
    if not _column_exists(conn, "ly_department", "path"):
        op.execute(
            "ALTER TABLE ly_department ADD COLUMN path VARCHAR(500) DEFAULT '' "
            "COMMENT '祖籍路径：从根到自身的ID链，如1.2.3，类ltree' AFTER parent_id"
        )
        op.execute("CREATE INDEX idx_department_path ON ly_department(path(100))")
    # 回填 path
    rows = conn.execute(text("SELECT id, parent_id FROM ly_department WHERE deleted = 0")).fetchall()
    id_to_parent = {r[0]: (r[1] or 0) for r in rows}
    id_to_path = {}

    def get_path(dept_id: int) -> str:
        if dept_id in id_to_path:
            return id_to_path[dept_id]
        pid = id_to_parent.get(dept_id, 0)
        if not pid:
            id_to_path[dept_id] = str(dept_id)
            return str(dept_id)
        parent_path = get_path(pid)
        path = f"{parent_path}.{dept_id}" if parent_path else str(dept_id)
        id_to_path[dept_id] = path
        return path

    for dept_id in id_to_parent:
        get_path(dept_id)

    for dept_id, path in id_to_path.items():
        conn.execute(text("UPDATE ly_department SET path = :p WHERE id = :id AND deleted = 0"), {"p": path or "", "id": dept_id})


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_department_path ON ly_department")
    op.execute("ALTER TABLE ly_department DROP COLUMN path")

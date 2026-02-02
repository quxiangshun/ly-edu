# -*- coding: utf-8 -*-
"""课程可见性及关联部门（对应 Flyway V12__add_course_visibility_and_department.sql）

Revision ID: v12_course_visibility
Revises:
Create Date: 2025-01-28

对应 Flyway: V12__add_course_visibility_and_department.sql
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "v12_course_visibility"
down_revision: Union[str, None] = "v11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 课程可见性：1-公开，0-私有；私有时关联部门，仅本部门及子部门用户可见
    op.execute(
        "ALTER TABLE ly_course ADD COLUMN visibility TINYINT DEFAULT 1 "
        "COMMENT '可见性：1-公开，0-私有' AFTER is_required"
    )
    op.execute(
        "ALTER TABLE ly_course ADD COLUMN department_id BIGINT DEFAULT NULL "
        "COMMENT '关联部门（私有时必填）' AFTER visibility"
    )
    op.execute("ALTER TABLE ly_course ADD KEY idx_department_id (department_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE ly_course DROP KEY idx_department_id")
    op.execute("ALTER TABLE ly_course DROP COLUMN department_id")
    op.execute("ALTER TABLE ly_course DROP COLUMN visibility")

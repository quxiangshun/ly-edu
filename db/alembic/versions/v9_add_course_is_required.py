# -*- coding: utf-8 -*-
"""Add is_required to ly_course (Flyway V9). Revision: v9, Revises: v8."""
from typing import Sequence, Union
from alembic import op

revision: str = "v9"
down_revision: Union[str, None] = "v8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "ALTER TABLE ly_course ADD COLUMN is_required TINYINT DEFAULT 0 "
        "COMMENT '是否必修：0-选修，1-必修' AFTER sort"
    )

def downgrade() -> None:
    op.execute("ALTER TABLE ly_course DROP COLUMN is_required")

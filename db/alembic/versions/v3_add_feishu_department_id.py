# -*- coding: utf-8 -*-
"""部门表增加飞书部门ID，用于飞书通讯录同步

Revision ID: v3
Revises: v2
Create Date: 2025-02-06

"""
from typing import Sequence, Union

from alembic import op

revision: str = "v3"
down_revision: Union[str, None] = "v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE ly_department
        ADD COLUMN feishu_department_id VARCHAR(64) DEFAULT NULL COMMENT '飞书部门ID，用于通讯录同步' AFTER status
    """)
    op.execute("ALTER TABLE ly_department ADD UNIQUE KEY uk_feishu_department_id (feishu_department_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE ly_department DROP INDEX uk_feishu_department_id")
    op.execute("ALTER TABLE ly_department DROP COLUMN feishu_department_id")

# -*- coding: utf-8 -*-
"""用户表增加飞书 open_id（与 Flyway V2 一致）

Revision ID: v2
Revises: v1
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v2"
down_revision: Union[str, None] = "v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE ly_user ADD COLUMN feishu_open_id VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id' AFTER avatar")
    op.execute("CREATE UNIQUE KEY uk_feishu_open_id ON ly_user (feishu_open_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE ly_user DROP KEY uk_feishu_open_id")
    op.execute("ALTER TABLE ly_user DROP COLUMN feishu_open_id")

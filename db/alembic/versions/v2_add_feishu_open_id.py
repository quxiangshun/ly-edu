# -*- coding: utf-8 -*-
"""用户表增加飞书 open_id（与 Flyway V2 一致）

Revision ID: v2
Revises: v1
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v2"
down_revision: Union[str, None] = "v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # 仅当列不存在时添加（幂等，避免重复执行报错）
    r = conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_user' AND COLUMN_NAME = 'feishu_open_id'"
    ))
    if r.scalar() == 0:
        op.execute("ALTER TABLE ly_user ADD COLUMN feishu_open_id VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id' AFTER avatar")
    # 仅当索引不存在时创建
    r = conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_user' AND INDEX_NAME = 'uk_feishu_open_id'"
    ))
    if r.scalar() == 0:
        op.execute("ALTER TABLE ly_user ADD UNIQUE KEY uk_feishu_open_id (feishu_open_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE ly_user DROP KEY uk_feishu_open_id")
    op.execute("ALTER TABLE ly_user DROP COLUMN feishu_open_id")

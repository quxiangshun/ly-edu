# -*- coding: utf-8 -*-
"""播放器限制配置（与 Flyway V11 一致）

Revision ID: v11
Revises: v10
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v11"
down_revision: Union[str, None] = "v10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO ly_config (config_key, config_value, category, remark) VALUES
        ('player.disable_seek', '0', 'player', '禁止拖拽进度条：0-允许，1-禁止'),
        ('player.disable_speed', '0', 'player', '禁止倍速播放：0-允许，1-禁止')
        ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), remark = VALUES(remark)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM ly_config WHERE config_key IN ('player.disable_seek', 'player.disable_speed')")

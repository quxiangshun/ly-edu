# -*- coding: utf-8 -*-
"""Add last_play_ping_at (Flyway V7). Revision: v7, Revises: v6."""
from typing import Sequence, Union
from alembic import op

revision: str = "v7"
down_revision: Union[str, None] = "v6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "ALTER TABLE ly_user_video_progress ADD COLUMN last_play_ping_at DATETIME NULL "
        "COMMENT '最近播放心跳时间' AFTER update_time"
    )

def downgrade() -> None:
    op.execute("ALTER TABLE ly_user_video_progress DROP COLUMN last_play_ping_at")

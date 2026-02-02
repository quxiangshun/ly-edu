# -*- coding: utf-8 -*-
"""Ensure ly_user_video_progress exists (Flyway V6). Revision: v6, Revises: v5."""
from typing import Sequence, Union
from alembic import op

revision: str = "v6"
down_revision: Union[str, None] = "v5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SQL = (
    "CREATE TABLE IF NOT EXISTS ly_user_video_progress ("
    "id BIGINT NOT NULL AUTO_INCREMENT, user_id BIGINT NOT NULL, video_id BIGINT NOT NULL, "
    "progress INT DEFAULT 0, duration INT DEFAULT 0, is_finished TINYINT DEFAULT 0, "
    "create_time DATETIME DEFAULT CURRENT_TIMESTAMP, update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
    "PRIMARY KEY (id), UNIQUE KEY uk_user_video (user_id, video_id), "
    "KEY idx_user_id (user_id), KEY idx_video_id (video_id)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户视频学习进度表'"
)

def upgrade() -> None:
    op.execute(_SQL)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_user_video_progress")

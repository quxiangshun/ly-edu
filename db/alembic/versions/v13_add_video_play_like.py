# -*- coding: utf-8 -*-
"""视频播放次数、点赞：play_count/like_count + ly_video_like（与 Flyway V14 对应）

Revision ID: v13
Revises: v12
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v13"
down_revision: Union[str, None] = "v12"
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
    if not _column_exists(conn, "ly_video", "play_count"):
        op.execute(
            "ALTER TABLE ly_video ADD COLUMN play_count INT NOT NULL DEFAULT 0 COMMENT '播放次数' AFTER sort"
        )
    if not _column_exists(conn, "ly_video", "like_count"):
        op.execute(
            "ALTER TABLE ly_video ADD COLUMN like_count INT NOT NULL DEFAULT 0 COMMENT '点赞数' AFTER play_count"
        )
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_video_like (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL COMMENT '用户ID',
            video_id BIGINT NOT NULL COMMENT '视频ID',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_video (user_id, video_id),
            KEY idx_video_id (video_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频点赞'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_video_like")
    op.execute("ALTER TABLE ly_video DROP COLUMN like_count")
    op.execute("ALTER TABLE ly_video DROP COLUMN play_count")

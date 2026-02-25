# -*- coding: utf-8 -*-
"""课程表新增 play_count、like_count、comment_count（视频播放/点赞总和，课程评论数）

Revision ID: v4
Revises: v3
Create Date: 2025-02-24

课程存储其下所有视频的播放总和、点赞总和，以及课程评论数，用于综合排序/最多播放/最多点赞/最多评论。
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v4"
down_revision: Union[str, None] = "v3"
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
    for col in ("play_count", "like_count", "comment_count"):
        if not _column_exists(conn, "ly_course", col):
            op.execute(
                f"ALTER TABLE ly_course ADD COLUMN {col} INT NOT NULL DEFAULT 0 "
                f"COMMENT '{'视频播放总和' if col == 'play_count' else '视频点赞总和' if col == 'like_count' else '课程评论数'}'"
            )
    # 回填：视频播放/点赞总和
    op.execute("""
        UPDATE ly_course c SET
            c.play_count = COALESCE((SELECT SUM(v.play_count) FROM ly_video v WHERE v.course_id = c.id AND v.deleted = 0), 0),
            c.like_count = COALESCE((SELECT SUM(v.like_count) FROM ly_video v WHERE v.course_id = c.id AND v.deleted = 0), 0)
        WHERE c.deleted = 0
    """)
    # 回填：课程评论数
    op.execute("""
        UPDATE ly_course c SET
            c.comment_count = COALESCE((SELECT COUNT(*) FROM ly_course_comment cc WHERE cc.course_id = c.id AND cc.deleted = 0 AND (cc.status IS NULL OR cc.status = 1)), 0)
        WHERE c.deleted = 0
    """)


def downgrade() -> None:
    conn = op.get_bind()
    for col in ("play_count", "like_count", "comment_count"):
        if _column_exists(conn, "ly_course", col):
            op.execute(f"ALTER TABLE ly_course DROP COLUMN {col}")

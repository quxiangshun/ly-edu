# -*- coding: utf-8 -*-
"""课程-视频、部门-视频多对多关联表

Revision ID: v14
Revises: v13
Create Date: 2025-02-05

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v14"
down_revision: Union[str, None] = "v13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_video (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            course_id BIGINT NOT NULL COMMENT '课程ID',
            video_id BIGINT NOT NULL COMMENT '视频ID',
            chapter_id BIGINT DEFAULT NULL COMMENT '章节ID（该课程下）',
            sort INT DEFAULT 0 COMMENT '排序',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_video (course_id, video_id),
            KEY idx_course_id (course_id),
            KEY idx_video_id (video_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-视频关联（多对多）'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_department_video (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            department_id BIGINT NOT NULL COMMENT '部门ID',
            video_id BIGINT NOT NULL COMMENT '视频ID',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_department_video (department_id, video_id),
            KEY idx_department_id (department_id),
            KEY idx_video_id (video_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门-视频关联（多对多）'
    """)
    op.execute("""
        INSERT IGNORE INTO ly_course_video (course_id, video_id, chapter_id, sort)
        SELECT course_id, id, chapter_id, sort FROM ly_video WHERE deleted = 0
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_department_video")
    op.execute("DROP TABLE IF EXISTS ly_course_video")

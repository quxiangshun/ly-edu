# -*- coding: utf-8 -*-
"""标签表及用户/部门/课程关联

Revision ID: v2
Revises: v1
Create Date: 2025-02-06

"""
from typing import Sequence, Union

from alembic import op

revision: str = "v2"
down_revision: Union[str, None] = "v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_tag (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            name VARCHAR(50) NOT NULL COMMENT '标签名称',
            sort INT DEFAULT 0 COMMENT '排序',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            PRIMARY KEY (id),
            UNIQUE KEY uk_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_tag (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            user_id BIGINT NOT NULL COMMENT '用户ID',
            tag_id BIGINT NOT NULL COMMENT '标签ID',
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_tag (user_id, tag_id),
            KEY idx_user_id (user_id),
            KEY idx_tag_id (tag_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户-标签关联'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_department_tag (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            department_id BIGINT NOT NULL COMMENT '部门ID',
            tag_id BIGINT NOT NULL COMMENT '标签ID',
            PRIMARY KEY (id),
            UNIQUE KEY uk_department_tag (department_id, tag_id),
            KEY idx_department_id (department_id),
            KEY idx_tag_id (tag_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门-标签关联'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_tag (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            course_id BIGINT NOT NULL COMMENT '课程ID',
            tag_id BIGINT NOT NULL COMMENT '标签ID',
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_tag (course_id, tag_id),
            KEY idx_course_id (course_id),
            KEY idx_tag_id (tag_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-标签关联'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_course_tag")
    op.execute("DROP TABLE IF EXISTS ly_department_tag")
    op.execute("DROP TABLE IF EXISTS ly_user_tag")
    op.execute("DROP TABLE IF EXISTS ly_tag")

# -*- coding: utf-8 -*-
"""初始化基础表结构（对应 Flyway V1__init_schema.sql）

Revision ID: v1
Revises:
Create Date: 2025-01-28

对应 Flyway: V1__init_schema.sql
"""
from typing import Sequence, Union

from alembic import op


revision: str = "v1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            username VARCHAR(50) NOT NULL COMMENT '用户名',
            password VARCHAR(255) NOT NULL COMMENT '密码',
            real_name VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
            email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
            mobile VARCHAR(20) DEFAULT NULL COMMENT '手机号',
            avatar VARCHAR(255) DEFAULT NULL COMMENT '头像',
            department_id BIGINT DEFAULT NULL COMMENT '部门ID',
            role VARCHAR(20) DEFAULT 'student' COMMENT '角色',
            status TINYINT DEFAULT 1 COMMENT '状态',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            UNIQUE KEY uk_username (username),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_department (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            parent_id BIGINT DEFAULT 0,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_parent_id (parent_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_category (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            parent_id BIGINT DEFAULT 0,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_parent_id (parent_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程分类表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course (
            id BIGINT NOT NULL AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            cover VARCHAR(255) DEFAULT NULL,
            description TEXT,
            category_id BIGINT DEFAULT NULL,
            status TINYINT DEFAULT 1,
            sort INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_category_id (category_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_chapter (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            title VARCHAR(200) NOT NULL,
            sort INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_course_id (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程章节表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_video (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            chapter_id BIGINT DEFAULT NULL,
            title VARCHAR(200) NOT NULL,
            url VARCHAR(500) NOT NULL,
            duration INT DEFAULT 0,
            sort INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_course_id (course_id),
            KEY idx_chapter_id (chapter_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_course (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            course_id BIGINT NOT NULL,
            progress INT DEFAULT 0,
            status TINYINT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_course (user_id, course_id),
            KEY idx_user_id (user_id),
            KEY idx_course_id (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户课程关联表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_video_progress (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            video_id BIGINT NOT NULL,
            progress INT DEFAULT 0,
            duration INT DEFAULT 0,
            is_finished TINYINT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_video (user_id, video_id),
            KEY idx_user_id (user_id),
            KEY idx_video_id (video_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户视频学习进度表'
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_user_video_progress")
    op.execute("DROP TABLE IF EXISTS ly_user_course")
    op.execute("DROP TABLE IF EXISTS ly_video")
    op.execute("DROP TABLE IF EXISTS ly_course_chapter")
    op.execute("DROP TABLE IF EXISTS ly_course")
    op.execute("DROP TABLE IF EXISTS ly_course_category")
    op.execute("DROP TABLE IF EXISTS ly_department")
    op.execute("DROP TABLE IF EXISTS ly_user")

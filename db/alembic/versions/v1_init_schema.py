# -*- coding: utf-8 -*-
"""完整初始化（合并原 v1～v13，与 Flyway V1 一致）

Revision ID: v1
Revises:
Create Date: 2025-01-28
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
            is_required TINYINT DEFAULT 0 COMMENT '是否必修',
            visibility TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_category_id (category_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_department (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            department_id BIGINT NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_department (course_id, department_id),
            KEY idx_course_id (course_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-部门关联表'
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
        CREATE TABLE IF NOT EXISTS ly_course_attachment (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            name VARCHAR(200) NOT NULL,
            type VARCHAR(50) DEFAULT NULL,
            file_url VARCHAR(500) NOT NULL,
            sort INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_course_id (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程附件表'
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
            last_play_ping_at DATETIME NULL COMMENT '最近播放心跳时间',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_video (user_id, video_id),
            KEY idx_user_id (user_id),
            KEY idx_video_id (video_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户视频学习进度表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_upload (
            id BIGINT NOT NULL AUTO_INCREMENT,
            file_id VARCHAR(64) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_size BIGINT NOT NULL,
            file_type VARCHAR(50) DEFAULT NULL,
            chunk_size BIGINT NOT NULL,
            total_chunks INT NOT NULL,
            uploaded_chunks INT DEFAULT 0,
            upload_path VARCHAR(500) DEFAULT NULL,
            status TINYINT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_file_id (file_id),
            KEY idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传进度表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_chunk (
            id BIGINT NOT NULL AUTO_INCREMENT,
            file_id VARCHAR(64) NOT NULL,
            chunk_index INT NOT NULL,
            chunk_size BIGINT NOT NULL,
            chunk_path VARCHAR(500) NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_file_chunk (file_id, chunk_index),
            KEY idx_file_id (file_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件分片上传记录表'
    """)
    op.execute("""
        INSERT INTO ly_user (username, password, real_name, email, role, status)
        VALUES ('admin', '$2a$10$YORpsv2uYZQNNt5hxVNrw.KyeVMcn.fjWYyX3CWGXSwdpL6hRpVSy', '管理员', 'admin@lyedu.com', 'admin', 1)
        ON DUPLICATE KEY UPDATE password = VALUES(password), real_name = VALUES(real_name)
    """)
    op.execute("""
        INSERT INTO ly_department (name, parent_id, sort, status) VALUES
        ('技术部', 0, 1, 1),
        ('产品部', 0, 2, 1),
        ('运营部', 0, 3, 1)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
    """)
    op.execute("""
        INSERT INTO ly_course (title, cover, description, status, sort) VALUES
        ('Java 基础教程', 'https://via.placeholder.com/300x200?text=Java', 'Java 编程语言基础入门课程，适合零基础学员', 1, 1),
        ('Vue3 前端开发', 'https://via.placeholder.com/300x200?text=Vue3', 'Vue3 框架学习，包含组合式 API 和 TypeScript', 1, 2),
        ('SpringBoot 实战', 'https://via.placeholder.com/300x200?text=SpringBoot', 'SpringBoot 企业级应用开发实战', 1, 3),
        ('MySQL 数据库', 'https://via.placeholder.com/300x200?text=MySQL', 'MySQL 数据库设计与优化', 1, 4),
        ('Docker 容器化', 'https://via.placeholder.com/300x200?text=Docker', 'Docker 容器化部署实践', 1, 5),
        ('Linux 系统管理', 'https://via.placeholder.com/300x200?text=Linux', 'Linux 系统管理与运维', 1, 6)
        ON DUPLICATE KEY UPDATE title = VALUES(title)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM ly_course WHERE title IN ('Java 基础教程', 'Vue3 前端开发', 'SpringBoot 实战', 'MySQL 数据库', 'Docker 容器化', 'Linux 系统管理')")
    op.execute("DELETE FROM ly_department WHERE name IN ('技术部', '产品部', '运营部')")
    op.execute("DELETE FROM ly_user WHERE username = 'admin'")
    op.execute("DROP TABLE IF EXISTS ly_file_chunk")
    op.execute("DROP TABLE IF EXISTS ly_file_upload")
    op.execute("DROP TABLE IF EXISTS ly_user_video_progress")
    op.execute("DROP TABLE IF EXISTS ly_user_course")
    op.execute("DROP TABLE IF EXISTS ly_video")
    op.execute("DROP TABLE IF EXISTS ly_course_attachment")
    op.execute("DROP TABLE IF EXISTS ly_course_chapter")
    op.execute("DROP TABLE IF EXISTS ly_course_department")
    op.execute("DROP TABLE IF EXISTS ly_course")
    op.execute("DROP TABLE IF EXISTS ly_course_category")
    op.execute("DROP TABLE IF EXISTS ly_department")
    op.execute("DROP TABLE IF EXISTS ly_user")

# -*- coding: utf-8 -*-
"""完整初始化

Revision ID: v1
Revises:
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table: str, column: str) -> bool:
    """检查列是否存在"""
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c LIMIT 1"
        ),
        {"t": table, "c": column},
    )
    return r.scalar() is not None


def upgrade() -> None:
    # ----- 用户表（含 feishu_open_id、union_id、entry_date、total_points）-----
    conn = op.get_bind()
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            username VARCHAR(50) NOT NULL COMMENT '用户名',
            password VARCHAR(255) NOT NULL COMMENT '密码',
            real_name VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
            email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
            mobile VARCHAR(20) DEFAULT NULL COMMENT '手机号',
            avatar VARCHAR(255) DEFAULT NULL COMMENT '头像',
            feishu_open_id VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id，用于飞书扫码登录',
            union_id VARCHAR(64) DEFAULT NULL COMMENT '开放平台 union_id，同一主体下多应用（飞书/小程序等）统一',
            department_id BIGINT DEFAULT NULL COMMENT '部门ID',
            entry_date DATE DEFAULT NULL COMMENT '入职日期',
            total_points INT DEFAULT 0 COMMENT '累计积分',
            role VARCHAR(20) DEFAULT 'student' COMMENT '角色',
            status TINYINT DEFAULT 1 COMMENT '状态',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            UNIQUE KEY uk_username (username),
            UNIQUE KEY uk_feishu_open_id (feishu_open_id),
            KEY idx_union_id (union_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表'
    """)
    # 如果表已存在但缺少字段，则添加（兼容旧表结构）
    # 若有 open_id 旧列，统一改为 feishu_open_id
    if _column_exists(conn, "ly_user", "open_id"):
        try:
            op.execute("ALTER TABLE ly_user DROP KEY uk_open_id")
        except Exception:
            pass
        op.execute("ALTER TABLE ly_user CHANGE COLUMN open_id feishu_open_id VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id，用于飞书扫码登录'")
        op.execute("ALTER TABLE ly_user ADD UNIQUE KEY uk_feishu_open_id (feishu_open_id)")
    elif not _column_exists(conn, "ly_user", "feishu_open_id"):
        op.execute("ALTER TABLE ly_user ADD COLUMN feishu_open_id VARCHAR(64) DEFAULT NULL COMMENT '飞书 open_id，用于飞书扫码登录' AFTER avatar")
        op.execute("ALTER TABLE ly_user ADD UNIQUE KEY uk_feishu_open_id (feishu_open_id)")
    if not _column_exists(conn, "ly_user", "union_id"):
        op.execute("ALTER TABLE ly_user ADD COLUMN union_id VARCHAR(64) DEFAULT NULL COMMENT '开放平台 union_id，同一主体下多应用统一' AFTER feishu_open_id")
        op.execute("ALTER TABLE ly_user ADD KEY idx_union_id (union_id)")
    if not _column_exists(conn, "ly_user", "entry_date"):
        op.execute("ALTER TABLE ly_user ADD COLUMN entry_date DATE DEFAULT NULL COMMENT '入职日期' AFTER department_id")
    if not _column_exists(conn, "ly_user", "total_points"):
        op.execute("ALTER TABLE ly_user ADD COLUMN total_points INT DEFAULT 0 COMMENT '累计积分' AFTER entry_date")
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
    # ----- 视频表（含 v12 cover、v13 play_count/like_count）-----
    conn = op.get_bind()
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_video (
            id BIGINT NOT NULL AUTO_INCREMENT,
            course_id BIGINT NOT NULL,
            chapter_id BIGINT DEFAULT NULL,
            title VARCHAR(200) NOT NULL,
            url VARCHAR(500) NOT NULL,
            cover VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL',
            duration INT DEFAULT 0,
            sort INT DEFAULT 0,
            play_count INT NOT NULL DEFAULT 0 COMMENT '播放次数',
            like_count INT NOT NULL DEFAULT 0 COMMENT '点赞数',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_course_id (course_id),
            KEY idx_chapter_id (chapter_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频表'
    """)
    # 如果表已存在但缺少字段，则添加（兼容旧表结构）
    if not _column_exists(conn, "ly_video", "cover"):
        op.execute("ALTER TABLE ly_video ADD COLUMN cover VARCHAR(500) DEFAULT NULL COMMENT '视频封面URL' AFTER url")
    if not _column_exists(conn, "ly_video", "play_count"):
        op.execute("ALTER TABLE ly_video ADD COLUMN play_count INT NOT NULL DEFAULT 0 COMMENT '播放次数' AFTER sort")
    if not _column_exists(conn, "ly_video", "like_count"):
        op.execute("ALTER TABLE ly_video ADD COLUMN like_count INT NOT NULL DEFAULT 0 COMMENT '点赞数' AFTER play_count")
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
    # 如果表已存在但缺少字段，则添加（兼容旧表结构）
    # 检查是否有旧的 file_path 字段需要重命名或删除
    if _column_exists(conn, "ly_file_upload", "file_path"):
        # 如果存在 file_path 但没有 upload_path，重命名
        if not _column_exists(conn, "ly_file_upload", "upload_path"):
            try:
                op.execute("ALTER TABLE ly_file_upload MODIFY COLUMN file_path VARCHAR(500) DEFAULT NULL")
            except:
                pass
            op.execute("ALTER TABLE ly_file_upload CHANGE COLUMN file_path upload_path VARCHAR(500) DEFAULT NULL")
        else:
            # 如果两个字段都存在，删除旧的 file_path
            op.execute("ALTER TABLE ly_file_upload DROP COLUMN file_path")
    if not _column_exists(conn, "ly_file_upload", "file_type"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN file_type VARCHAR(50) DEFAULT NULL AFTER file_size")
    if not _column_exists(conn, "ly_file_upload", "chunk_size"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN chunk_size BIGINT NOT NULL DEFAULT 5242880 AFTER file_type")
    if not _column_exists(conn, "ly_file_upload", "total_chunks"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN total_chunks INT NOT NULL DEFAULT 1 AFTER chunk_size")
    if not _column_exists(conn, "ly_file_upload", "uploaded_chunks"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN uploaded_chunks INT DEFAULT 0 AFTER total_chunks")
    if not _column_exists(conn, "ly_file_upload", "upload_path"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN upload_path VARCHAR(500) DEFAULT NULL AFTER uploaded_chunks")
    if not _column_exists(conn, "ly_file_upload", "status"):
        op.execute("ALTER TABLE ly_file_upload ADD COLUMN status TINYINT DEFAULT 0 AFTER upload_path")
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
    # 如果表已存在但缺少字段，则添加（兼容旧表结构）
    # 检查是否有旧的 file_path 字段需要重命名（先修改为允许 NULL，再重命名，最后改回 NOT NULL）
    if _column_exists(conn, "ly_file_chunk", "file_path") and not _column_exists(conn, "ly_file_chunk", "chunk_path"):
        # 先修改为允许 NULL 并设置默认值，避免重命名时 NOT NULL 约束问题
        try:
            op.execute("ALTER TABLE ly_file_chunk MODIFY COLUMN file_path VARCHAR(500) DEFAULT ''")
        except:
            pass
        op.execute("ALTER TABLE ly_file_chunk CHANGE COLUMN file_path chunk_path VARCHAR(500) NOT NULL DEFAULT ''")
    elif not _column_exists(conn, "ly_file_chunk", "chunk_path"):
        op.execute("ALTER TABLE ly_file_chunk ADD COLUMN chunk_path VARCHAR(500) NOT NULL DEFAULT '' AFTER chunk_size")
    if not _column_exists(conn, "ly_file_chunk", "chunk_size"):
        op.execute("ALTER TABLE ly_file_chunk ADD COLUMN chunk_size BIGINT NOT NULL DEFAULT 0 AFTER chunk_index")
    # ----- v3 课程评论 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_comment (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            course_id BIGINT NOT NULL COMMENT '课程ID',
            chapter_id BIGINT DEFAULT NULL COMMENT '章节ID，NULL表示课程级评论',
            user_id BIGINT NOT NULL COMMENT '评论用户ID',
            parent_id BIGINT DEFAULT NULL COMMENT '父评论ID，NULL表示一级评论',
            content TEXT NOT NULL COMMENT '评论内容',
            status TINYINT DEFAULT 1 COMMENT '状态：0-隐藏，1-正常',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_course_id (course_id),
            KEY idx_chapter_id (chapter_id),
            KEY idx_user_id (user_id),
            KEY idx_parent_id (parent_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程评论表'
    """)
    # ----- v4 知识库 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_knowledge (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            title VARCHAR(200) NOT NULL COMMENT '标题/名称',
            category VARCHAR(100) DEFAULT NULL COMMENT '分类',
            file_name VARCHAR(255) DEFAULT NULL COMMENT '文件名',
            file_url VARCHAR(500) NOT NULL COMMENT '文件地址',
            file_size BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
            file_type VARCHAR(50) DEFAULT NULL COMMENT '文件类型/扩展名',
            sort INT DEFAULT 0 COMMENT '排序',
            visibility TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_category (category),
            KEY idx_sort (sort)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表'
    """)
    # 如果表已存在但缺少字段，则添加（兼容旧表结构）
    if not _column_exists(conn, "ly_knowledge", "file_type"):
        op.execute("ALTER TABLE ly_knowledge ADD COLUMN file_type VARCHAR(50) DEFAULT NULL COMMENT '文件类型/扩展名' AFTER file_size")
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_knowledge_department (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            knowledge_id BIGINT NOT NULL COMMENT '知识ID',
            department_id BIGINT NOT NULL COMMENT '部门ID',
            PRIMARY KEY (id),
            UNIQUE KEY uk_knowledge_department (knowledge_id, department_id),
            KEY idx_knowledge_id (knowledge_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库-部门关联表'
    """)
    # ----- v5 考试 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_question (
            id BIGINT NOT NULL AUTO_INCREMENT,
            type VARCHAR(20) NOT NULL,
            title TEXT NOT NULL,
            options JSON DEFAULT NULL,
            answer TEXT DEFAULT NULL,
            score INT DEFAULT 10,
            analysis TEXT DEFAULT NULL,
            sort INT DEFAULT 0,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_type (type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试题表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_paper (
            id BIGINT NOT NULL AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            total_score INT DEFAULT 100,
            pass_score INT DEFAULT 60,
            duration_minutes INT DEFAULT 60,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_paper_question (
            id BIGINT NOT NULL AUTO_INCREMENT,
            paper_id BIGINT NOT NULL,
            question_id BIGINT NOT NULL,
            score INT DEFAULT 10,
            sort INT DEFAULT 0,
            PRIMARY KEY (id),
            UNIQUE KEY uk_paper_question (paper_id, question_id),
            KEY idx_paper_id (paper_id),
            KEY idx_question_id (question_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷-试题关联表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_exam (
            id BIGINT NOT NULL AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            paper_id BIGINT NOT NULL,
            start_time DATETIME DEFAULT NULL,
            end_time DATETIME DEFAULT NULL,
            duration_minutes INT DEFAULT 60,
            pass_score INT DEFAULT NULL,
            visibility TINYINT DEFAULT 1,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_paper_id (paper_id),
            KEY idx_start_time (start_time),
            KEY idx_end_time (end_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试任务表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_exam_department (
            id BIGINT NOT NULL AUTO_INCREMENT,
            exam_id BIGINT NOT NULL,
            department_id BIGINT NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uk_exam_department (exam_id, department_id),
            KEY idx_exam_id (exam_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试-部门关联表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_exam_record (
            id BIGINT NOT NULL AUTO_INCREMENT,
            exam_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            paper_id BIGINT NOT NULL,
            score INT DEFAULT NULL,
            passed TINYINT DEFAULT NULL,
            answers JSON DEFAULT NULL,
            submit_time DATETIME DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_exam_id (exam_id),
            KEY idx_user_id (user_id),
            KEY idx_exam_user (exam_id, user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试记录表'
    """)
    # ----- v6 证书 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_certificate_template (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500) DEFAULT NULL,
            config TEXT DEFAULT NULL,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书模板表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_certificate (
            id BIGINT NOT NULL AUTO_INCREMENT,
            template_id BIGINT NOT NULL,
            name VARCHAR(200) NOT NULL,
            source_type VARCHAR(20) NOT NULL,
            source_id BIGINT NOT NULL,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_template_id (template_id),
            KEY idx_source (source_type, source_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书颁发规则表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_certificate (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            certificate_id BIGINT NOT NULL,
            template_id BIGINT NOT NULL,
            certificate_no VARCHAR(64) NOT NULL,
            title VARCHAR(200) NOT NULL,
            issued_at DATETIME NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_certificate_no (certificate_no),
            KEY idx_user_id (user_id),
            KEY idx_certificate_id (certificate_id),
            KEY idx_template_id (template_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户已获证书表'
    """)
    # ----- v7 任务 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_task (
            id BIGINT NOT NULL AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT DEFAULT NULL,
            cycle_type VARCHAR(20) NOT NULL DEFAULT 'once',
            cycle_config JSON DEFAULT NULL,
            items JSON NOT NULL,
            certificate_id BIGINT DEFAULT NULL,
            sort INT DEFAULT 0,
            status TINYINT DEFAULT 1,
            start_time DATETIME DEFAULT NULL,
            end_time DATETIME DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted TINYINT DEFAULT 0,
            PRIMARY KEY (id),
            KEY idx_status (status),
            KEY idx_certificate_id (certificate_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='周期任务表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_task_department (
            id BIGINT NOT NULL AUTO_INCREMENT,
            task_id BIGINT NOT NULL,
            department_id BIGINT NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_task_department (task_id, department_id),
            KEY idx_task_id (task_id),
            KEY idx_department_id (department_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务-部门关联表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_user_task (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            task_id BIGINT NOT NULL,
            progress JSON DEFAULT NULL,
            status TINYINT NOT NULL DEFAULT 0,
            completed_at DATETIME DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_user_task (user_id, task_id),
            KEY idx_user_id (user_id),
            KEY idx_task_id (task_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户任务进度表'
    """)
    # ----- v8 系统配置 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_config (
            id BIGINT NOT NULL AUTO_INCREMENT,
            config_key VARCHAR(100) NOT NULL,
            config_value TEXT DEFAULT NULL,
            category VARCHAR(50) DEFAULT 'site',
            remark VARCHAR(200) DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_config_key (config_key),
            KEY idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表'
    """)
    # ----- v9 积分 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_point_rule (
            id BIGINT NOT NULL AUTO_INCREMENT,
            rule_key VARCHAR(50) NOT NULL COMMENT '规则键：course_finish, exam_pass, task_finish',
            rule_name VARCHAR(100) DEFAULT NULL COMMENT '规则名称',
            points INT NOT NULL DEFAULT 0 COMMENT '奖励积分',
            enabled TINYINT DEFAULT 1 COMMENT '是否启用：0-否，1-是',
            remark VARCHAR(200) DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_rule_key (rule_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分规则表'
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_point_log (
            id BIGINT NOT NULL AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            points INT NOT NULL COMMENT '本次变动积分（正数）',
            rule_key VARCHAR(50) NOT NULL,
            ref_type VARCHAR(30) DEFAULT NULL COMMENT '关联类型：course, exam, task',
            ref_id BIGINT DEFAULT NULL COMMENT '关联ID',
            remark VARCHAR(200) DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_user_id (user_id),
            KEY idx_ref (ref_type, ref_id),
            KEY idx_create_time (create_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分流水表'
    """)
    # ----- v10 图片库 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_image (
            id BIGINT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL COMMENT '原始文件名',
            path VARCHAR(500) NOT NULL COMMENT '相对路径，如 2025/01/xxx.jpg',
            file_size BIGINT DEFAULT 0 COMMENT '文件大小（字节）',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_create_time (create_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图片库'
    """)
    # ----- v12 文件哈希 + 已在 ly_video 中含 cover -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_file_hash (
            id BIGINT NOT NULL AUTO_INCREMENT,
            content_hash VARCHAR(64) NOT NULL COMMENT '文件内容 SHA-256 十六进制',
            relative_path VARCHAR(500) NOT NULL COMMENT '相对路径，如 videos/xxx/file.mp4',
            file_size BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小（字节）',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_content_hash (content_hash),
            KEY idx_content_hash (content_hash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件内容哈希表，用于视频去重'
    """)
    # ----- v13 视频点赞 -----
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
    # ----- v14 课程-视频（不含 ly_department_video，v15 已弃用）-----
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
    # ----- v16 课程-考试 -----
    op.execute("""
        CREATE TABLE IF NOT EXISTS ly_course_exam (
            id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
            course_id BIGINT NOT NULL COMMENT '课程ID',
            exam_id BIGINT NOT NULL COMMENT '考试ID',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uk_course_exam (course_id),
            KEY idx_exam_id (exam_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程-考试关联（多课程可共用同一考试）'
    """)

    # ----- 种子数据（v1 + v8 + v9 + v11）-----
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
    op.execute("""
        INSERT INTO ly_config (config_key, config_value, category, remark) VALUES
        ('site.title', 'LyEdu 学习平台', 'site', '网站标题'),
        ('site.keywords', '在线学习,培训', 'site', 'SEO关键词'),
        ('site.description', '企业在线学习与培训平台', 'site', '网站描述'),
        ('player.allow_download', '0', 'player', '是否允许下载'),
        ('student.default_page_size', '20', 'student', '学员端每页条数'),
        ('player.disable_seek', '0', 'player', '禁止拖拽进度条：0-允许，1-禁止'),
        ('player.disable_speed', '0', 'player', '禁止倍速播放：0-允许，1-禁止')
        ON DUPLICATE KEY UPDATE config_value = VALUES(config_value), remark = VALUES(remark)
    """)
    op.execute("""
        INSERT INTO ly_point_rule (rule_key, rule_name, points, enabled, remark) VALUES
        ('course_finish', '完成课程', 10, 1, '学习进度达到100%'),
        ('exam_pass', '考试合格', 20, 1, '考试通过'),
        ('task_finish', '完成任务', 30, 1, '周期/新员工任务全部闯关完成')
        ON DUPLICATE KEY UPDATE rule_name = VALUES(rule_name), points = VALUES(points), enabled = VALUES(enabled), remark = VALUES(remark)
    """)
    op.execute("""
        INSERT IGNORE INTO ly_course_video (course_id, video_id, chapter_id, sort)
        SELECT course_id, id, chapter_id, sort FROM ly_video WHERE deleted = 0
    """)


def downgrade() -> None:
    op.execute("DELETE FROM ly_course WHERE title IN ('Java 基础教程', 'Vue3 前端开发', 'SpringBoot 实战', 'MySQL 数据库', 'Docker 容器化', 'Linux 系统管理')")
    op.execute("DELETE FROM ly_department WHERE name IN ('技术部', '产品部', '运营部')")
    op.execute("DELETE FROM ly_user WHERE username = 'admin'")
    op.execute("DELETE FROM ly_config WHERE config_key IN ('site.title','site.keywords','site.description','player.allow_download','student.default_page_size','player.disable_seek','player.disable_speed')")
    op.execute("DELETE FROM ly_point_rule WHERE rule_key IN ('course_finish','exam_pass','task_finish')")
    op.execute("DROP TABLE IF EXISTS ly_course_exam")
    op.execute("DROP TABLE IF EXISTS ly_course_video")
    op.execute("DROP TABLE IF EXISTS ly_video_like")
    op.execute("DROP TABLE IF EXISTS ly_file_hash")
    op.execute("DROP TABLE IF EXISTS ly_image")
    op.execute("DROP TABLE IF EXISTS ly_point_log")
    op.execute("DROP TABLE IF EXISTS ly_point_rule")
    op.execute("DROP TABLE IF EXISTS ly_config")
    op.execute("DROP TABLE IF EXISTS ly_user_task")
    op.execute("DROP TABLE IF EXISTS ly_task_department")
    op.execute("DROP TABLE IF EXISTS ly_task")
    op.execute("DROP TABLE IF EXISTS ly_user_certificate")
    op.execute("DROP TABLE IF EXISTS ly_certificate")
    op.execute("DROP TABLE IF EXISTS ly_certificate_template")
    op.execute("DROP TABLE IF EXISTS ly_exam_record")
    op.execute("DROP TABLE IF EXISTS ly_exam_department")
    op.execute("DROP TABLE IF EXISTS ly_exam")
    op.execute("DROP TABLE IF EXISTS ly_paper_question")
    op.execute("DROP TABLE IF EXISTS ly_paper")
    op.execute("DROP TABLE IF EXISTS ly_question")
    op.execute("DROP TABLE IF EXISTS ly_knowledge_department")
    op.execute("DROP TABLE IF EXISTS ly_knowledge")
    op.execute("DROP TABLE IF EXISTS ly_course_comment")
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

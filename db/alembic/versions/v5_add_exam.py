# -*- coding: utf-8 -*-
"""考试中心表（试题、试卷、考试、考试记录，与 Flyway V5 一致）

Revision ID: v5
Revises: v4
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v5"
down_revision: Union[str, None] = "v4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_exam_record")
    op.execute("DROP TABLE IF EXISTS ly_exam_department")
    op.execute("DROP TABLE IF EXISTS ly_exam")
    op.execute("DROP TABLE IF EXISTS ly_paper_question")
    op.execute("DROP TABLE IF EXISTS ly_paper")
    op.execute("DROP TABLE IF EXISTS ly_question")

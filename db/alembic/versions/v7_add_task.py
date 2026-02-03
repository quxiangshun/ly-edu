# -*- coding: utf-8 -*-
"""周期任务相关表（与 Flyway V7 一致）

Revision ID: v7
Revises: v6
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v7"
down_revision: Union[str, None] = "v6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_user_task")
    op.execute("DROP TABLE IF EXISTS ly_task_department")
    op.execute("DROP TABLE IF EXISTS ly_task")

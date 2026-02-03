# -*- coding: utf-8 -*-
"""知识库及知识库-部门关联表（与 Flyway V4 一致）

Revision ID: v4
Revises: v3
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v4"
down_revision: Union[str, None] = "v3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_knowledge_department")
    op.execute("DROP TABLE IF EXISTS ly_knowledge")

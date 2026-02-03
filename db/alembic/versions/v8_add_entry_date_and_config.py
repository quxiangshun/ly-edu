# -*- coding: utf-8 -*-
"""用户入职日期 + 系统配置表（与 Flyway V8 一致）

Revision ID: v8
Revises: v7
Create Date: 2025-01-28

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v8"
down_revision: Union[str, None] = "v7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE ly_user ADD COLUMN entry_date DATE DEFAULT NULL COMMENT '入职日期' AFTER department_id")
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
    op.execute("""
        INSERT INTO ly_config (config_key, config_value, category, remark) VALUES
        ('site.title', 'LyEdu 学习平台', 'site', '网站标题'),
        ('site.keywords', '在线学习,培训', 'site', 'SEO关键词'),
        ('site.description', '企业在线学习与培训平台', 'site', '网站描述'),
        ('player.allow_download', '0', 'player', '是否允许下载'),
        ('student.default_page_size', '20', 'student', '学员端列表每页条数')
        ON DUPLICATE KEY UPDATE config_value = VALUES(config_value)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM ly_config WHERE config_key IN ('site.title','site.keywords','site.description','player.allow_download','student.default_page_size')")
    op.execute("DROP TABLE IF EXISTS ly_config")
    op.execute("ALTER TABLE ly_user DROP COLUMN entry_date")

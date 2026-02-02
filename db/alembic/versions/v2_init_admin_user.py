# -*- coding: utf-8 -*-
"""初始化管理员账号（对应 Flyway V2__init_admin_user.sql）

Revision ID: v2
Revises: v1
Create Date: 2025-01-28
"""
from typing import Sequence, Union
from alembic import op

revision: str = "v2"
down_revision: Union[str, None] = "v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "INSERT INTO ly_user (username, password, real_name, email, role, status) "
        "VALUES ('admin', '$2a$10$YORpsv2uYZQNNt5hxVNrw.KyeVMcn.fjWYyX3CWGXSwdpL6hRpVSy', "
        "'管理员', 'admin@lyedu.com', 'admin', 1) "
        "ON DUPLICATE KEY UPDATE password = VALUES(password), real_name = VALUES(real_name)"
    )

def downgrade() -> None:
    op.execute("DELETE FROM ly_user WHERE username = 'admin'")

# -*- coding: utf-8 -*-
"""Fix video titles (Flyway V5). Revision: v5, Revises: v4."""
from typing import Sequence, Union
from alembic import op

revision: str = "v5"
down_revision: Union[str, None] = "v4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("UPDATE ly_video SET title = 'Java基础入门视频1：环境搭建与第一个程序' WHERE id = 1")
    op.execute("UPDATE ly_video SET title = 'Java基础入门视频2：变量与数据类型' WHERE id = 2")
    op.execute("UPDATE ly_video SET title = 'Java基础入门视频3：控制流程与循环' WHERE id = 3")
    op.execute("UPDATE ly_video SET title = 'Vue3入门视频1：项目创建与组件' WHERE id = 4")
    op.execute("UPDATE ly_video SET title = 'Vue3入门视频2：响应式数据' WHERE id = 5")

def downgrade() -> None:
    pass

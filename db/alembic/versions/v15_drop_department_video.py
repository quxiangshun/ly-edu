# -*- coding: utf-8 -*-
"""移除部门-视频多对多关联表（需求变更）

Revision ID: v15
Revises: v14
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op


revision: str = "v15"
down_revision: Union[str, None] = "v14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_department_video")


def downgrade() -> None:
    # 不再重建该表
    pass

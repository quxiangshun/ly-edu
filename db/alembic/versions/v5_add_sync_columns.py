# -*- coding: utf-8 -*-
"""为 fa->ly 同步脚本增加字段（ly_user nickname/last_login_time/study_time_long, ly_video description）

Revision ID: v5
Revises: v4
Create Date: 2025-02-06

"""
from typing import Sequence, Union

from alembic import op

revision: str = "v5"
down_revision: Union[str, None] = "v4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE ly_user ADD COLUMN nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称（同步自 fa_staff.name）' AFTER real_name")
    op.execute("ALTER TABLE ly_user ADD COLUMN last_login_time DATETIME DEFAULT NULL COMMENT '最后登录时间（同步自 fa_staff）' AFTER union_id")
    op.execute("ALTER TABLE ly_user ADD COLUMN study_time_long INT DEFAULT 0 COMMENT '学习时长（分钟）（同步自 fa_staff）' AFTER total_points")
    op.execute("ALTER TABLE ly_video ADD COLUMN description TEXT DEFAULT NULL COMMENT '视频介绍（同步自 fa_video）' AFTER title")


def downgrade() -> None:
    op.execute("ALTER TABLE ly_user DROP COLUMN nickname, DROP COLUMN last_login_time, DROP COLUMN study_time_long")
    op.execute("ALTER TABLE ly_video DROP COLUMN description")

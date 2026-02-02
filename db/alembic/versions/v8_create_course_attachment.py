# -*- coding: utf-8 -*-
"""Create ly_course_attachment (Flyway V8). Revision: v8, Revises: v7."""
from typing import Sequence, Union
from alembic import op

revision: str = "v8"
down_revision: Union[str, None] = "v7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SQL = (
    "CREATE TABLE IF NOT EXISTS ly_course_attachment ("
    "id BIGINT NOT NULL AUTO_INCREMENT, course_id BIGINT NOT NULL, name VARCHAR(200) NOT NULL, "
    "type VARCHAR(50) DEFAULT NULL, file_url VARCHAR(500) NOT NULL, sort INT DEFAULT 0, "
    "create_time DATETIME DEFAULT CURRENT_TIMESTAMP, update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
    "deleted TINYINT DEFAULT 0, PRIMARY KEY (id), KEY idx_course_id (course_id)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程附件表'"
)

def upgrade() -> None:
    op.execute(_SQL)

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ly_course_attachment")

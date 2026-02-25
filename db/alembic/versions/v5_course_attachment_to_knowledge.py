# -*- coding: utf-8 -*-
"""课程-知识库中间表（多对多）

Revision ID: v5
Revises: v4
Create Date: 2025-02-24

将 ly_course_attachment 改为 ly_course_knowledge（课程与知识库中间表），
仅存储 course_id、knowledge_id、sort，文件属性从 ly_knowledge 获取。
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "v5"
down_revision: Union[str, None] = "v4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(conn, table: str, column: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c LIMIT 1"
        ),
        {"t": table, "c": column},
    )
    return r.scalar() is not None


def _table_exists(conn, table: str) -> bool:
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t LIMIT 1"
    ), {"t": table}).scalar()
    return bool(r)


def upgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "ly_course_knowledge"):
        return  # 已迁移完成
    if _column_exists(conn, "ly_course_attachment", "knowledge_id"):
        op.execute("RENAME TABLE ly_course_attachment TO ly_course_knowledge")
        return  # 已 alter 过，仅需重命名
    # 1. 添加 knowledge_id 列（可空）
    op.execute("""
        ALTER TABLE ly_course_attachment
        ADD COLUMN knowledge_id BIGINT DEFAULT NULL COMMENT '知识库ID（关联 ly_knowledge）' AFTER course_id
    """)
    # 2. 迁移旧数据：按 file_url 匹配 ly_knowledge，填充 knowledge_id
    op.execute("""
        UPDATE ly_course_attachment ca
        INNER JOIN ly_knowledge k ON k.file_url = ca.file_url AND k.deleted = 0
        SET ca.knowledge_id = k.id
        WHERE ca.deleted = 0 AND ca.knowledge_id IS NULL
    """)
    # 3. 无法匹配的旧记录：插入 ly_knowledge 后关联（保留历史数据）
    op.execute("""
        INSERT INTO ly_knowledge (title, file_name, file_url, file_size, file_type, sort, visibility)
        SELECT COALESCE(ca.name, '未命名'), ca.name, ca.file_url, NULL, ca.type, 0, 1
        FROM ly_course_attachment ca
        WHERE ca.deleted = 0 AND ca.knowledge_id IS NULL
          AND ca.file_url IS NOT NULL AND ca.file_url != ''
          AND NOT EXISTS (SELECT 1 FROM ly_knowledge k WHERE k.file_url = ca.file_url AND k.deleted = 0)
    """)
    op.execute("""
        UPDATE ly_course_attachment ca
        INNER JOIN ly_knowledge k ON k.file_url = ca.file_url AND k.deleted = 0
        SET ca.knowledge_id = k.id
        WHERE ca.deleted = 0 AND ca.knowledge_id IS NULL
    """)
    # 4. 删除无法关联的旧记录（无 file_url 或无法创建 knowledge）
    op.execute("""
        DELETE FROM ly_course_attachment WHERE deleted = 0 AND knowledge_id IS NULL
    """)
    # 5. 去重：同一课程关联同一知识只保留一条（保留 id 最小的）
    op.execute("""
        DELETE ca1 FROM ly_course_attachment ca1
        INNER JOIN ly_course_attachment ca2
          ON ca1.course_id = ca2.course_id AND ca1.knowledge_id = ca2.knowledge_id AND ca1.id > ca2.id
        WHERE ca1.deleted = 0
    """)
    # 6. 删除 name, type, file_url 列，knowledge_id 改为 NOT NULL
    op.execute("ALTER TABLE ly_course_attachment DROP COLUMN name")
    op.execute("ALTER TABLE ly_course_attachment DROP COLUMN type")
    op.execute("ALTER TABLE ly_course_attachment DROP COLUMN file_url")
    op.execute("ALTER TABLE ly_course_attachment MODIFY COLUMN knowledge_id BIGINT NOT NULL")
    # 7. 添加唯一约束，防止同一课程重复关联同一知识
    op.execute("""
        ALTER TABLE ly_course_attachment
        ADD UNIQUE KEY uk_course_knowledge (course_id, knowledge_id)
    """)
    # 8. 重命名为课程-知识库中间表
    op.execute("RENAME TABLE ly_course_attachment TO ly_course_knowledge")


def downgrade() -> None:
    conn = op.get_bind()
    # 若已是 ly_course_knowledge，先改回 ly_course_attachment
    r = conn.execute(text(
        "SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ly_course_knowledge' LIMIT 1"
    )).scalar()
    if r:
        op.execute("RENAME TABLE ly_course_knowledge TO ly_course_attachment")
    if not _column_exists(conn, "ly_course_attachment", "knowledge_id"):
        return
    op.execute("ALTER TABLE ly_course_attachment DROP INDEX uk_course_knowledge")
    op.execute("""
        ALTER TABLE ly_course_attachment
        ADD COLUMN name VARCHAR(200) NOT NULL DEFAULT '' AFTER knowledge_id,
        ADD COLUMN type VARCHAR(50) DEFAULT NULL AFTER name,
        ADD COLUMN file_url VARCHAR(500) NOT NULL DEFAULT '' AFTER type
    """)
    op.execute("""
        UPDATE ly_course_attachment ca
        INNER JOIN ly_knowledge k ON k.id = ca.knowledge_id AND k.deleted = 0
        SET ca.name = COALESCE(k.title, k.file_name, '未命名'),
            ca.type = k.file_type,
            ca.file_url = k.file_url
        WHERE ca.deleted = 0
    """)
    op.execute("ALTER TABLE ly_course_attachment DROP COLUMN knowledge_id")

# -*- coding: utf-8 -*-
"""课程-知识库中间表服务（多对多关联）"""
from typing import Any, List

import pymysql

import db

# 优先使用 ly_course_knowledge，若未迁移则回退到 ly_course_attachment（含 knowledge_id）
TABLE_KNOWLEDGE = "ly_course_knowledge"
TABLE_ATTACHMENT = "ly_course_attachment"


def _int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _to_camel(row: dict) -> dict:
    """转为前端 camelCase 格式，name/type/fileUrl 来自 ly_knowledge"""
    if not row:
        return {}
    return {
        "id": row.get("id"),
        "courseId": row.get("course_id"),
        "knowledgeId": row.get("knowledge_id"),
        "name": row.get("title") or row.get("file_name") or "未命名",
        "type": row.get("file_type"),
        "fileUrl": row.get("file_url"),
        "sort": _int(row.get("sort"), 0),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
    }


def _get_table() -> str:
    """返回实际使用的表名（ly_course_knowledge 或 ly_course_attachment）"""
    try:
        r = db.query_one(
            "SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s LIMIT 1",
            (TABLE_KNOWLEDGE,),
        )
        if r:
            return TABLE_KNOWLEDGE
    except Exception:
        pass
    return TABLE_ATTACHMENT


def list_by_course_id_camel(course_id: int) -> List[dict]:
    """按课程 ID 查询关联的知识库文件，JOIN ly_knowledge 获取文件属性"""
    table = _get_table()
    rows = db.query_all(
        f"""
        SELECT ck.id, ck.course_id, ck.knowledge_id, ck.sort, ck.create_time, ck.update_time,
               k.title, k.file_name, k.file_url, k.file_type
        FROM {table} ck
        INNER JOIN ly_knowledge k ON k.id = ck.knowledge_id AND k.deleted = 0
        WHERE ck.course_id = %s AND ck.deleted = 0
        ORDER BY ck.sort ASC, ck.id ASC
        """,
        (course_id,),
    )
    return [_to_camel(r) for r in rows] if rows else []


def save(course_id: int, knowledge_id: int, sort: int = 0) -> int:
    """添加课程-知识库关联，返回新 id。若已存在则跳过；若为软删除记录则恢复"""
    table = _get_table()
    try:
        rid = db.execute_insert(
            f"INSERT INTO {table} (course_id, knowledge_id, sort) VALUES (%s, %s, %s)",
            (course_id, knowledge_id, sort),
        )
        if rid:
            return rid
        # lastrowid 可能为 0 的边界情况，尝试查询刚插入的 id
        existing = db.query_one(
            f"SELECT id FROM {table} WHERE course_id = %s AND knowledge_id = %s AND deleted = 0 ORDER BY id DESC LIMIT 1",
            (course_id, knowledge_id),
        )
        return existing.get("id", 0) if existing else 0
    except pymysql.err.IntegrityError:
        # 唯一约束冲突：可能已存在未删除记录，或存在软删除记录
        existing = db.query_one(
            f"SELECT id, deleted FROM {table} WHERE course_id = %s AND knowledge_id = %s ORDER BY id DESC LIMIT 1",
            (course_id, knowledge_id),
        )
        if not existing:
            return 0
        rid = existing.get("id", 0)
        if existing.get("deleted") == 1:
            # 恢复软删除记录
            db.execute(
                f"UPDATE {table} SET deleted = 0, sort = %s, update_time = NOW() WHERE id = %s",
                (sort, rid),
            )
        return rid
    except Exception:
        raise


def delete(relation_id: int) -> int:
    """软删除关联（deleted=1）"""
    table = _get_table()
    return db.execute(f"UPDATE {table} SET deleted = 1 WHERE id = %s", (relation_id,))

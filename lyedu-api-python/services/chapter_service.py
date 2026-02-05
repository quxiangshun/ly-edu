# -*- coding: utf-8 -*-
"""课程章节服务"""
from typing import Any, List, Optional
import db


def _int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _row_to_chapter(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": _int(row["id"]),
        "course_id": _int(row["course_id"]),
        "title": row.get("title"),
        "sort": _int(row.get("sort"), 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }

def list_by_course_id(course_id: int) -> List[dict]:
    rows = db.query_all(
        "SELECT id, course_id, title, sort, create_time, update_time, deleted "
        "FROM ly_course_chapter WHERE course_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC",
        (course_id,))
    return [_row_to_chapter(r) for r in rows]

def get_by_id(chapter_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, course_id, title, sort, create_time, update_time, deleted "
        "FROM ly_course_chapter WHERE id = %s AND deleted = 0", (chapter_id,))
    return _row_to_chapter(row) if row else None

def save(course_id: int, title: str, sort: int = 0) -> int:
    return db.execute_insert(
        "INSERT INTO ly_course_chapter (course_id, title, sort) VALUES (%s, %s, %s)",
        (course_id, title or "", sort))

def update(chapter_id: int, title: str, sort: int = 0) -> int:
    return db.execute(
        "UPDATE ly_course_chapter SET title = %s, sort = %s WHERE id = %s AND deleted = 0",
        (title or "", sort, chapter_id))

def delete(chapter_id: int) -> int:
    return db.execute("UPDATE ly_course_chapter SET deleted = 1 WHERE id = %s", (chapter_id,))

# -*- coding: utf-8 -*-
"""课程服务，与 Java CourseService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result


def _row_to_course(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "title": row.get("title"),
        "cover": row.get("cover"),
        "description": row.get("description"),
        "category_id": row.get("category_id"),
        "status": row.get("status", 1),
        "sort": row.get("sort", 0),
        "is_required": row.get("is_required", 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def page(
    page_num: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if keyword and keyword.strip():
        where.append("(title LIKE %s OR description LIKE %s)")
        like = "%" + keyword.strip() + "%"
        params.extend([like, like])
    if category_id is not None:
        where.append("category_id = %s")
        params.append(category_id)
    where_sql = " AND ".join(where)
    total_row = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_course WHERE " + where_sql, tuple(params)
    )
    total = total_row["cnt"] or 0
    sql = (
        "SELECT id, title, cover, description, category_id, status, sort, is_required, create_time, update_time, deleted "
        "FROM ly_course WHERE " + where_sql + " ORDER BY sort ASC, id DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_course(r) for r in rows]
    return page_result(records, total, page_num, size)


def get_detail_by_id(course_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, title, cover, description, category_id, status, sort, is_required, create_time, update_time, deleted "
        "FROM ly_course WHERE id = %s AND deleted = 0",
        (course_id,),
    )
    return _row_to_course(row) if row else None


def save(
    title: Optional[str] = None,
    cover: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    status: int = 1,
    sort: int = 0,
    is_required: int = 0,
) -> int:
    db.execute(
        "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title or "", cover, description, category_id, status, sort, is_required),
    )
    return 0


def update(
    course_id: int,
    title: Optional[str] = None,
    cover: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[int] = None,
    is_required: Optional[int] = None,
) -> int:
    sql = "UPDATE ly_course SET title = %s, cover = %s, description = %s, category_id = %s, status = %s, sort = %s, is_required = %s WHERE id = %s AND deleted = 0"
    return db.execute(
        sql,
        (
            title or "",
            cover,
            description,
            category_id,
            status,
            sort,
            is_required if is_required is not None else 0,
            course_id,
        ),
    )


def delete(course_id: int) -> int:
    return db.execute("UPDATE ly_course SET deleted = 1 WHERE id = %s", (course_id,))


def list_recommended(limit: int = 6) -> List[dict]:
    rows = db.query_all(
        "SELECT id, title, cover, description, category_id, status, sort, is_required, create_time, update_time, deleted "
        "FROM ly_course WHERE deleted = 0 AND status = 1 ORDER BY sort ASC, id DESC LIMIT %s",
        (limit,),
    )
    return [_row_to_course(r) for r in rows]

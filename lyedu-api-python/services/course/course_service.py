# -*- coding: utf-8 -*-
"""课程服务，与 Java CourseService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result

SELECT_COLS = (
    "id, title, cover, description, category_id, status, sort, is_required, "
    "create_time, update_time, deleted"
)


def _int(v: Any, default: int = 0) -> int:
    """将 DB 返回的 int/Decimal/None 转为 int，避免 JSON 序列化报错。"""
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _row_to_course(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": _int(row["id"]),
        "title": row.get("title"),
        "cover": row.get("cover"),
        "description": row.get("description"),
        "category_id": row.get("category_id") if row.get("category_id") is None else _int(row["category_id"]),
        "status": _int(row.get("status"), 1),
        "sort": _int(row.get("sort"), 0),
        "is_required": _int(row.get("is_required"), 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def page(
    page_num: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    status: Optional[int] = None,
) -> dict:
    """分页查询课程。status=1 时仅返回上架课程（PC/uni 学员端用）；不传则返回全部（管理端用）。"""
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if status is not None:
        where.append("status = %s")
        params.append(status)
    if keyword and keyword.strip():
        where.append("(title LIKE %s OR description LIKE %s)")
        like = "%" + keyword.strip() + "%"
        params.extend([like, like])
    if category_id is not None:
        where.append("category_id = %s")
        params.append(category_id)
    if tag_id is not None:
        try:
            from services.learning import tag_service

            if tag_service._table_exists():
                where.append(
                    "EXISTS (SELECT 1 FROM ly_course_tag ct WHERE ct.course_id = ly_course.id AND ct.tag_id = %s)"
                )
                params.append(tag_id)
        except Exception:
            pass
    where_sql = " AND ".join(where)
    total_row = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_course WHERE " + where_sql, tuple(params)
    )
    total = total_row["cnt"] or 0
    sql = (
        f"SELECT {SELECT_COLS} FROM ly_course WHERE " + where_sql + " ORDER BY sort ASC, id DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_course(r) for r in rows]
    return page_result(records, total, page_num, size)


def get_detail_by_id(course_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    row = db.query_one(
        f"SELECT {SELECT_COLS} FROM ly_course WHERE id = %s AND deleted = 0",
        (course_id,),
    )
    return _row_to_course(row) if row else None


def get_by_id_ignore_visibility(course_id: int) -> Optional[dict]:
    """管理端用：按ID获取课程"""
    row = db.query_one(
        f"SELECT {SELECT_COLS} FROM ly_course WHERE id = %s AND deleted = 0",
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
    last_id = db.execute_insert(
        "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title or "", cover, description, category_id, status, sort, is_required),
    )
    return last_id or 0


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
    row = db.query_one(f"SELECT {SELECT_COLS} FROM ly_course WHERE id = %s AND deleted = 0", (course_id,))
    if not row:
        return 0
    sql = "UPDATE ly_course SET title = %s, cover = %s, description = %s, category_id = %s, status = %s, sort = %s, is_required = %s WHERE id = %s AND deleted = 0"
    db.execute(
        sql,
        (title or row.get("title"), cover if cover is not None else row.get("cover"), description if description is not None else row.get("description"), category_id if category_id is not None else row.get("category_id"), status if status is not None else row.get("status"), sort if sort is not None else row.get("sort"), is_required if is_required is not None else row.get("is_required", 0), course_id),
    )
    return 0


def delete(course_id: int) -> int:
    return db.execute("UPDATE ly_course SET deleted = 1 WHERE id = %s", (course_id,))


def list_recommended(limit: int = 6, user_id: Optional[int] = None) -> List[dict]:
    """推荐课程：仅返回上架课程"""
    rows = db.query_all(
        f"SELECT {SELECT_COLS} FROM ly_course WHERE deleted = 0 AND status = 1 ORDER BY sort ASC, id DESC LIMIT %s",
        (limit,),
    )
    return [_row_to_course(r) for r in rows]

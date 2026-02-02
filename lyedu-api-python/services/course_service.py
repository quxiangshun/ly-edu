# -*- coding: utf-8 -*-
"""课程服务，与 Java CourseService 对应"""
from typing import Any, List, Optional

import pymysql

import db
from models.schemas import page_result
from services import department_service
from services import user_service

SELECT_COLS_FULL = (
    "id, title, cover, description, category_id, status, sort, is_required, visibility, department_id, "
    "create_time, update_time, deleted"
)
SELECT_COLS_LEGACY = (
    "id, title, cover, description, category_id, status, sort, is_required, "
    "create_time, update_time, deleted"
)

_has_visibility_columns: Optional[bool] = None


def _course_table_has_visibility() -> bool:
    """检测 ly_course 是否已有 visibility/department_id 列（V12 迁移后为 True）"""
    global _has_visibility_columns
    if _has_visibility_columns is not None:
        return _has_visibility_columns
    try:
        db.query_one("SELECT visibility, department_id FROM ly_course LIMIT 0", ())
        _has_visibility_columns = True
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1054:  # Unknown column
            _has_visibility_columns = False
        else:
            raise
    return _has_visibility_columns


def _select_cols() -> str:
    return SELECT_COLS_FULL if _course_table_has_visibility() else SELECT_COLS_LEGACY


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
        "visibility": row.get("visibility", 1),
        "department_id": row.get("department_id"),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def _append_visibility_condition(where: List[str], params: List[Any], user_id: Optional[int]) -> None:
    if not _course_table_has_visibility():
        return  # 未执行 V12 迁移时不做可见性过滤
    if user_id is None:
        where.append("visibility = 1")
        return
    user = user_service.get_by_id(user_id)
    if not user:
        where.append("visibility = 1")
        return
    if user.get("role") == "admin":
        return  # 管理员看全部
    dept_id = user.get("department_id")
    if dept_id is None:
        where.append("visibility = 1")
        return
    allowed = department_service.get_department_id_and_descendant_ids(dept_id)
    if not allowed:
        where.append("visibility = 1")
        return
    placeholders = ", ".join(["%s"] * len(allowed))
    where.append(f"(visibility = 1 OR (visibility = 0 AND department_id IN ({placeholders})))")
    params.extend(allowed)


def _can_user_see_course(course: dict, user_id: Optional[int]) -> bool:
    if (course.get("visibility") or 1) == 1:
        return True
    if user_id is None:
        return False
    user = user_service.get_by_id(user_id)
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    dept_id = user.get("department_id")
    if dept_id is None:
        return False
    allowed = department_service.get_department_id_and_descendant_ids(dept_id)
    return course.get("department_id") is not None and course["department_id"] in allowed


def page(
    page_num: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    _append_visibility_condition(where, params, user_id)
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
        f"SELECT {_select_cols()} FROM ly_course WHERE " + where_sql + " ORDER BY sort ASC, id DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_course(r) for r in rows]
    return page_result(records, total, page_num, size)


def get_detail_by_id(course_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    row = db.query_one(
        f"SELECT {_select_cols()} FROM ly_course WHERE id = %s AND deleted = 0",
        (course_id,),
    )
    course = _row_to_course(row) if row else None
    if not course or not _can_user_see_course(course, user_id):
        return None
    return course


def get_by_id_ignore_visibility(course_id: int) -> Optional[dict]:
    """管理端用：按ID获取课程，不做可见性校验"""
    row = db.query_one(
        f"SELECT {_select_cols()} FROM ly_course WHERE id = %s AND deleted = 0",
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
    visibility: int = 1,
    department_id: Optional[int] = None,
) -> int:
    if _course_table_has_visibility():
        db.execute(
            "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required, visibility, department_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (title or "", cover, description, category_id, status, sort, is_required, visibility, department_id),
        )
    else:
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
    visibility: Optional[int] = None,
    department_id: Optional[int] = None,
) -> int:
    row = db.query_one(f"SELECT {_select_cols()} FROM ly_course WHERE id = %s AND deleted = 0", (course_id,))
    if not row:
        return 0
    if _course_table_has_visibility():
        vis = visibility if visibility is not None else row.get("visibility", 1)
        dept = department_id if department_id is not None else row.get("department_id")
        sql = "UPDATE ly_course SET title = %s, cover = %s, description = %s, category_id = %s, status = %s, sort = %s, is_required = %s, visibility = %s, department_id = %s WHERE id = %s AND deleted = 0"
        return db.execute(
            sql,
            (title or "", cover, description, category_id, status, sort, is_required if is_required is not None else 0, vis, dept, course_id),
        )
    sql = "UPDATE ly_course SET title = %s, cover = %s, description = %s, category_id = %s, status = %s, sort = %s, is_required = %s WHERE id = %s AND deleted = 0"
    return db.execute(
        sql,
        (title or "", cover, description, category_id, status, sort, is_required if is_required is not None else 0, course_id),
    )


def delete(course_id: int) -> int:
    return db.execute("UPDATE ly_course SET deleted = 1 WHERE id = %s", (course_id,))


def list_recommended(limit: int = 6, user_id: Optional[int] = None) -> List[dict]:
    where = ["deleted = 0", "status = 1"]
    params: List[Any] = []
    _append_visibility_condition(where, params, user_id)
    where_sql = " AND ".join(where)
    rows = db.query_all(
        f"SELECT {_select_cols()} FROM ly_course WHERE {where_sql} ORDER BY sort ASC, id DESC LIMIT %s",
        tuple(params) + (limit,),
    )
    return [_row_to_course(r) for r in rows]

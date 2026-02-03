# -*- coding: utf-8 -*-
"""考试任务服务，与 Java ExamService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result
from services import department_service
from services import exam_department_service
from services import user_service

SELECT_COLS = "id, title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status, create_time, update_time, deleted"


def _row_to_exam(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "title": row.get("title"),
        "paperId": row.get("paper_id"),
        "startTime": row.get("start_time"),
        "endTime": row.get("end_time"),
        "durationMinutes": row.get("duration_minutes"),
        "passScore": row.get("pass_score"),
        "visibility": row.get("visibility", 1),
        "status": row.get("status", 1),
        "departmentIds": [],
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def _append_visibility_condition(where: List[str], params: List[Any], user_id: Optional[int]) -> None:
    if user_id is None:
        where.append("visibility = 1")
        return
    user = user_service.get_by_id(user_id)
    if not user:
        where.append("visibility = 1")
        return
    if user.get("role") == "admin":
        return
    dept_id = user.get("department_id")
    if dept_id is None:
        where.append("visibility = 1")
        return
    allowed = department_service.get_department_id_and_descendant_ids(dept_id)
    if not allowed:
        where.append("visibility = 1")
        return
    placeholders = ", ".join(["%s"] * len(allowed))
    where.append(
        "(visibility = 1 OR (visibility = 0 AND EXISTS (SELECT 1 FROM ly_exam_department ed WHERE ed.exam_id = ly_exam.id AND ed.department_id IN (" + placeholders + "))))"
    )
    params.extend(allowed)


def _can_user_see(exam: dict, user_id: Optional[int]) -> bool:
    if (exam.get("visibility") or 1) == 1:
        return True
    if not user_id:
        return False
    user = user_service.get_by_id(user_id)
    if not user or user.get("role") == "admin":
        return True
    dept_id = user.get("department_id")
    if dept_id is None:
        return False
    allowed = department_service.get_department_id_and_descendant_ids(dept_id)
    return exam_department_service.exam_visible_to_departments(exam.get("id"), allowed)


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    user_id: Optional[int] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    _append_visibility_condition(where, params, user_id)
    if keyword and keyword.strip():
        where.append("title LIKE %s")
        params.append("%" + keyword.strip() + "%")
    where_sql = " AND ".join(where)
    count_sql = "SELECT COUNT(*) AS total FROM ly_exam WHERE " + where_sql
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total", 0) or 0
    query_sql = "SELECT " + SELECT_COLS + " FROM ly_exam WHERE " + where_sql + " ORDER BY id DESC LIMIT %s OFFSET %s"
    query_params = list(params) + [size, offset]
    rows = db.query_all(query_sql, tuple(query_params))
    records = []
    for r in (rows or []):
        e = _row_to_exam(r)
        e["departmentIds"] = exam_department_service.list_department_ids_by_exam_id(e.get("id"))
        records.append(e)
    return page_result(records, total, page_num, size)


def get_by_id(exam_id: int, user_id: Optional[int]) -> Optional[dict]:
    e = get_by_id_ignore_visibility(exam_id)
    if not e or not _can_user_see(e, user_id):
        return None
    return e


def get_by_id_ignore_visibility(exam_id: int) -> Optional[dict]:
    sql = "SELECT " + SELECT_COLS + " FROM ly_exam WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (exam_id,))
    if not row:
        return None
    e = _row_to_exam(row)
    e["departmentIds"] = exam_department_service.list_department_ids_by_exam_id(e.get("id"))
    return e


def save(
    title: str,
    paper_id: int,
    start_time: Optional[Any] = None,
    end_time: Optional[Any] = None,
    duration_minutes: Optional[int] = None,
    pass_score: Optional[int] = None,
    visibility: int = 1,
    status: int = 1,
    department_ids: Optional[List[int]] = None,
) -> int:
    sql = (
        "INSERT INTO ly_exam (title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    eid = db.execute_insert(
        sql,
        (title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status),
    )
    if eid and department_ids:
        exam_department_service.set_exam_departments(eid, department_ids)
    return eid or 0


def update(
    exam_id: int,
    title: str,
    paper_id: int,
    start_time: Optional[Any] = None,
    end_time: Optional[Any] = None,
    duration_minutes: Optional[int] = None,
    pass_score: Optional[int] = None,
    visibility: int = 1,
    status: int = 1,
    department_ids: Optional[List[int]] = None,
) -> bool:
    sql = (
        "UPDATE ly_exam SET title = %s, paper_id = %s, start_time = %s, end_time = %s, duration_minutes = %s, pass_score = %s, visibility = %s, status = %s "
        "WHERE id = %s AND deleted = 0"
    )
    n = db.execute(
        sql,
        (title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status, exam_id),
    )
    exam_department_service.set_exam_departments(exam_id, department_ids or [])
    return n > 0


def delete(exam_id: int) -> bool:
    n = db.execute("UPDATE ly_exam SET deleted = 1 WHERE id = %s", (exam_id,))
    exam_department_service.set_exam_departments(exam_id, None)
    return n > 0

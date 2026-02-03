# -*- coding: utf-8 -*-
"""周期任务服务，与 Java TaskService 对应"""
import json
from datetime import date, datetime
from typing import Any, List, Optional

import db
from models.schemas import page_result
from services import department_service
from services import task_department_service
from services import user_service

SELECT_COLS = "id, title, description, cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time, create_time, update_time, deleted"


def _row_to_task(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "title": row.get("title"),
        "description": row.get("description"),
        "cycleType": row.get("cycle_type") or "once",
        "cycleConfig": row.get("cycle_config"),
        "items": row.get("items") or "[]",
        "certificateId": row.get("certificate_id"),
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
        "startTime": row.get("start_time"),
        "endTime": row.get("end_time"),
        "departmentIds": [],
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def _append_newcomer_condition(where: List[str], params: List[Any], user_id: Optional[int]) -> None:
    if user_id is None:
        where.append(" AND (ly_task.cycle_type IS NULL OR ly_task.cycle_type <> 'newcomer')")
        return
    where.append(
        " AND (ly_task.cycle_type IS NULL OR ly_task.cycle_type <> 'newcomer' OR "
        "(SELECT DATEDIFF(CURDATE(), COALESCE(u.entry_date, u.create_time)) FROM ly_user u WHERE u.id = %s AND u.deleted = 0) <= "
        "CAST(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(ly_task.cycle_config, '$.within_days')), '9999') AS UNSIGNED))"
    )
    params.append(user_id)


def _append_visibility_condition(where: List[str], params: List[Any], user_id: Optional[int]) -> None:
    if user_id is None:
        where.append("(NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))")
        _append_newcomer_condition(where, params, None)
        return
    user = user_service.get_by_id(user_id)
    if not user:
        where.append("(NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))")
        _append_newcomer_condition(where, params, None)
        return
    if user.get("role") == "admin":
        return
    dept_id = user.get("department_id")
    if dept_id is None:
        where.append("(NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))")
        _append_newcomer_condition(where, params, user_id)
        return
    allowed = department_service.get_department_id_and_descendant_ids(dept_id)
    if not allowed:
        where.append("(NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))")
        _append_newcomer_condition(where, params, user_id)
        return
    placeholders = ", ".join(["%s"] * len(allowed))
    where.append(
        "(NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id) "
        "OR EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id AND td.department_id IN (" + placeholders + ")))"
    )
    params.extend(allowed)
    _append_newcomer_condition(where, params, user_id)


def _parse_within_days(cycle_config: Optional[str]) -> int:
    if not cycle_config or not cycle_config.strip():
        return 9999
    try:
        obj = json.loads(cycle_config)
        return int(obj.get("within_days", 9999))
    except Exception:
        return 9999


def _days_since_entry(user: dict) -> int:
    entry = user.get("entry_date") or user.get("entryDate")
    if entry:
        if isinstance(entry, date):
            return (date.today() - entry).days
        if isinstance(entry, datetime):
            return (date.today() - entry.date()).days
        if isinstance(entry, str):
            try:
                d = datetime.fromisoformat(entry.replace("Z", "+00:00")).date() if "T" in entry else datetime.strptime(entry[:10], "%Y-%m-%d").date()
                return (date.today() - d).days
            except Exception:
                pass
    create_time = user.get("create_time") or user.get("createTime")
    if create_time:
        if hasattr(create_time, "date"):
            return (date.today() - create_time.date()).days
        if isinstance(create_time, str):
            try:
                d = datetime.fromisoformat(create_time.replace("Z", "+00:00")).date() if "T" in create_time else datetime.strptime(create_time[:10], "%Y-%m-%d").date()
                return (date.today() - d).days
            except Exception:
                pass
    return 0


def _can_user_see(task: dict, user_id: Optional[int]) -> bool:
    if task.get("cycle_type") == "newcomer":
        if not user_id:
            return False
        user = user_service.get_by_id(user_id)
        if not user or user.get("role") == "admin":
            return True
        within_days = _parse_within_days(task.get("cycle_config"))
        if _days_since_entry(user) > within_days:
            return False
    dept_ids = task_department_service.list_department_ids_by_task_id(task.get("id"))
    if not dept_ids:
        return True
    if not user_id:
        return False
    user = user_service.get_by_id(user_id)
    if not user or user.get("role") == "admin":
        return True
    if user.get("department_id") is None:
        return False
    allowed = department_service.get_department_id_and_descendant_ids(user["department_id"])
    return task_department_service.task_visible_to_departments(task.get("id"), allowed)


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    user_id: Optional[int] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["ly_task.deleted = 0"]
    params: List[Any] = []
    _append_visibility_condition(where, params, user_id)
    if keyword and keyword.strip():
        where.append("ly_task.title LIKE %s")
        params.append("%" + keyword.strip() + "%")
    where_sql = " AND ".join(where)
    count_sql = "SELECT COUNT(*) AS total FROM ly_task WHERE " + where_sql
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total", 0) or 0
    query_sql = (
        "SELECT ly_task.id, ly_task.title, ly_task.description, ly_task.cycle_type, ly_task.cycle_config, "
        "ly_task.items, ly_task.certificate_id, ly_task.sort, ly_task.status, ly_task.start_time, ly_task.end_time, "
        "ly_task.create_time, ly_task.update_time, ly_task.deleted FROM ly_task WHERE " + where_sql
        + " ORDER BY ly_task.sort ASC, ly_task.id DESC LIMIT %s OFFSET %s"
    )
    query_params = list(params) + [size, offset]
    rows = db.query_all(query_sql, tuple(query_params))
    records = []
    for r in (rows or []):
        t = _row_to_task(r)
        t["departmentIds"] = task_department_service.list_department_ids_by_task_id(t.get("id"))
        records.append(t)
    return page_result(records, total, page_num, size)


def get_by_id(task_id: int, user_id: Optional[int]) -> Optional[dict]:
    t = get_by_id_ignore_visibility(task_id)
    if not t or not _can_user_see(t, user_id):
        return None
    return t


def get_by_id_ignore_visibility(task_id: int) -> Optional[dict]:
    sql = "SELECT " + SELECT_COLS + " FROM ly_task WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (task_id,))
    if not row:
        return None
    t = _row_to_task(row)
    t["departmentIds"] = task_department_service.list_department_ids_by_task_id(t.get("id"))
    return t


def save(
    title: str,
    description: Optional[str] = None,
    cycle_type: str = "once",
    cycle_config: Optional[str] = None,
    items: str = "[]",
    certificate_id: Optional[int] = None,
    sort: int = 0,
    status: int = 1,
    start_time: Optional[Any] = None,
    end_time: Optional[Any] = None,
    department_ids: Optional[List[int]] = None,
) -> int:
    sql = (
        "INSERT INTO ly_task (title, description, cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    tid = db.execute_insert(
        sql,
        (title, description or "", cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time),
    )
    if tid and department_ids:
        task_department_service.set_task_departments(tid, department_ids)
    return tid or 0


def update(
    task_id: int,
    title: str,
    description: Optional[str] = None,
    cycle_type: str = "once",
    cycle_config: Optional[str] = None,
    items: str = "[]",
    certificate_id: Optional[int] = None,
    sort: int = 0,
    status: int = 1,
    start_time: Optional[Any] = None,
    end_time: Optional[Any] = None,
    department_ids: Optional[List[int]] = None,
) -> bool:
    sql = (
        "UPDATE ly_task SET title = %s, description = %s, cycle_type = %s, cycle_config = %s, items = %s, "
        "certificate_id = %s, sort = %s, status = %s, start_time = %s, end_time = %s WHERE id = %s AND deleted = 0"
    )
    n = db.execute(
        sql,
        (title, description or "", cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time, task_id),
    )
    task_department_service.set_task_departments(task_id, department_ids or [])
    return n > 0


def delete(task_id: int) -> bool:
    n = db.execute("UPDATE ly_task SET deleted = 1 WHERE id = %s", (task_id,))
    task_department_service.set_task_departments(task_id, None)
    return n > 0

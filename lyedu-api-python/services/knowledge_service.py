# -*- coding: utf-8 -*-
"""知识库服务，与 Java KnowledgeService 对应"""
from typing import Any, List, Optional

import pymysql

import db
from models.schemas import page_result
from services import department_service
from services import knowledge_department_service
from services import user_service

SELECT_COLS = "id, title, category, file_name, file_url, file_size, file_type, sort, visibility, create_time, update_time, deleted"


def _row_to_knowledge(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "title": row.get("title"),
        "category": row.get("category"),
        "fileName": row.get("file_name"),
        "fileUrl": row.get("file_url"),
        "fileSize": row.get("file_size"),
        "fileType": row.get("file_type"),
        "sort": row.get("sort", 0),
        "visibility": row.get("visibility", 1),
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
        "(visibility = 1 OR (visibility = 0 AND EXISTS (SELECT 1 FROM ly_knowledge_department kd WHERE kd.knowledge_id = ly_knowledge.id AND kd.department_id IN (" + placeholders + "))))"
    )
    params.extend(allowed)


def _can_user_see(knowledge: dict, user_id: Optional[int]) -> bool:
    if (knowledge.get("visibility") or 1) == 1:
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
    return knowledge_department_service.knowledge_visible_to_departments(knowledge.get("id"), allowed)


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
) -> dict:
    try:
        offset = (page_num - 1) * size
        where = ["deleted = 0"]
        params: List[Any] = []
        _append_visibility_condition(where, params, user_id)
        if keyword and keyword.strip():
            where.append("(title LIKE %s OR category LIKE %s)")
            like = "%" + keyword.strip() + "%"
            params.append(like)
            params.append(like)
        if category and category.strip():
            where.append("category = %s")
            params.append(category.strip())
        where_sql = " AND ".join(where)
        count_sql = "SELECT COUNT(*) AS total FROM ly_knowledge WHERE " + where_sql
        total_row = db.query_one(count_sql, tuple(params))
        total = total_row.get("total", 0) or 0
        query_sql = (
            "SELECT " + SELECT_COLS + " FROM ly_knowledge WHERE " + where_sql + " ORDER BY sort ASC, id DESC LIMIT %s OFFSET %s"
        )
        query_params = list(params) + [size, offset]
        rows = db.query_all(query_sql, tuple(query_params))
        records = []
        for r in rows or []:
            k = _row_to_knowledge(r)
            k["departmentIds"] = knowledge_department_service.list_department_ids_by_knowledge_id(k.get("id"))
            records.append(k)
        return page_result(records, total, page_num, size)
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:  # Table doesn't exist
            return page_result([], 0, page_num, size)
        raise


def get_by_id(knowledge_id: int, user_id: Optional[int]) -> Optional[dict]:
    k = get_by_id_ignore_visibility(knowledge_id)
    if not k or not _can_user_see(k, user_id):
        return None
    return k


def get_by_id_ignore_visibility(knowledge_id: int) -> Optional[dict]:
    try:
        sql = "SELECT " + SELECT_COLS + " FROM ly_knowledge WHERE id = %s AND deleted = 0"
        row = db.query_one(sql, (knowledge_id,))
        if not row:
            return None
        k = _row_to_knowledge(row)
        k["departmentIds"] = knowledge_department_service.list_department_ids_by_knowledge_id(k.get("id"))
        return k
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return None
        raise


def save(
    title: str,
    file_url: str,
    category: Optional[str] = None,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    file_type: Optional[str] = None,
    sort: int = 0,
    visibility: int = 1,
    department_ids: Optional[List[int]] = None,
) -> int:
    try:
        sql = (
            "INSERT INTO ly_knowledge (title, category, file_name, file_url, file_size, file_type, sort, visibility) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        kid = db.execute_insert(
            sql,
            (title, category, file_name, file_url, file_size, file_type, sort, visibility),
        )
        if kid and department_ids:
            knowledge_department_service.set_knowledge_departments(kid, department_ids)
        return kid or 0
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return 0
        raise


def update(
    knowledge_id: int,
    title: str,
    file_url: str,
    category: Optional[str] = None,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    file_type: Optional[str] = None,
    sort: int = 0,
    visibility: int = 1,
    department_ids: Optional[List[int]] = None,
) -> bool:
    sql = (
        "UPDATE ly_knowledge SET title = %s, category = %s, file_name = %s, file_url = %s, file_size = %s, file_type = %s, sort = %s, visibility = %s "
        "WHERE id = %s AND deleted = 0"
    )
    n = db.execute(
        sql,
        (title, category, file_name, file_url, file_size, file_type, sort, visibility, knowledge_id),
    )
    knowledge_department_service.set_knowledge_departments(knowledge_id, department_ids or [])
    return n > 0


def delete(knowledge_id: int) -> bool:
    try:
        n = db.execute("UPDATE ly_knowledge SET deleted = 1 WHERE id = %s", (knowledge_id,))
        knowledge_department_service.set_knowledge_departments(knowledge_id, None)
        return n > 0
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return False
        raise

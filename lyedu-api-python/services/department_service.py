# -*- coding: utf-8 -*-
"""部门服务，与 Java DepartmentService 对应"""
from typing import List, Optional

import db


def _row_to_dept(row: dict) -> dict:
    """转为前端需要的 camelCase：id, name, parentId, sort, status"""
    if not row:
        return {}
    return {
        "id": row["id"],
        "name": row.get("name"),
        "parentId": row.get("parent_id") if row.get("parent_id") is not None else 0,
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
    }


def list_all() -> List[dict]:
    """查询所有部门（未删除），按 sort、id 排序"""
    rows = db.query_all(
        "SELECT id, name, parent_id, sort, status, create_time, update_time, deleted "
        "FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
    )
    return [_row_to_dept(r) for r in rows]


def list_tree() -> List[dict]:
    """部门树/列表：返回全部部门（扁平），便于前端表格展示；与 Java 语义兼容"""
    return list_all()


def get_by_id(dept_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, name, parent_id, sort, status, create_time, update_time, deleted "
        "FROM ly_department WHERE id = %s AND deleted = 0",
        (dept_id,),
    )
    return _row_to_dept(row) if row else None


def save(
    name: str,
    parent_id: Optional[int] = None,
    sort: int = 0,
    status: int = 1,
) -> None:
    pid = parent_id if parent_id is not None else 0
    db.execute(
        "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)",
        (name or "", pid, sort, status),
    )


def update(
    dept_id: int,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    sort: Optional[int] = None,
    status: Optional[int] = None,
) -> int:
    row = db.query_one(
        "SELECT id, name, parent_id, sort, status FROM ly_department WHERE id = %s AND deleted = 0",
        (dept_id,),
    )
    if not row:
        return 0
    name = name if name is not None else row["name"]
    pid = parent_id if parent_id is not None else row["parent_id"]
    if pid is None:
        pid = 0
    sort_val = sort if sort is not None else row["sort"]
    status_val = status if status is not None else row["status"]
    return db.execute(
        "UPDATE ly_department SET name = %s, parent_id = %s, sort = %s, status = %s WHERE id = %s AND deleted = 0",
        (name, pid, sort_val, status_val, dept_id),
    )


def delete(dept_id: int) -> int:
    return db.execute("UPDATE ly_department SET deleted = 1 WHERE id = %s", (dept_id,))

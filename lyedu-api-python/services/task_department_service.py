# -*- coding: utf-8 -*-
"""任务-部门多对多关联服务，与 Java TaskDepartmentService 对应"""
from typing import List, Optional

import db

TABLE = "ly_task_department"


def list_department_ids_by_task_id(task_id: Optional[int]) -> List[int]:
    if not task_id:
        return []
    rows = db.query_all("SELECT department_id FROM " + TABLE + " WHERE task_id = %s", (task_id,))
    return [r["department_id"] for r in (rows or []) if r.get("department_id") is not None]


def set_task_departments(task_id: Optional[int], department_ids: Optional[List[int]]) -> None:
    if not task_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE task_id = %s", (task_id,))
    if department_ids:
        for dept_id in department_ids:
            if dept_id is not None:
                db.execute(
                    "INSERT INTO " + TABLE + " (task_id, department_id) VALUES (%s, %s)",
                    (task_id, dept_id),
                )


def task_visible_to_departments(task_id: Optional[int], allowed_dept_ids: Optional[List[int]]) -> bool:
    if not task_id or not allowed_dept_ids:
        return False
    placeholders = ", ".join(["%s"] * len(allowed_dept_ids))
    sql = "SELECT 1 FROM " + TABLE + " WHERE task_id = %s AND department_id IN (" + placeholders + ") LIMIT 1"
    row = db.query_one(sql, (task_id, *allowed_dept_ids))
    return row is not None

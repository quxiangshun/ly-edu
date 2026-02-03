# -*- coding: utf-8 -*-
"""考试-部门多对多关联服务，与 Java ExamDepartmentService 对应"""
from typing import List, Optional

import db

TABLE = "ly_exam_department"


def list_department_ids_by_exam_id(exam_id: Optional[int]) -> List[int]:
    if not exam_id:
        return []
    rows = db.query_all("SELECT department_id FROM " + TABLE + " WHERE exam_id = %s", (exam_id,))
    return [r["department_id"] for r in (rows or []) if r.get("department_id") is not None]


def set_exam_departments(exam_id: Optional[int], department_ids: Optional[List[int]]) -> None:
    if not exam_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE exam_id = %s", (exam_id,))
    if department_ids:
        for dept_id in department_ids:
            if dept_id is not None:
                db.execute(
                    "INSERT INTO " + TABLE + " (exam_id, department_id) VALUES (%s, %s)",
                    (exam_id, dept_id),
                )


def exam_visible_to_departments(exam_id: Optional[int], allowed_dept_ids: Optional[List[int]]) -> bool:
    if not exam_id or not allowed_dept_ids:
        return False
    placeholders = ", ".join(["%s"] * len(allowed_dept_ids))
    sql = "SELECT 1 FROM " + TABLE + " WHERE exam_id = %s AND department_id IN (" + placeholders + ") LIMIT 1"
    row = db.query_one(sql, (exam_id, *allowed_dept_ids))
    return row is not None

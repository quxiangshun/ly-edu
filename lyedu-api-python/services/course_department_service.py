# -*- coding: utf-8 -*-
"""课程-部门多对多关联服务，与 Java CourseDepartmentService 对应"""
from typing import List, Optional

import db

TABLE = "ly_course_department"


def list_department_ids_by_course_id(course_id: Optional[int]) -> List[int]:
    if not course_id:
        return []
    rows = db.query_all("SELECT department_id FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    return [r["department_id"] for r in (rows or []) if r.get("department_id") is not None]


def set_course_departments(course_id: Optional[int], department_ids: Optional[List[int]]) -> None:
    if not course_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    if department_ids:
        for dept_id in department_ids:
            if dept_id is not None:
                db.execute("INSERT INTO " + TABLE + " (course_id, department_id) VALUES (%s, %s)", (course_id, dept_id))


def list_course_ids_by_department_id(department_id: Optional[int]) -> List[int]:
    if not department_id:
        return []
    rows = db.query_all("SELECT course_id FROM " + TABLE + " WHERE department_id = %s", (department_id,))
    return [r["course_id"] for r in (rows or []) if r.get("course_id") is not None]


def add_courses_to_department(department_id: Optional[int], course_ids: Optional[List[int]]) -> None:
    if not department_id or not course_ids:
        return
    for course_id in course_ids:
        if course_id is not None:
            db.execute(
                "INSERT IGNORE INTO " + TABLE + " (course_id, department_id) VALUES (%s, %s)",
                (course_id, department_id),
            )


def remove_course_from_department(department_id: Optional[int], course_id: Optional[int]) -> None:
    if not department_id or not course_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE department_id = %s AND course_id = %s", (department_id, course_id))


def course_visible_to_departments(course_id: Optional[int], allowed_dept_ids: Optional[List[int]]) -> bool:
    if not course_id or not allowed_dept_ids:
        return False
    placeholders = ", ".join(["%s"] * len(allowed_dept_ids))
    sql = "SELECT 1 FROM " + TABLE + " WHERE course_id = %s AND department_id IN (" + placeholders + ") LIMIT 1"
    row = db.query_one(sql, (course_id, *allowed_dept_ids))
    return row is not None


def table_exists() -> bool:
    """检测 ly_course_department 表是否存在（V13 迁移后为 True）"""
    try:
        db.query_one("SELECT 1 FROM " + TABLE + " LIMIT 0", ())
        return True
    except Exception:
        return False

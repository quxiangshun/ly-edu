# -*- coding: utf-8 -*-
"""知识库-部门多对多关联服务，与 Java KnowledgeDepartmentService 对应"""
from typing import List, Optional

import pymysql

import db

TABLE = "ly_knowledge_department"


def list_department_ids_by_knowledge_id(knowledge_id: Optional[int]) -> List[int]:
    if not knowledge_id:
        return []
    try:
        rows = db.query_all("SELECT department_id FROM " + TABLE + " WHERE knowledge_id = %s", (knowledge_id,))
        return [r["department_id"] for r in (rows or []) if r.get("department_id") is not None]
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return []
        raise


def set_knowledge_departments(knowledge_id: Optional[int], department_ids: Optional[List[int]]) -> None:
    if not knowledge_id:
        return
    try:
        db.execute("DELETE FROM " + TABLE + " WHERE knowledge_id = %s", (knowledge_id,))
        if department_ids:
            for dept_id in department_ids:
                if dept_id is not None:
                    db.execute(
                        "INSERT INTO " + TABLE + " (knowledge_id, department_id) VALUES (%s, %s)",
                        (knowledge_id, dept_id),
                    )
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1146:
            return
        raise


def knowledge_visible_to_departments(knowledge_id: Optional[int], allowed_dept_ids: Optional[List[int]]) -> bool:
    if not knowledge_id or not allowed_dept_ids:
        return False
    try:
        placeholders = ", ".join(["%s"] * len(allowed_dept_ids))
        sql = "SELECT 1 FROM " + TABLE + " WHERE knowledge_id = %s AND department_id IN (" + placeholders + ") LIMIT 1"
        row = db.query_one(sql, (knowledge_id, *allowed_dept_ids))
        return row is not None
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return False
        raise

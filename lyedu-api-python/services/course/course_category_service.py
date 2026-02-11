# -*- coding: utf-8 -*-
"""课程分类服务，供学员端课程中心分类下拉等使用"""
from typing import Any, List

import pymysql

import db


def _int(v: Any, default: int = 0) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def list_all() -> List[dict]:
    """返回所有启用的课程分类（id, name），按 sort、id 排序，供学员端下拉选择"""
    try:
        rows = db.query_all(
            "SELECT id, name, parent_id, sort FROM ly_course_category WHERE status = 1 AND deleted = 0 ORDER BY sort ASC, id ASC"
        )
        return [
            {
                "id": _int(r["id"]),
                "name": r.get("name") or "",
                "parentId": _int(r.get("parent_id"), 0),
                "sort": _int(r.get("sort"), 0),
            }
            for r in (rows or [])
        ]
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:  # Table doesn't exist
            return []
        raise

# -*- coding: utf-8 -*-
"""课程附件服务，与 Java CourseAttachmentService 对应"""
from typing import List

import db


def _row_to_attachment(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "course_id": row["course_id"],
        "name": row.get("name"),
        "type": row.get("type"),
        "file_url": row.get("file_url"),
        "sort": row.get("sort", 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def list_by_course_id(course_id: int) -> List[dict]:
    rows = db.query_all(
        "SELECT id, course_id, name, type, file_url, sort, create_time, update_time, deleted "
        "FROM ly_course_attachment WHERE course_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC",
        (course_id,),
    )
    return [_row_to_attachment(r) for r in rows]

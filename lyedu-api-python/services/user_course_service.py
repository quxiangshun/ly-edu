# -*- coding: utf-8 -*-
"""用户课程服务，与 Java UserCourseService 对应"""
from typing import List, Optional

import db


def _row_to_user_course(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "progress": row.get("progress", 0),
        "status": row.get("status", 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
    }


def join_course(user_id: int, course_id: int) -> None:
    cnt = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_user_course WHERE user_id = %s AND course_id = %s",
        (user_id, course_id),
    )
    if (cnt.get("cnt") or 0) == 0:
        db.execute(
            "INSERT INTO ly_user_course (user_id, course_id, progress, status) VALUES (%s, %s, 0, 0)",
            (user_id, course_id),
        )


def list_by_user_id(user_id: int) -> List[dict]:
    rows = db.query_all(
        "SELECT id, user_id, course_id, progress, status, create_time, update_time "
        "FROM ly_user_course WHERE user_id = %s ORDER BY update_time DESC",
        (user_id,),
    )
    return [_row_to_user_course(r) for r in rows]


def get_by_user_and_course(user_id: int, course_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, user_id, course_id, progress, status, create_time, update_time "
        "FROM ly_user_course WHERE user_id = %s AND course_id = %s",
        (user_id, course_id),
    )
    return _row_to_user_course(row) if row else None


def update_progress(user_id: int, course_id: int, progress: int) -> int:
    status = 1 if progress >= 100 else 0
    return db.execute(
        "UPDATE ly_user_course SET progress = %s, status = %s WHERE user_id = %s AND course_id = %s",
        (progress, status, user_id, course_id),
    )

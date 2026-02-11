# -*- coding: utf-8 -*-
"""课程-考试关联：一门课关联一场考试；一场考试可关联多门课"""
from typing import Optional, List

import db

TABLE = "ly_course_exam"


def table_exists() -> bool:
    try:
        db.query_one("SELECT 1 FROM " + TABLE + " LIMIT 0", ())
        return True
    except Exception:
        return False


def get_exam_id_by_course(course_id: Optional[int]) -> Optional[int]:
    if not course_id:
        return None
    row = db.query_one("SELECT exam_id FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    return row.get("exam_id") if row else None


def get_course_ids_by_exam(exam_id: Optional[int]) -> List[int]:
    if not exam_id:
        return []
    rows = db.query_all("SELECT course_id FROM " + TABLE + " WHERE exam_id = %s", (exam_id,))
    return [r["course_id"] for r in (rows or []) if r.get("course_id") is not None]


def set_course_exam(course_id: Optional[int], exam_id: Optional[int]) -> None:
    if not course_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    if exam_id:
        db.execute("INSERT INTO " + TABLE + " (course_id, exam_id) VALUES (%s, %s)", (course_id, exam_id))
# -*- coding: utf-8 -*-
"""课程-考试关联：一门课关联一场考试；一场考试可关联多门课"""
from typing import Optional, List

import db

TABLE = "ly_course_exam"


def table_exists() -> bool:
    try:
        db.query_one("SELECT 1 FROM " + TABLE + " LIMIT 0", ())
        return True
    except Exception:
        return False


def get_exam_id_by_course(course_id: Optional[int]) -> Optional[int]:
    if not course_id:
        return None
    row = db.query_one("SELECT exam_id FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    return row.get("exam_id") if row else None


def get_course_ids_by_exam(exam_id: Optional[int]) -> List[int]:
    if not exam_id:
        return []
    rows = db.query_all("SELECT course_id FROM " + TABLE + " WHERE exam_id = %s", (exam_id,))
    return [r["course_id"] for r in (rows or []) if r.get("course_id") is not None]


def set_course_exam(course_id: Optional[int], exam_id: Optional[int]) -> None:
    if not course_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE course_id = %s", (course_id,))
    if exam_id:
        db.execute("INSERT INTO " + TABLE + " (course_id, exam_id) VALUES (%s, %s)", (course_id, exam_id))

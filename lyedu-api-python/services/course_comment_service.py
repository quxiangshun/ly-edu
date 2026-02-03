# -*- coding: utf-8 -*-
"""课程评论服务，与 Java CourseCommentService 对应"""
from typing import Any, List, Optional

import db


def list_by_course(course_id: int, chapter_id: Optional[int] = None) -> List[dict]:
    if chapter_id is not None:
        rows = db.query_all(
            "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.create_time, "
            "u.real_name AS user_real_name FROM ly_course_comment c "
            "LEFT JOIN ly_user u ON c.user_id = u.id AND u.deleted = 0 "
            "WHERE c.course_id = %s AND c.deleted = 0 AND (c.status IS NULL OR c.status = 1) "
            "AND (c.chapter_id IS NULL OR c.chapter_id = %s) ORDER BY c.id ASC",
            (course_id, chapter_id),
        )
    else:
        rows = db.query_all(
            "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.create_time, "
            "u.real_name AS user_real_name FROM ly_course_comment c "
            "LEFT JOIN ly_user u ON c.user_id = u.id AND u.deleted = 0 "
            "WHERE c.course_id = %s AND c.deleted = 0 AND (c.status IS NULL OR c.status = 1) "
            "ORDER BY c.id ASC",
            (course_id,),
        )
    return [_row_to_dto(r) for r in rows]


def _row_to_dto(r: dict) -> dict:
    out = {
        "id": r["id"],
        "courseId": r["course_id"],
        "chapterId": r.get("chapter_id"),
        "userId": r["user_id"],
        "userRealName": r.get("user_real_name"),
        "parentId": r.get("parent_id"),
        "content": r.get("content") or "",
        "status": r.get("status") or 1,
        "createTime": r.get("create_time"),
    }
    if hasattr(out["createTime"], "isoformat"):
        out["createTime"] = out["createTime"].isoformat()
    return out


def add(
    course_id: int,
    user_id: int,
    content: str,
    chapter_id: Optional[int] = None,
    parent_id: Optional[int] = None,
) -> Optional[dict]:
    content = (content or "").strip()
    if not content:
        return None
    db.execute(
        "INSERT INTO ly_course_comment (course_id, chapter_id, user_id, parent_id, content, status) "
        "VALUES (%s, %s, %s, %s, %s, 1)",
        (course_id, chapter_id, user_id, parent_id, content),
    )
    row = db.query_one(
        "SELECT id, course_id, chapter_id, user_id, parent_id, content, status, create_time "
        "FROM ly_course_comment WHERE course_id = %s AND user_id = %s ORDER BY id DESC LIMIT 1",
        (course_id, user_id),
    )
    if not row:
        return None
    return {
        "id": row["id"],
        "courseId": row["course_id"],
        "chapterId": row.get("chapter_id"),
        "userId": row["user_id"],
        "parentId": row.get("parent_id"),
        "content": row["content"],
        "status": row.get("status") or 1,
        "createTime": row.get("create_time").isoformat() if row.get("create_time") else None,
    }


def delete(comment_id: int) -> int:
    return db.execute("UPDATE ly_course_comment SET deleted = 1 WHERE id = %s", (comment_id,))
